"""
Fluent Conversation System for ARCHON

This module provides natural, human-like conversation responses
without unnecessary pauses or robotic phrasing.
"""

import re
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class ConversationStyle:
    """Defines conversation style preferences"""
    formality: str = "casual"  # casual, formal, professional
    enthusiasm: float = 0.7  # 0.0 to 1.0
    verbosity: str = "balanced"  # concise, balanced, detailed
    personality: str = "helpful"  # helpful, witty, professional, friendly

class FluentConversationManager:
    """Manages fluid, human-like conversations"""
    
    def __init__(self):
        self.style = ConversationStyle()
        self.conversation_patterns = self._load_conversation_patterns()
        self.response_templates = self._load_response_templates()
        self.context_memory = []
        
    def _load_conversation_patterns(self) -> Dict[str, List[str]]:
        """Load natural conversation patterns"""
        return {
            "greetings": [
                "Hey there!", "Hi!", "Hello!", "Good to see you!", 
                "Hey!", "What's up?", "How's it going?"
            ],
            "acknowledgments": [
                "Got it!", "I see!", "Understood!", "Right!", 
                "Makes sense!", "I get it!", "Okay!", "Sure!"
            ],
            "transitions": [
                "Anyway,", "So,", "Well then,", "Moving on,", 
                "That reminds me,", "Speaking of which,", "By the way,"
            ],
            "enthusiasm": [
                "Awesome!", "Great!", "Excellent!", "Perfect!",
                "Fantastic!", "Wonderful!", "Brilliant!", "Cool!"
            ],
            "helpful": [
                "I'd be happy to help!", "Of course!", "Absolutely!",
                "Let me help you with that.", "I can definitely assist.",
                "I'm on it!", "Consider it done!", "No problem!"
            ],
            "clarifications": [
                "Let me make sure I understand...", "Just to clarify...",
                "So you're saying...", "If I'm following correctly...",
                "So what you mean is...", "Am I right in thinking..."
            ],
            "completions": [
                "All set!", "Done!", "There you go!", "And that's it!",
                "Mission accomplished!", "Good to go!", "Ready when you are!"
            ],
            "concern": [
                "Hmm, let me think about this...", "That's interesting...",
                "I need to consider...", "Let me make sure...",
                "I should mention...", "Be careful with..."
            ]
        }
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates for different situations"""
        return {
            "file_operations": [
                "I'll handle that file operation for you.",
                "Let me take care of those files.",
                "I can work with your files right away.",
                "File management - I'm on it!",
                "I'll help you organize your files."
            ],
            "programming_help": [
                "I'd love to help with your code!",
                "Programming questions - I'm here for it!",
                "Let me assist with your development.",
                "Code assistance coming right up!",
                "I can definitely help with that."
            ],
            "system_info": [
                "I'll check the system status for you.",
                "Let me gather that system information.",
                "I'll look into the system details.",
                "System check - on it now!",
                "I'll get those system metrics."
            ],
            "general_chat": [
                "That's an interesting point!",
                "I love discussing this with you!",
                "That's a great question!",
                "Let me think about that...",
                "That makes perfect sense!"
            ],
            "errors": [
                "Hmm, something's not quite right here.",
                "I ran into a small issue.",
                "Let me try a different approach.",
                "I need to handle this carefully.",
                "Something needs my attention here."
            ],
            "success": [
                "Perfect! That worked out great.",
                "Excellent! Everything went smoothly.",
                "Great! Mission accomplished.",
                "Awesome! That's all set.",
                "Brilliant! It's done."
            ]
        }
    
    def generate_fluent_response(self, user_input: str, intent: str, 
                               entities: Dict[str, Any], context: str = "") -> str:
        """
        Generate a natural, human-like response
        
        Args:
            user_input: User's message
            intent: Detected intent
            entities: Extracted entities
            context: Conversation context
            
        Returns:
            Natural, fluent response
        """
        # Add to conversation memory
        self.context_memory.append({
            'timestamp': datetime.now(),
            'user_input': user_input,
            'intent': intent
        })
        
        # Keep memory manageable
        if len(self.context_memory) > 10:
            self.context_memory = self.context_memory[-5:]
        
        # Generate response based on intent and context
        if intent == "greeting":
            return self._generate_greeting_response(user_input)
        elif intent == "file_operation":
            return self._generate_file_response(entities, context)
        elif intent == "programming_help":
            return self._generate_programming_response(user_input, entities)
        elif intent == "system_info":
            return self._generate_system_response(entities, context)
        elif intent == "question":
            return self._generate_question_response(user_input, context)
        elif intent == "help_request":
            return self._generate_help_response(user_input, entities)
        else:
            return self._generate_general_response(user_input, context)
    
    def _generate_greeting_response(self, user_input: str) -> str:
        """Generate natural greeting response"""
        greetings = self.conversation_patterns["greetings"]
        base_greeting = random.choice(greetings)
        
        # Add contextual element
        if "how are you" in user_input.lower():
            return f"{base_greeting} I'm doing great, thanks for asking! Ready to help with whatever you need."
        elif "what's up" in user_input.lower():
            return f"{base_greeting} Just here and ready to assist! What can I help you with today?"
        else:
            return f"{base_greeting} I'm here to help! What's on your mind?"
    
    def _generate_file_response(self, entities: Dict[str, Any], context: str) -> str:
        """Generate natural file operation response"""
        templates = self.response_templates["file_operations"]
        base_response = random.choice(templates)
        
        operation = entities.get('operation', '')
        if operation:
            if operation == 'list':
                return f"{base_response} I'll show you what's in the directory right away."
            elif operation == 'create':
                return f"{base_response} What kind of file or folder would you like to create?"
            elif operation == 'delete':
                return f"{base_response} Just to be sure, which file would you like me to remove?"
            elif operation == 'copy':
                return f"{base_response} What would you like to copy and where should it go?"
            else:
                return f"{base_response} I'll help you {operation} your files."
        else:
            return f"{base_response} I'm ready to work with your files!"
    
    def _generate_programming_response(self, user_input: str, entities: Dict[str, Any]) -> str:
        """Generate natural programming help response"""
        templates = self.response_templates["programming_help"]
        base_response = random.choice(templates)
        
        # Check for specific programming needs
        if "error" in user_input.lower() or "bug" in user_input.lower():
            return f"{base_response} Let me help you debug this. What error are you seeing?"
        elif "optimize" in user_input.lower() or "improve" in user_input.lower():
            return f"{base_response} I'd love to help optimize your code! What specific improvements are you looking for?"
        elif "explain" in user_input.lower():
            return f"{base_response} I'll break it down for you. What part needs explanation?"
        else:
            return f"{base_response} What programming challenge can I help you solve?"
    
    def _generate_system_response(self, entities: Dict[str, Any], context: str) -> str:
        """Generate natural system information response"""
        templates = self.response_templates["system_info"]
        base_response = random.choice(templates)
        
        operation = entities.get('operation', '')
        if operation:
            if operation == 'check':
                return f"{base_response} I'll get you the latest system status."
            elif operation == 'monitor':
                return f"{base_response} I'll keep an eye on system performance for you."
            else:
                return f"{base_response} I'll handle that system operation."
        else:
            return f"{base_response} I'm ready to help with system tasks!"
    
    def _generate_question_response(self, user_input: str, context: str) -> str:
        """Generate natural question response"""
        # Analyze the question
        if "why" in user_input.lower():
            return "That's a great question! Let me explain the reasoning behind it."
        elif "how" in user_input.lower():
            return "I'll walk you through how that works step by step."
        elif "what" in user_input.lower():
            return "Let me break down what that means for you."
        elif "can you" in user_input.lower():
            return "Absolutely! I can definitely help with that."
        else:
            return "That's an interesting question! Let me give you a thorough answer."
    
    def _generate_help_response(self, user_input: str, entities: Dict[str, Any]) -> str:
        """Generate natural help response"""
        templates = self.response_templates["general_chat"]
        base_response = random.choice(templates)
        
        return f"{base_response} I'm here to assist with programming, file management, system operations, and much more. What specific area can I help you with?"
    
    def _generate_general_response(self, user_input: str, context: str) -> str:
        """Generate natural general conversation response"""
        user_lower = user_input.lower()
        
        # Acknowledgments and agreements
        if any(word in user_lower for word in ["yes", "yeah", "sure", "ok", "okay"]):
            return "Got it! What would you like to do next?"
        
        # Expressions of thanks
        if any(word in user_lower for word in ["thank", "thanks", "appreciate"]):
            return "You're welcome! Let me know if there's anything else I can help with."
        
        # Expressions of understanding
        if any(word in user_lower for word in ["understand", "got it", "see", "right"]):
            return "Great, glad we're on the same page. What's next?"
        
        # Default
        return "I'm here to help. What can I do for you?"
    
    def add_conversation_flavor(self, response: str) -> str:
        """Return the response without injecting random filler words."""
        return response
    
    def get_conversation_context(self) -> str:
        """Get current conversation context for better responses"""
        if not self.context_memory:
            return "new_conversation"
        
        recent_intents = [item['intent'] for item in self.context_memory[-3:]]
        
        if len(set(recent_intents)) == 1 and recent_intents[0] != "general_chat":
            return f"focused_on_{recent_intents[0]}"
        elif len(set(recent_intents)) > 2:
            return "varied_topics"
        else:
            return "casual_chat"

class NaturalLanguageProcessor:
    """Processes natural language for better conversation flow"""
    
    def __init__(self):
        self.contractions = {
            "I am": "I'm",
            "you are": "you're", 
            "it is": "it's",
            "that is": "that's",
            "we are": "we're",
            "they are": "they're",
            "do not": "don't",
            "cannot": "can't",
            "will not": "won't",
            "I have": "I've",
            "you have": "you've",
            "we have": "we've",
            "they have": "they've",
            "I would": "I'd",
            "you would": "you'd",
            "I will": "I'll",
            "you will": "you'll"
        }
    
    def naturalize_text(self, text: str) -> str:
        """Make text sound more natural by using contractions and conversational patterns"""
        # Apply contractions
        for formal, informal in self.contractions.items():
            text = text.replace(formal, informal)
        
        # Remove overly formal phrases
        formal_phrases = [
            "I would be happy to",
            "I would like to",
            "Please allow me to",
            "It would be my pleasure to"
        ]
        
        informal_replacements = [
            "I'd love to",
            "I'd like to",
            "Let me",
            "I'd be glad to"
        ]
        
        for formal, informal in zip(formal_phrases, informal_replacements):
            text = text.replace(formal, informal)
        
        # Remove robotic phrases
        robotic_phrases = [
            "I understand",
            "I can help you",
            "Please specify",
            "I am processing"
        ]
        
        natural_replacements = [
            "Got it",
            "I can help",
            "Let me know",
            "I'm on it"
        ]
        
        for formal, informal in zip(robotic_phrases, natural_replacements):
            text = text.replace(formal, informal)
        
        return text
    
    def add_conversational_connectors(self, text: str) -> str:
        """Add natural conversational connectors"""
        sentences = text.split('. ')
        
        if len(sentences) > 1:
            # Add connectors between sentences
            connectors = ["Also,", "Plus,", "And,", "So,", "Well,"]
            
            for i in range(len(sentences) - 1):
                if random.random() < 0.2:  # 20% chance
                    connector = random.choice(connectors)
                    sentences[i] = f"{sentences[i].rstrip('.')} {connector}"
        
        return '. '.join(sentences)

# Global instance for use in ARCHON
fluent_conversation = FluentConversationManager()
natural_processor = NaturalLanguageProcessor()
