import re
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import pandas as pd
from dataclasses import dataclass
from enum import Enum
import unicodedata
import contractions

class PreprocessingLevel(Enum):
    """Levels of text preprocessing"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"

@dataclass
class PreprocessingConfig:
    """Configuration for text preprocessing"""
    level: PreprocessingLevel = PreprocessingLevel.STANDARD
    remove_stopwords: bool = True
    lemmatize: bool = True
    lowercase: bool = True
    remove_punctuation: bool = True
    remove_numbers: bool = False
    expand_contractions: bool = True
    remove_special_chars: bool = True
    min_word_length: int = 2
    max_word_length: int = 20
    vocabulary_size: int = 50000

class TextPreprocessor:
    """
    Advanced text preprocessing system for conversational AI training data
    """
    
    def __init__(self, config: PreprocessingConfig = None):
        self.config = config or PreprocessingConfig()
        
        # Download required NLTK data
        self._download_nltk_data()
        
        # Initialize components
        self.stop_words = set(stopwords.words('english')) if self.config.remove_stopwords else set()
        self.lemmatizer = WordNetLemmatizer() if self.config.lemmatize else None
        
        # Load spaCy model for advanced processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Advanced features will be limited.")
            self.nlp = None
        
        # Initialize label encoders
        self.intent_encoder = LabelEncoder()
        self.entity_encoder = LabelEncoder()
        
        # Vocabulary
        self.vocabulary = set()
        self.word_to_idx = {}
        self.idx_to_word = {}
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            print(f"Warning: Could not download NLTK data: {e}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Expand contractions
        if self.config.expand_contractions:
            text = contractions.fix(text)
        
        # Remove special characters and extra whitespace
        if self.config.remove_special_chars:
            text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Convert to lowercase
        if self.config.lowercase:
            text = text.lower()
        
        return text
    
    def tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        # Basic tokenization
        tokens = word_tokenize(text)
        
        # Filter tokens
        filtered_tokens = []
        for token in tokens:
            # Remove punctuation
            if self.config.remove_punctuation and not token.isalnum():
                continue
            
            # Remove numbers
            if self.config.remove_numbers and token.isdigit():
                continue
            
            # Filter by length
            if len(token) < self.config.min_word_length or len(token) > self.config.max_word_length:
                continue
            
            # Remove stopwords
            if token.lower() in self.stop_words:
                continue
            
            filtered_tokens.append(token)
        
        # Lemmatize
        if self.config.lemmatize and self.lemmatizer:
            filtered_tokens = [self.lemmatizer.lemmatize(token) for token in filtered_tokens]
        
        return filtered_tokens
    
    def extract_entities_advanced(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities using spaCy
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'times': [],
            'money': [],
            'products': [],
            'events': [],
            'file_paths': [],
            'process_names': [],
            'system_commands': []
        }
        
        if not self.nlp or not text:
            return entities
        
        try:
            doc = self.nlp(text)
            
            # Extract named entities
            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    entities['persons'].append(ent.text)
                elif ent.label_ == 'ORG':
                    entities['organizations'].append(ent.text)
                elif ent.label_ == 'GPE' or ent.label_ == 'LOC':
                    entities['locations'].append(ent.text)
                elif ent.label_ == 'DATE':
                    entities['dates'].append(ent.text)
                elif ent.label_ == 'TIME':
                    entities['times'].append(ent.text)
                elif ent.label_ == 'MONEY':
                    entities['money'].append(ent.text)
                elif ent.label_ == 'PRODUCT':
                    entities['products'].append(ent.text)
                elif ent.label_ == 'EVENT':
                    entities['events'].append(ent.text)
            
            # Extract computer-specific entities
            entities['file_paths'].extend(self._extract_file_paths(text))
            entities['process_names'].extend(self._extract_process_names(text))
            entities['system_commands'].extend(self._extract_system_commands(text))
        
        except Exception as e:
            print(f"Error in advanced entity extraction: {e}")
        
        return entities
    
    def _extract_file_paths(self, text: str) -> List[str]:
        """Extract file paths from text"""
        patterns = [
            r'[a-zA-Z]:\\[^"\'\s]*',
            r'["\']?([a-zA-Z]:\\[^"\'\\]+)["\']?',
            r'["\']?([^"\'\\]+\.[a-zA-Z0-9]+)["\']?',
            r'/[^"\'\s]*\.[a-zA-Z0-9]+'
        ]
        
        file_paths = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            file_paths.extend(matches)
        
        return list(set(file_paths))
    
    def _extract_process_names(self, text: str) -> List[str]:
        """Extract process names from text"""
        patterns = [
            r'["\']?([a-zA-Z0-9_\-\.]+\.exe)["\']?',
            r'["\']?([a-zA-Z0-9_\-]+)\.exe["\']?',
            r'\b([a-zA-Z]+\.exe)\b'
        ]
        
        process_names = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            process_names.extend(matches)
        
        return list(set(process_names))
    
    def _extract_system_commands(self, text: str) -> List[str]:
        """Extract system commands from text"""
        commands = [
            'shutdown', 'restart', 'reboot', 'sleep', 'hibernate',
            'lock', 'logout', 'logoff', 'create', 'delete', 'copy',
            'move', 'rename', 'list', 'open', 'close', 'start',
            'stop', 'kill', 'monitor', 'check', 'enable', 'disable'
        ]
        
        found_commands = []
        for command in commands:
            if command in text.lower():
                found_commands.append(command)
        
        return found_commands
    
    def extract_intent_features(self, text: str) -> Dict[str, float]:
        """
        Extract intent-related features from text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of intent features
        """
        features = {
            'question_score': 0.0,
            'command_score': 0.0,
            'greeting_score': 0.0,
            'help_score': 0.0,
            'file_operation_score': 0.0,
            'process_management_score': 0.0,
            'system_control_score': 0.0,
            'voice_command_score': 0.0,
            'urgency_score': 0.0,
            'politeness_score': 0.0
        }
        
        if not text:
            return features
        
        text_lower = text.lower()
        
        # Question indicators
        question_words = ['what', 'where', 'when', 'why', 'how', 'who', 'which', 'can', 'could', 'would', 'should', 'is', 'are', 'do', 'does', 'did']
        features['question_score'] = sum(1 for word in question_words if word in text_lower) / len(question_words)
        
        # Command indicators
        command_words = ['please', 'can you', 'could you', 'would you', 'help me', 'i need', 'i want']
        features['command_score'] = sum(1 for word in command_words if word in text_lower) / len(command_words)
        
        # Greeting indicators
        greeting_words = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
        features['greeting_score'] = sum(1 for word in greeting_words if word in text_lower) / len(greeting_words)
        
        # Help indicators
        help_words = ['help', 'assist', 'support', 'guide', 'tutorial', 'how to', 'explain']
        features['help_score'] = sum(1 for word in help_words if word in text_lower) / len(help_words)
        
        # File operation indicators
        file_words = ['file', 'folder', 'directory', 'create', 'delete', 'copy', 'move', 'rename', 'list', 'open', 'save']
        features['file_operation_score'] = sum(1 for word in file_words if word in text_lower) / len(file_words)
        
        # Process management indicators
        process_words = ['process', 'program', 'application', 'start', 'stop', 'kill', 'restart', 'monitor', 'running']
        features['process_management_score'] = sum(1 for word in process_words if word in text_lower) / len(process_words)
        
        # System control indicators
        system_words = ['system', 'shutdown', 'restart', 'reboot', 'sleep', 'hibernate', 'lock', 'logout', 'settings', 'configuration']
        features['system_control_score'] = sum(1 for word in system_words if word in text_lower) / len(system_words)
        
        # Voice command indicators
        voice_words = ['speak', 'voice', 'say', 'tell', 'announce', 'louder', 'softer', 'faster', 'slower', 'repeat']
        features['voice_command_score'] = sum(1 for word in voice_words if word in text_lower) / len(voice_words)
        
        # Urgency indicators
        urgency_words = ['urgent', 'emergency', 'immediately', 'asap', 'quickly', 'fast', 'now', 'right now']
        features['urgency_score'] = sum(1 for word in urgency_words if word in text_lower) / len(urgency_words)
        
        # Politeness indicators
        politeness_words = ['please', 'thank', 'thanks', 'appreciate', 'kindly', 'could you', 'would you']
        features['politeness_score'] = sum(1 for word in politeness_words if word in text_lower) / len(politeness_words)
        
        return features
    
    def preprocess_conversation_pair(self, input_text: str, target_text: str) -> Dict[str, Any]:
        """
        Preprocess a conversation pair
        
        Args:
            input_text: User input
            target_text: Assistant response
            
        Returns:
            Preprocessed conversation data
        """
        # Clean texts
        cleaned_input = self.clean_text(input_text)
        cleaned_target = self.clean_text(target_text)
        
        # Tokenize
        input_tokens = self.tokenize_text(cleaned_input)
        target_tokens = self.tokenize_text(cleaned_target)
        
        # Extract entities
        input_entities = self.extract_entities_advanced(input_text)
        target_entities = self.extract_entities_advanced(target_text)
        
        # Extract features
        input_features = self.extract_intent_features(input_text)
        target_features = self.extract_intent_features(target_text)
        
        # Update vocabulary
        self.vocabulary.update(input_tokens)
        self.vocabulary.update(target_tokens)
        
        return {
            'input_text': cleaned_input,
            'target_text': cleaned_target,
            'input_tokens': input_tokens,
            'target_tokens': target_tokens,
            'input_entities': input_entities,
            'target_entities': target_entities,
            'input_features': input_features,
            'target_features': target_features
        }
    
    def build_vocabulary(self, texts: List[str], min_frequency: int = 2) -> Dict[str, int]:
        """
        Build vocabulary from texts
        
        Args:
            texts: List of texts to build vocabulary from
            min_frequency: Minimum frequency for a word to be included
            
        Returns:
            Dictionary mapping words to indices
        """
        word_counts = {}
        
        for text in texts:
            cleaned_text = self.clean_text(text)
            tokens = self.tokenize_text(cleaned_text)
            
            for token in tokens:
                word_counts[token] = word_counts.get(token, 0) + 1
        
        # Filter by frequency and create vocabulary
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Add special tokens
        self.word_to_idx = {
            '<PAD>': 0,
            '<UNK>': 1,
            '<SOS>': 2,
            '<EOS>': 3
        }
        
        # Add most frequent words
        for word, count in sorted_words:
            if count >= min_frequency and len(self.word_to_idx) < self.config.vocabulary_size:
                self.word_to_idx[word] = len(self.word_to_idx)
        
        # Create reverse mapping
        self.idx_to_word = {idx: word for word, idx in self.word_to_idx.items()}
        self.vocabulary = set(self.word_to_idx.keys())
        
        print(f"Vocabulary built: {len(self.word_to_idx)} words")
        return self.word_to_idx
    
    def text_to_sequence(self, text: str, max_length: int = 512) -> List[int]:
        """
        Convert text to sequence of indices
        
        Args:
            text: Input text
            max_length: Maximum sequence length
            
        Returns:
            List of token indices
        """
        cleaned_text = self.clean_text(text)
        tokens = self.tokenize_text(cleaned_text)
        
        # Convert to indices
        sequence = [self.word_to_idx.get(token, self.word_to_idx['<UNK>']) for token in tokens]
        
        # Add special tokens
        sequence = [self.word_to_idx['<SOS>']] + sequence + [self.word_to_idx['<EOS>']]
        
        # Pad or truncate
        if len(sequence) > max_length:
            sequence = sequence[:max_length]
        else:
            sequence = sequence + [self.word_to_idx['<PAD>']] * (max_length - len(sequence))
        
        return sequence
    
    def sequence_to_text(self, sequence: List[int]) -> str:
        """
        Convert sequence of indices back to text
        
        Args:
            sequence: List of token indices
            
        Returns:
            Reconstructed text
        """
        tokens = [self.idx_to_word.get(idx, '<UNK>') for idx in sequence]
        
        # Remove special tokens
        tokens = [token for token in tokens if token not in ['<PAD>', '<SOS>', '<EOS>']]
        
        return ' '.join(tokens)
    
    def compute_text_statistics(self, texts: List[str]) -> Dict[str, Any]:
        """
        Compute statistics about the text corpus
        
        Args:
            texts: List of texts
            
        Returns:
            Dictionary of text statistics
        """
        all_tokens = []
        all_lengths = []
        
        for text in texts:
            cleaned_text = self.clean_text(text)
            tokens = self.tokenize_text(cleaned_text)
            all_tokens.extend(tokens)
            all_lengths.append(len(tokens))
        
        # Compute statistics
        stats = {
            'total_texts': len(texts),
            'total_tokens': len(all_tokens),
            'unique_tokens': len(set(all_tokens)),
            'avg_text_length': np.mean(all_lengths) if all_lengths else 0,
            'median_text_length': np.median(all_lengths) if all_lengths else 0,
            'min_text_length': min(all_lengths) if all_lengths else 0,
            'max_text_length': max(all_lengths) if all_lengths else 0,
            'std_text_length': np.std(all_lengths) if all_lengths else 0
        }
        
        # Token frequency distribution
        token_counts = {}
        for token in all_tokens:
            token_counts[token] = token_counts.get(token, 0) + 1
        
        stats['most_common_tokens'] = sorted(token_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        stats['vocabulary_size'] = len(token_counts)
        
        return stats
    
    def augment_text(self, text: str, augmentation_type: str = 'synonym') -> str:
        """
        Augment text for training data diversity
        
        Args:
            text: Input text
            augmentation_type: Type of augmentation ('synonym', 'paraphrase', 'noise')
            
        Returns:
            Augmented text
        """
        if augmentation_type == 'synonym':
            return self._synonym_replacement(text)
        elif augmentation_type == 'paraphrase':
            return self._paraphrase_text(text)
        elif augmentation_type == 'noise':
            return self._add_noise(text)
        else:
            return text
    
    def _synonym_replacement(self, text: str) -> str:
        """Replace words with synonyms (simplified)"""
        # This is a simplified implementation
        # In practice, you'd use WordNet or a synonym dictionary
        synonyms = {
            'help': ['assist', 'aid', 'support'],
            'create': ['make', 'generate', 'produce'],
            'delete': ['remove', 'erase', 'eliminate'],
            'open': ['launch', 'start', 'begin'],
            'close': ['shut', 'end', 'terminate']
        }
        
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in synonyms:
                words[i] = np.random.choice(synonyms[word.lower()])
        
        return ' '.join(words)
    
    def _paraphrase_text(self, text: str) -> str:
        """Paraphrase text (simplified implementation)"""
        # This would typically use a paraphrasing model
        # For now, just shuffle word order slightly
        words = text.split()
        if len(words) > 3:
            # Swap two random words
            i, j = np.random.choice(len(words), 2, replace=False)
            words[i], words[j] = words[j], words[i]
        
        return ' '.join(words)
    
    def _add_noise(self, text: str) -> str:
        """Add small noise to text"""
        noise_types = ['typo', 'extra_space', 'missing_space']
        noise_type = np.random.choice(noise_types)
        
        if noise_type == 'typo' and len(text) > 5:
            # Introduce a simple typo
            idx = np.random.randint(1, len(text) - 1)
            text = text[:idx] + text[idx+1:] + text[idx]
        
        elif noise_type == 'extra_space':
            # Add extra space
            words = text.split()
            if len(words) > 1:
                idx = np.random.randint(len(words))
                words.insert(idx, '')
            text = ' '.join(words)
        
        elif noise_type == 'missing_space':
            # Remove a space
            words = text.split()
            if len(words) > 2:
                idx = np.random.randint(len(words) - 1)
                words[idx] = words[idx] + words[idx+1]
                del words[idx+1]
            text = ' '.join(words)
        
        return text
    
    def save_preprocessor(self, path: str):
        """Save preprocessor state"""
        state = {
            'config': self.config.__dict__,
            'word_to_idx': self.word_to_idx,
            'idx_to_word': self.idx_to_word,
            'vocabulary': list(self.vocabulary)
        }
        
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"Preprocessor saved to {path}")
    
    def load_preprocessor(self, path: str):
        """Load preprocessor state"""
        with open(path, 'r') as f:
            state = json.load(f)
        
        self.config = PreprocessingConfig(**state['config'])
        self.word_to_idx = state['word_to_idx']
        self.idx_to_word = {int(k): v for k, v in state['idx_to_word'].items()}
        self.vocabulary = set(state['vocabulary'])
        
        print(f"Preprocessor loaded from {path}")
