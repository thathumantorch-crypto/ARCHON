"""
ARCHON Neural Network — conversational backbone powered by DialoGPT.

DialoGPT is a GPT-2 model fine-tuned on 147M Reddit conversation threads,
so it actually understands dialogue turns and produces relevant replies
(unlike raw GPT-2 / DistilGPT2 which are text-completion models).
"""

import logging
import random
from typing import Dict, List, Optional, Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class ConversationalNeuralNetwork:
    """Conversational AI engine backed by DialoGPT."""

    # Models to try in order of preference
    _MODEL_CHAIN = [
        "microsoft/DialoGPT-medium",
        "microsoft/DialoGPT-small",
    ]

    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        self.logger = logging.getLogger("ARCHON.NEURAL_NETWORK")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Conversation history stored as token IDs so DialoGPT can
        # condition on previous turns (like a real chat).
        self._history_ids: Optional[torch.Tensor] = None
        self._max_history_turns = 5

        # Try loading models in order
        self.model = None
        self.tokenizer = None
        self.model_name = model_name

        models_to_try = [model_name] if model_name not in self._MODEL_CHAIN else []
        models_to_try.extend(self._MODEL_CHAIN)

        for name in models_to_try:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(name)
                self.model = AutoModelForCausalLM.from_pretrained(name)
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                self.model.eval()
                self.model.to(self.device)
                self.model_name = name
                self.hidden_size = self.model.config.n_embd
                self.logger.info(f"Loaded {name} ({sum(p.numel() for p in self.model.parameters()):,} params)")
                break
            except Exception as exc:
                self.logger.warning(f"Could not load {name}: {exc}")

        if self.model is None:
            raise RuntimeError("Failed to load any conversational model")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_response(
        self,
        prompt: str,
        max_new_tokens: int = 100,
        temperature: float = 0.75,
        top_p: float = 0.92,
        top_k: int = 50,
        computer_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a conversational reply to *prompt*.

        Uses DialoGPT's native multi-turn format: each user turn is
        appended to the running history so the model can see context.
        """
        try:
            # Encode the new user utterance + EOS separator
            new_input_ids = self.tokenizer.encode(
                prompt + self.tokenizer.eos_token, return_tensors="pt"
            ).to(self.device)

            # Append to conversation history (or start fresh)
            if self._history_ids is not None:
                bot_input_ids = torch.cat([self._history_ids, new_input_ids], dim=-1)
            else:
                bot_input_ids = new_input_ids

            # Truncate if history is too long (keep last 512 tokens)
            if bot_input_ids.shape[-1] > 512:
                bot_input_ids = bot_input_ids[:, -512:]

            # Build explicit attention mask to suppress the warning
            attention_mask = torch.ones_like(bot_input_ids)

            # Generate
            with torch.no_grad():
                output_ids = self.model.generate(
                    bot_input_ids,
                    attention_mask=attention_mask,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.2,
                    no_repeat_ngram_size=3,
                )

            # Extract only the newly generated tokens
            reply_ids = output_ids[:, bot_input_ids.shape[-1]:]
            response_text = self.tokenizer.decode(
                reply_ids[0], skip_special_tokens=True
            ).strip()

            # Update conversation history (keep last N turns)
            self._history_ids = output_ids
            self._trim_history()

            # Filter out Reddit-isms that DialoGPT sometimes produces
            response_text = self._clean_response(response_text)

            if not response_text or len(response_text) < 2:
                return self._fallback(prompt)

            return {
                "response": response_text,
                "confidence": 0.85,
                "model": self.model_name,
                "fallback": False,
            }

        except Exception as exc:
            self.logger.error(f"Generation error: {exc}")
            return self._fallback(prompt)

    def reset_history(self):
        """Clear conversation history (start a new session)."""
        self._history_ids = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _trim_history(self):
        """Keep history from growing unbounded."""
        if self._history_ids is not None and self._history_ids.shape[-1] > 400:
            self._history_ids = self._history_ids[:, -400:]

    @staticmethod
    def _clean_response(text: str) -> str:
        """Filter out responses where DialoGPT breaks character."""
        if not text:
            return ""
        lower = text.lower().strip()

        # Reddit culture leaks
        bad_phrases = [
            'upvote', 'downvote', 'subreddit', '/r/', 'reddit',
            'karma', 'repost', 'OP ', 'TIL ', 'ELI5',
            'username', 'gilded', 'wholesome award',
            'lol', 'lmao', 'rofl', 'bruh', 'ngl',
            # Human persona leaks
            'my husband', 'my wife', 'my kids', 'my children',
            'my boyfriend', 'my girlfriend', 'my mom', 'my dad',
            'my office', 'my job', 'i work at', 'i live in',
            'my school', 'my teacher', 'my boss', 'my coworker',
            'i went to', 'i was at', 'i ate', 'i drank',
            # Common non-answers / exclamations
            'oh my god', 'omg', 'wtf', 'this is so',
        ]
        for phrase in bad_phrases:
            if phrase.lower() in lower:
                return ""

        # Reject very short responses (< 12 chars)
        if len(text.strip()) < 12:
            return ""

        # Reject if the response is just a question back (no substance)
        stripped = text.strip()
        if stripped.endswith('?') and len(stripped) < 60 and stripped.count('.') == 0:
            return ""

        return text

    @staticmethod
    def _fallback(prompt: str) -> Dict[str, Any]:
        """Context-aware fallback when DialoGPT fails to produce a good response."""
        lower = prompt.lower()

        # Try to give a relevant fallback based on what was asked
        if any(w in lower for w in ['joke', 'funny', 'humor']):
            resp = "I'm better at helping with tasks than telling jokes, but I'll try to keep things light! What else can I help you with?"
        elif any(w in lower for w in ['meaning', 'life', 'purpose', 'philosophy']):
            resp = "That's a deep question. As an AI, I find purpose in helping you accomplish your goals. What would you like to work on?"
        elif lower.endswith('?'):
            resp = "That's a great question. I'd be happy to help you explore that topic. Could you give me a bit more context?"
        elif any(w in lower for w in ['think', 'opinion', 'feel']):
            resp = "As ARCHON, I'm focused on being helpful and accurate. I can share information and analysis on most topics. What would you like to know more about?"
        else:
            resp = "I understand. How can I assist you further? I can help with programming, file management, system operations, or just have a conversation."

        return {
            "response": resp,
            "confidence": 0.6,
            "model": "fallback",
            "fallback": True,
        }
