import torch
import torch.nn.functional as F
from typing import List, Dict, Optional, Tuple, Any
import re
import json
import random
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Import fluent conversation system
try:
    from .fluent_conversation import fluent_conversation, natural_processor
    FLUENT_CONVERSATION_AVAILABLE = True
except ImportError:
    FLUENT_CONVERSATION_AVAILABLE = False

class ConversationIntent(Enum):
    """Enumeration of conversation intents"""
    GENERAL_CHAT = "general_chat"
    FILE_OPERATION = "file_operation"
    PROCESS_MANAGEMENT = "process_management"
    SYSTEM_CONTROL = "system_control"
    VOICE_COMMAND = "voice_command"
    HELP_REQUEST = "help_request"
    LEARNING_REQUEST = "learning_request"
    PROGRAMMING_ASSISTANCE = "programming_assistance"
    CREATIVE_TASK = "creative_task"
    PROBLEM_SOLVING = "problem_solving"
    TECHNICAL_EXPLANATION = "technical_explanation"
    CODE_REVIEW = "code_review"
    ARCHITECTURE_DESIGN = "architecture_design"
    RESEARCH_QUERY = "research_query"
    EMOTIONAL_SUPPORT = "emotional_support"
    STRATEGIC_PLANNING = "strategic_planning"
    LEARNING_ANALYSIS = "learning_analysis"
    UNKNOWN = "unknown"

@dataclass
class ConversationContext:
    """Data class for conversation context"""
    user_id: str
    session_id: str
    timestamp: datetime
    previous_turns: List[Dict[str, Any]]
    computer_state: Dict[str, Any]
    voice_active: bool = False
    current_directory: str = ""

class ConversationManager:
    """
    Advanced conversation management system with context awareness
    and computer interaction understanding
    """
    
    def __init__(self, max_context_length: int = 10):
        self.max_context_length = max_context_length
        self.conversation_history = []
        self.context_patterns = self._load_context_patterns()
        self.intent_classifiers = self._initialize_intent_classifiers()
        
    def _load_context_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for different conversation contexts"""
        return {
            'file_operations': [
                r'create\s+(file|folder|directory)',
                r'delete\s+(file|folder|directory)',
                r'copy\s+(file|folder)',
                r'move\s+(file|folder)',
                r'open\s+file',
                r'save\s+file',
                r'list\s+(files|directories)',
                r'find\s+file',
                r'rename\s+file',
                r'change\s+directory'
            ],
            'process_management': [
                r'start\s+(process|program|application)',
                r'stop\s+(process|program|application)',
                r'kill\s+process',
                r'restart\s+(process|program)',
                r'list\s+(processes|running)',
                r'check\s+(process|status)',
                r'monitor\s+(process|performance)'
            ],
            'system_control': [
                r'shutdown\s+(computer|system)',
                r'restart\s+(computer|system)',
                r'sleep\s+(computer|system)',
                r'hibernate\s+(computer|system)',
                r'lock\s+(computer|screen)',
                r'log\s+out',
                r'change\s+(settings|configuration)',
                r'check\s+(system|status|performance)'
            ],
            'voice_commands': [
                r'speak\s+(louder|softer)',
                r'change\s+voice',
                r'stop\s+speaking',
                r'repeat\s+(that|again)',
                r'enable\s+voice',
                r'disable\s+voice',
                r'voice\s+(on|off)'
            ],
            'help_requests': [
                r'help\s+me',
                r'how\s+to',
                r'what\s+can\s+you\s+do',
                r'show\s+commands',
                r'explain\s+(how|what)',
                r'tutorial',
                r'guide\s+me'
            ]
        }
    
    def _initialize_intent_classifiers(self) -> Dict[str, Any]:
        """Initialize intent classification models"""
        # This would typically load pre-trained models
        # For now, we'll use rule-based classification
        return {
            'file_ops_weight': 0.3,
            'process_ops_weight': 0.25,
            'system_ops_weight': 0.2,
            'voice_ops_weight': 0.15,
            'help_weight': 0.1
        }
    
    def classify_intent(self, user_input: str) -> ConversationIntent:
        """
        Classify the intent of user input
        
        Args:
            user_input: The user's input string
            
        Returns:
            Classified conversation intent
        """
        user_input_lower = user_input.lower()
        
        # Check each pattern category
        for intent, patterns in self.context_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    return self._map_pattern_to_intent(intent)
        
        return ConversationIntent.UNKNOWN
    
    def _map_pattern_to_intent(self, pattern_category: str) -> ConversationIntent:
        """Map pattern category to conversation intent"""
        mapping = {
            'file_operations': ConversationIntent.FILE_OPERATION,
            'process_management': ConversationIntent.PROCESS_MANAGEMENT,
            'system_control': ConversationIntent.SYSTEM_CONTROL,
            'voice_commands': ConversationIntent.VOICE_COMMAND,
            'help_requests': ConversationIntent.HELP_REQUEST
        }
        return mapping.get(pattern_category, ConversationIntent.UNKNOWN)
    
    def extract_entities(self, user_input: str, intent: ConversationIntent) -> Dict[str, Any]:
        """
        Extract relevant entities from user input based on intent
        
        Args:
            user_input: The user's input string
            intent: Classified conversation intent
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        if intent == ConversationIntent.FILE_OPERATION:
            entities.update(self._extract_file_entities(user_input))
        elif intent == ConversationIntent.PROCESS_MANAGEMENT:
            entities.update(self._extract_process_entities(user_input))
        elif intent == ConversationIntent.SYSTEM_CONTROL:
            entities.update(self._extract_system_entities(user_input))
        elif intent == ConversationIntent.VOICE_COMMAND:
            entities.update(self._extract_voice_entities(user_input))
        
        # Extract common entities
        entities.update(self._extract_common_entities(user_input))
        
        return entities
    
    def _extract_file_entities(self, user_input: str) -> Dict[str, Any]:
        """Extract file-related entities"""
        entities = {}
        
        # File paths
        path_pattern = r'["\']?([a-zA-Z]:\\[^"\']+)["\']?'
        paths = re.findall(path_pattern, user_input)
        if paths:
            entities['file_paths'] = paths
        
        # File names
        file_pattern = r'["\']?([^"\'\\]+\.[a-zA-Z0-9]+)["\']?'
        files = re.findall(file_pattern, user_input)
        if files:
            entities['file_names'] = files
        
        # Operations
        operations = ['create', 'delete', 'copy', 'move', 'open', 'save', 'list', 'find', 'rename']
        for op in operations:
            if op in user_input.lower():
                entities['operation'] = op
                break
        
        return entities
    
    def _extract_process_entities(self, user_input: str) -> Dict[str, Any]:
        """Extract process-related entities"""
        entities = {}
        
        # Process names
        process_pattern = r'["\']?([a-zA-Z0-9_\-\.]+\.exe)["\']?'
        processes = re.findall(process_pattern, user_input, re.IGNORECASE)
        if processes:
            entities['process_names'] = processes
        
        # Operations
        operations = ['start', 'stop', 'kill', 'restart', 'list', 'check', 'monitor']
        for op in operations:
            if op in user_input.lower():
                entities['operation'] = op
                break
        
        return entities
    
    def _extract_system_entities(self, user_input: str) -> Dict[str, Any]:
        """Extract system-related entities"""
        entities = {}
        
        # System operations
        operations = ['shutdown', 'restart', 'sleep', 'hibernate', 'lock', 'logout', 'change', 'check']
        for op in operations:
            if op in user_input.lower():
                entities['operation'] = op
                break
        
        # Settings
        settings = ['volume', 'brightness', 'display', 'network', 'power', 'security']
        for setting in settings:
            if setting in user_input.lower():
                entities['setting'] = setting
                break
        
        return entities
    
    def _extract_voice_entities(self, user_input: str) -> Dict[str, Any]:
        """Extract voice-related entities"""
        entities = {}
        
        # Voice commands
        commands = ['speak', 'change', 'stop', 'repeat', 'enable', 'disable']
        for cmd in commands:
            if cmd in user_input.lower():
                entities['voice_command'] = cmd
                break
        
        # Voice settings
        settings = ['louder', 'softer', 'faster', 'slower', 'voice']
        for setting in settings:
            if setting in user_input.lower():
                entities['voice_setting'] = setting
                break
        
        return entities
    
    def _extract_common_entities(self, user_input: str) -> Dict[str, Any]:
        """Extract common entities across all intents"""
        entities = {}
        
        # Numbers
        numbers = re.findall(r'\b\d+\b', user_input)
        if numbers:
            entities['numbers'] = [int(n) for n in numbers]
        
        # Time expressions
        time_patterns = [
            r'\b\d{1,2}:\d{2}\s*(am|pm)?\b',
            r'\b(in\s+\d+\s+(minutes|hours|seconds))\b',
            r'\b(at\s+\d{1,2}:\d{2})\b'
        ]
        for pattern in time_patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            if matches:
                entities['time_expressions'] = matches
                break
        
        return entities
    
    def generate_contextual_response(self, user_input: str, intent: ConversationIntent, 
                                   entities: Dict[str, Any], context: ConversationContext) -> str:
        """
        Generate a contextual response based on intent, entities, and conversation context
        
        Args:
            user_input: The user's input string
            intent: Classified conversation intent
            entities: Extracted entities
            context: Conversation context
            
        Returns:
            Generated response string
        """
        # Use fluent conversation system if available
        if FLUENT_CONVERSATION_AVAILABLE:
            # Map intents to fluent conversation intents
            intent_mapping = {
                ConversationIntent.GENERAL_CHAT: "general_chat",
                ConversationIntent.FILE_OPERATION: "file_operation", 
                ConversationIntent.PROCESS_MANAGEMENT: "system_info",
                ConversationIntent.SYSTEM_CONTROL: "system_info",
                ConversationIntent.VOICE_COMMAND: "general_chat",
                ConversationIntent.HELP_REQUEST: "help_request",
                ConversationIntent.UNKNOWN: "general_chat"
            }
            
            fluent_intent = intent_mapping.get(intent, "general_chat")
            
            # Override for questions and greetings that the intent classifier misses
            lower = user_input.strip().lower()
            if fluent_intent == "general_chat":
                if lower.endswith('?') or lower.startswith(('what ', 'how ', 'why ', 'who ', 'where ', 'when ', 'can you', 'could you', 'is there', 'do you')):
                    fluent_intent = "question"
                elif any(g in lower for g in ['hello', 'hi ', 'hi!', 'hey', 'good morning', 'good afternoon', 'good evening']):
                    fluent_intent = "greeting"
            
            # Generate fluent response
            fluent_response = fluent_conversation.generate_fluent_response(
                user_input, fluent_intent, entities, str(context)
            )
            
            # Naturalize the text
            naturalized = natural_processor.naturalize_text(fluent_response)
            
            # Add conversational flavor
            final_response = fluent_conversation.add_conversation_flavor(naturalized)
            
            return final_response
        
        # Fallback to original system if fluent conversation not available
        if intent == ConversationIntent.FILE_OPERATION:
            return self._generate_file_response(entities, context)
        elif intent == ConversationIntent.PROCESS_MANAGEMENT:
            return self._generate_process_response(entities, context)
        elif intent == ConversationIntent.SYSTEM_CONTROL:
            return self._generate_system_response(entities, context)
        elif intent == ConversationIntent.VOICE_COMMAND:
            return self._generate_voice_response(entities, context)
        elif intent == ConversationIntent.HELP_REQUEST:
            return self._generate_help_response(entities, context)
        else:
            return self._generate_general_response(user_input, context)
    
    def _generate_file_response(self, entities: Dict[str, Any], context: ConversationContext) -> str:
        """Generate response for file operations"""
        operation = entities.get('operation', 'unknown')
        
        if operation == 'list':
            return "I'll show you what's in the directory right away."
        elif operation == 'create':
            return "I can create that for you! What kind of file or folder would you like?"
        elif operation == 'delete':
            return "I can help remove files. Just to be sure, which ones would you like me to delete?"
        elif operation == 'open':
            return "I'll open that file for you. Which one would you like to access?"
        elif operation == 'copy':
            return "I can copy that! Where would you like me to put the copy?"
        elif operation == 'move':
            return "I'll move that for you. Where should it go?"
        else:
            return f"I'll help you {operation} your files. Let me know the details!"
    
    def _generate_process_response(self, entities: Dict[str, Any], context: ConversationContext) -> str:
        """Generate response for process management"""
        operation = entities.get('operation', 'unknown')
        
        if operation == 'list':
            return "I'll show you all the running processes right now."
        elif operation == 'start':
            return "I can start that for you! Which program would you like me to launch?"
        elif operation == 'stop':
            return "I can stop that process for you. Which one should I terminate?"
        elif operation == 'restart':
            return "I'll restart that process for you. Which one needs restarting?"
        elif operation == 'kill':
            return "I'll terminate that process. Just to be sure, which PID should I kill?"
        else:
            return f"I'll help you {operation} the processes. Let me know which ones!"
    
    def _generate_system_response(self, entities: Dict[str, Any], context: ConversationContext) -> str:
        """Generate response for system control"""
        operation = entities.get('operation', 'unknown')
        
        if operation == 'shutdown':
            return "I can help you shutdown the system. Are you absolutely sure about this?"
        elif operation == 'restart':
            return "I'll restart the system for you. Ready to proceed with the restart?"
        elif operation == 'check':
            return "I'll check the system status and performance for you right now."
        elif operation == 'monitor':
            return "I'll keep an eye on system performance for you."
        elif operation == 'sleep':
            return "I can put the system to sleep. Ready to power it down?"
        else:
            return f"I'll help you {operation} the system. Just let me know when you're ready!"
    
    def _generate_voice_response(self, entities: Dict[str, Any], context: ConversationContext) -> str:
        """Generate response for voice commands"""
        command = entities.get('voice_command', 'unknown')
        
        if command == 'enable':
            return "Voice control is now enabled! You can use voice commands to interact with me."
        elif command == 'disable':
            return "Voice control is now disabled. Just let me know when you'd like to turn it back on."
        elif command == 'speak':
            return "I'll adjust my speaking voice as requested. How does that sound?"
        elif command == 'stop':
            return "I'll stop speaking. Is there anything else I can help you with?"
        else:
            return f"I'll help you with the {command} voice command. What would you like me to do?"
    
    def _generate_help_response(self, entities: Dict[str, Any], context: ConversationContext) -> str:
        """Generate response for help requests"""
        help_text = """
I'm here to help with all sorts of tasks! Here's what I can do:

**File Operations:**
- Create, delete, copy, move files and folders
- List directory contents  
- Find and rename files
- Read and edit file contents

**Programming Help:**
- Code analysis and debugging
- Explain programming concepts
- Suggest improvements and optimizations
- Help with multiple programming languages

**System Management:**
- Monitor system performance
- Manage running processes
- Check system status and health
- Handle system operations safely

**Voice Interaction:**
- Text-to-speech and speech-to-text
- Voice commands and control
- Natural conversation

**Self-Improvement:**
- Learn from our interactions
- Improve my own capabilities
- Adapt to your preferences

Just tell me what you'd like to do, and I'll help you get it done!
        """
        return help_text.strip()
    
    def _generate_general_response(self, user_input: str, context: ConversationContext) -> str:
        """Generate response for general conversation"""
        # More natural greeting patterns
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        user_input_lower = user_input.lower()
        
        for greeting in greetings:
            if greeting in user_input_lower:
                return f"Hey there! I'm ready to help. What can I do for you?"
        
        # More natural question handling
        if user_input_lower.endswith('?'):
            if "how" in user_input_lower:
                return "I'll walk you through how that works step by step."
            elif "why" in user_input_lower:
                return "That's a great question! Let me explain the reasoning behind it."
            elif "what" in user_input_lower:
                return "Let me break down what that means for you."
            else:
                return "That's an interesting question! I'd love to help you with that."
        
        # More natural acknowledgments
        if any(word in user_input_lower for word in ["yes", "yeah", "sure", "ok", "okay", "right"]):
            return "Got it! What's next?"
        
        # More natural thanks
        if any(word in user_input_lower for word in ["thank", "thanks", "appreciate"]):
            return "You're very welcome! Always happy to help."
        
        # More natural general responses
        natural_responses = [
            "I'm here and ready to help! What's on your mind?",
            "Sounds good! How can I assist you?",
            "I'd love to help! What do you need?",
            "I'm listening! What can I do for you?",
            "Ready when you are! What's your question?"
        ]
        
        return random.choice(natural_responses)
