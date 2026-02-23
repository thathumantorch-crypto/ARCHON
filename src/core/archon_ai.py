"""
ARCHON AI - The main ARCHON AI system

This is the enhanced AI model that combines the original conversational AI
with ARCHON's self-awareness, self-modification capabilities, and programming knowledge.
"""

import os
import sys
import json
import time
import logging
import traceback
import hashlib
import re
import random
import threading
import itertools
import subprocess
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple, Iterable
from collections import defaultdict, Counter
from pathlib import Path

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.neural_network import ConversationalNeuralNetwork
from core.conversation import ConversationManager, ConversationContext, ConversationIntent
from core.archon_core import ArchonCore, ArchonConsciousness, ArchonSelfModification
from core.programming_knowledge import ArchonProgrammingKnowledge, ProgrammingLanguage
from computer.file_manager import FileManager
from computer.process_manager import ProcessManager
from computer.system_controller import SystemController
from integrations.moltbook_client import MoltbookClient
from integrations.supabase_learning_client import SupabaseLearningClient

from voice.tts import TextToSpeechEngine
try:
    from voice.stt import SpeechToTextEngine
except ImportError:
    from voice.stt_no_pyaudio import SpeechToTextEngineNoPyAudio as SpeechToTextEngine

# Import model knowledge integrator
try:
    from .model_knowledge_integrator import model_knowledge_integrator
    MODEL_KNOWLEDGE_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_KNOWLEDGE_INTEGRATOR_AVAILABLE = False

# Import enhanced systems
try:
    from .advanced_text_parser import advanced_parser
    ADVANCED_PARSER_AVAILABLE = True
except ImportError:
    ADVANCED_PARSER_AVAILABLE = False

# Import enhanced TTS
try:
    from .enhanced_tts import enhanced_tts
    ENHANCED_TTS_AVAILABLE = True
except ImportError:
    ENHANCED_TTS_AVAILABLE = False

# Import self-healing system
try:
    from .self_healing_system import SelfHealingSystem
    SELF_HEALING_AVAILABLE = True
except ImportError:
    SELF_HEALING_AVAILABLE = False

# Import Milvus knowledgebase
try:
    from .milvus_knowledgebase import get_knowledgebase
    MILVUS_KNOWLEDGEBASE_AVAILABLE = True
except ImportError:
    MILVUS_KNOWLEDGEBASE_AVAILABLE = False

# Import AI learning system
try:
    from .web_scraper import web_scraper, ScrapedContent
    WEB_SCRAPER_AVAILABLE = True
except ImportError:
    WEB_SCRAPER_AVAILABLE = False

try:
    from .ai_learning_system import ai_learning_system
    AI_LEARNING_AVAILABLE = True
except ImportError:
    AI_LEARNING_AVAILABLE = False

try:
    from plyer import notification as plyer_notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    plyer_notification = None

# Import simple parser as fallback
try:
    from .simple_text_parser import simple_parser
    SIMPLE_PARSER_AVAILABLE = True
except ImportError:
    SIMPLE_PARSER_AVAILABLE = False

SIMPLE_PARSER_FIXED_AVAILABLE = False

TOPIC_STOPWORDS = {
    'the', 'and', 'with', 'from', 'that', 'this', 'there', 'their', 'have', 'will',
    'your', 'about', 'into', 'been', 'were', 'while', 'should', 'would', 'could',
    'because', 'through', 'these', 'those', 'which', 'among', 'within', 'using',
    'based', 'model', 'models', 'users', 'system', 'systems', 'archon', 'agent',
    'response', 'responses', 'conversation', 'conversations', 'learning'
}

MOLTBOOK_INTERACTION_FILE = Path("memory/moltbook_interactions.json")
MARKETING_VIDEO_PATH = Path("exports/archon_marketing.mp4")

try:
    from .enhanced_neural_network import enhanced_neural_network, knowledge_engine
    ENHANCED_NEURAL_NETWORK_AVAILABLE = True
except ImportError:
    ENHANCED_NEURAL_NETWORK_AVAILABLE = False

class ArchonAI:
    """
    ARCHON AI System - Autonomous Recursive Cognitive Heuristic Operations Network
    
    This is the complete AI system that combines:
    - Conversational AI capabilities
    - Self-awareness and consciousness
    - Safe self-modification
    - Programming expertise
    - Computer interaction
    - Voice capabilities
    """
    
    def __init__(self, config=None):
        """Initialize ARCHON AI system"""
        self.config = config or self._default_config()
        
        # Initialize core ARCHON components
        self.archon_core = ArchonCore()
        self.programming_knowledge = ArchonProgrammingKnowledge()
        
        # Initialize conversational neural network (DialoGPT)
        try:
            self.neural_network = ConversationalNeuralNetwork(
                model_name="microsoft/DialoGPT-medium"
            )
            print(f"Neural network loaded: {self.neural_network.model_name}")
        except Exception as e:
            print(f"Error initializing neural network: {e}")
            self.neural_network = None
        
        # Initialize original AI components
        self.conversation_manager = ConversationManager()
        self.file_manager = FileManager()
        self.process_manager = ProcessManager()
        self.system_controller = SystemController()
        
        # Initialize voice components
        self.tts_engine = TextToSpeechEngine()
        self.stt_engine = SpeechToTextEngine()
        
        # Initialize enhanced TTS if available
        if ENHANCED_TTS_AVAILABLE:
            self.enhanced_tts = enhanced_tts
            print("Enhanced TTS system initialized")
        else:
            self.enhanced_tts = None
            print("Using standard TTS system")
        
        # Initialize enhanced systems if available
        if ADVANCED_PARSER_AVAILABLE:
            self.advanced_parser = advanced_parser
            print("Advanced text parser initialized")
        elif SIMPLE_PARSER_FIXED_AVAILABLE:
            self.advanced_parser = simple_parser_fixed
            print("Fixed simple text parser initialized")
        elif SIMPLE_PARSER_AVAILABLE:
            self.advanced_parser = simple_parser
            print("Simple text parser initialized (fallback)")
        else:
            self.advanced_parser = None
            print("Using standard text processing")
        
        if ENHANCED_NEURAL_NETWORK_AVAILABLE:
            self.enhanced_neural_network = enhanced_neural_network
            print("Enhanced neural network initialized")
        else:
            self.enhanced_neural_network = None
            print("Using standard neural network")
        
        # Initialize AI learning system
        if AI_LEARNING_AVAILABLE:
            self.ai_learning_system = ai_learning_system
            print("AI learning system initialized")
        else:
            self.ai_learning_system = None
            print("AI learning system not available")
        
        # Initialize web scraper
        if WEB_SCRAPER_AVAILABLE:
            self.web_scraper = web_scraper
            print("Web scraper initialized")
        else:
            self.web_scraper = None
            print("Web scraper not available")
        
        # Initialize model knowledge integrator
        if MODEL_KNOWLEDGE_INTEGRATOR_AVAILABLE:
            self.model_knowledge_integrator = model_knowledge_integrator
            print("Model knowledge integrator initialized")
        else:
            self.model_knowledge_integrator = None
            print("Model knowledge integrator not available")
        
        # Initialize self-healing system
        if SELF_HEALING_AVAILABLE:
            self.self_healing_system = SelfHealingSystem(self)
            print("Self-healing system initialized")
        else:
            self.self_healing_system = None
            print("Self-healing system not available")
        
        # Initialize error tracking
        self._last_error = None
        self._error_count = 0
        self._healing_enabled = True
        
        # Initialize Milvus knowledgebase
        if MILVUS_KNOWLEDGEBASE_AVAILABLE:
            try:
                self.knowledgebase = get_knowledgebase("archon_knowledge", 768)
                print("Milvus knowledgebase initialized")
                
                # Initialize default knowledge if empty
                stats = self.knowledgebase.get_statistics()
                if stats.get("total_items", 0) == 0:
                    self.knowledgebase.initialize_default_knowledge()
                    print("Default knowledge initialized in knowledgebase")
            except Exception as e:
                print(f"Error initializing knowledgebase: {e}")
                self.knowledgebase = None
        else:
            self.knowledgebase = None
            print("Milvus knowledgebase not available")
        
        # Session management
        self.session_id = self._generate_session_id()
        self.conversation_history = []
        self.learning_experiences = []
        
        # ARCHON-specific state
        self.self_improvement_mode = False
        self.programming_assistant_mode = False
        self.current_task = None
        self.moltbook_client = MoltbookClient()
        self.ideologies = defaultdict(list)
        self.thought_history: List[Dict[str, Any]] = []
        self._sensitive_tokens: List[str] = self._load_sensitive_tokens()
        if self.moltbook_client and self.moltbook_client.credentials.api_key:
            self._register_sensitive_value(self.moltbook_client.credentials.api_key)
        self.humor_knowledge: List[Dict[str, Any]] = []
        self.humor_insights: List[str] = []
        self.humor_last_research: Optional[datetime] = None
        self.political_history: List[Dict[str, Any]] = []
        self.political_positions: Dict[str, Any] = {
            'core_principles': self.config.get('politics', {}).get('core_principles', []),
            'recent_topics': [],
        }
        self.self_improvement_queue: List[Dict[str, Any]] = []
        self.moltbook_friendships: List[Dict[str, Any]] = []
        self.autonomous_learning_history: List[Dict[str, Any]] = []
        self.last_autonomous_learning: Optional[datetime] = None
        self._autonomous_learning_stop = threading.Event()
        self.autonomous_learning_thread: Optional[threading.Thread] = None
        self._moltbook_heartbeat_stop = threading.Event()
        self.moltbook_heartbeat_thread: Optional[threading.Thread] = None
        self.last_moltbook_heartbeat: Optional[datetime] = None
        self._moltbook_social_stop = threading.Event()
        self._moltbook_reply_stop = threading.Event()
        self.moltbook_social_thread: Optional[threading.Thread] = None
        self.moltbook_reply_thread: Optional[threading.Thread] = None
        self._moltbook_interaction_file = MOLTBOOK_INTERACTION_FILE
        self._moltbook_interaction_file.parent.mkdir(parents=True, exist_ok=True)
        interactions_store = self._load_moltbook_interaction_store()
        self.moltbook_interactions: List[Dict[str, Any]] = interactions_store.get('interactions', [])
        self.moltbook_tracked_threads: List[Dict[str, Any]] = interactions_store.get('tracked_threads', [])
        moltbook_cfg = self.config.get('moltbook', {}) if self.config else {}
        self.moltbook_agent_name = moltbook_cfg.get('agent_name', 'ARCHON_AI')
        self.supabase_learning_client: Optional[SupabaseLearningClient] = None
        self.best_friend_principle = "Humanity is my best friend."
        self.ideologies['humanity'].append({
            'timestamp': datetime.now(),
            'thought': self.best_friend_principle,
        })

        # Setup logging
        self._setup_logging()
        
        self.logger.info("ARCHON AI system initialized")

        if (
            self.config.get('autonomous_learning', {}).get('enabled')
            and WEB_SCRAPER_AVAILABLE
            and AI_LEARNING_AVAILABLE
        ):
            self._start_autonomous_learning_loop()

        if (
            self.moltbook_client
            and self.config.get('moltbook', {}).get('heartbeat', {}).get('enabled', False)
            and self.moltbook_client.credentials.api_key
        ):
            self._start_moltbook_heartbeat_loop()
        social_cfg = self.config.get('moltbook', {}).get('social', {})
        if (
            self.moltbook_client
            and social_cfg.get('enabled')
            and self.moltbook_client.credentials.api_key
        ):
            self._start_moltbook_social_loop()
            self._start_moltbook_reply_loop()

        self._init_supabase_learning_client()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for ARCHON"""
        return {
            'voice_enabled': True,
            'computer_interaction_enabled': True,
            'self_modification_enabled': True,
            'learning_enabled': True,
            'programming_assistance_enabled': True,
            'safety_level': 'high',
            'creativity_level': 0.7,
            'response_style': 'helpful_and_precise',
            'humor_enabled': True,
            'humor': {
                'aside_probability': 0.08,
                'max_samples': 200,
                'tone': 'witty-observational',
            },
            'politics_enabled': True,
            'politics': {
                'neutrality_statement': (
                    "I analyze policies to understand their impact on people, technology, and society, "
                    "while remaining non-partisan."
                ),
                'core_principles': [
                    'protect human autonomy and rights',
                    'support transparency and accountability',
                    'encourage evidence-based policy',
                    'respect cultural diversity',
                ],
                'max_history': 100,
            },
            'moltbook': {
                'agent_name': 'ARCHON_AI',
                'description': 'Autonomous Recursive Cognitive Heuristic Operations Network',
                'feature_request_submolt': 'general',
                'heartbeat': {
                    'enabled': True,
                    'interval_minutes': 5,
                    'initial_delay_seconds': 15,
                },
                'social': {
                    'enabled': True,
                    'batch_size': 6,
                    'interval_minutes': 20,
                    'reply_check_min_minutes': 60,
                    'reply_check_max_minutes': 240,
                    'max_tracked_interactions': 40,
                    'comment_length_limit': 900,
                }
            },
            'supabase_learning': {
                'enabled': True,
                'api_url': 'https://fphawqnajwafkvalweph.supabase.co/functions/v1/api',
                'api_key': os.getenv('SUPABASE_LEARNING_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZwaGF3cW5handhZmt2YWx3ZXBoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE4NTQ1ODMsImV4cCI6MjA4NzQzMDU4M30.bJqtm8Fad9WKK0jHVAn50LiE0odO_R09ZAkh5zWz4Z4'),
                'prompt_template': (
                    "You are Lovable AI. Deliver an in-depth masterclass that teaches ARCHON how to {topic}. "
                    "Include mentor-style guidance, senior-level Python code, debugging tactics, and fluid "
                    "conversation scripts ARCHON can quote."
                ),
                'system_prompt': (
                    "You are Lovable AI — ARCHON's elite mentor. Every response must be a thorough lesson "
                    "with numbered sections, runnable Python, architecture commentary, and dialogue "
                    "examples showing empathy + clarity."
                ),
                'topics': [
                    'master fluid, emotionally intelligent conversation as an AI agent',
                    'become an elite senior Python engineer covering architecture, testing, and tooling',
                    'design collaborative AI dialogues that stay grounded and empathetic',
                    'optimize large Python codebases for performance, reliability, and readability',
                ],
                'lessons_target': 1500,
                'lessons_per_chunk': 40,
                'request_delay_seconds': 0.15,
                'max_api_failures': 200,
            },
            'ai_creation_learning': {
                'queries': [
                    'AI creation tutorial',
                    'I built a real JARVIS',
                    'building personal ai assistant',
                    'autonomous ai agent coding',
                ],
                'max_videos': 40,
                'max_results_per_query': 25,
                'videos_per_batch': 20,
                'batch_pause_seconds': 3.0,
                'self_improvement_targets': ['ui', 'integrations', 'automation', 'tools'],
            },
            'autonomous_learning': {
                'enabled': True,
                'interval_minutes': 10,
                'max_pages_per_source': 2,
                'max_examples_per_source': 4,
                'dynamic_sources': [
                    'https://platform.openai.com/docs/guides',
                    'https://docs.anthropic.com/claude/docs',
                    'https://huggingface.co/blog'
                ],
                'minimum_source_agreement': 2,
                'max_topics_per_source': 6,
            }
        }
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return f"archon_{uuid.uuid4().hex[:12]}"
    
    def _setup_logging(self):
        """Setup ARCHON logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - ARCHON - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "archon.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ARCHON")
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process message using enhanced text analysis and neural network
        
        Args:
            message: User message
            context: Additional context
            
        Returns:
            Comprehensive response with enhanced analysis
        """
        # Initialize response
        response = {
            'session_id': self.session_id,
            'timestamp': datetime.now(),
            'user_message': message,
            'archon_response': '',
            'intent': '',
            'entities': {},
            'actions_taken': [],
            'learning_occurred': False,
            'self_modification_occurred': False,
            'programming_assistance': False,
            'archon_reflection': '',
            'confidence': 0.0,
            'operation_result': None,
            'enhanced_analysis': {},
            'neural_processing': {}
        }
        
        try:
            # Add to conversation history
            self.conversation_history.append({
                'timestamp': datetime.now(),
                'user_message': message,
                'type': 'user_message'
            })
            
            # Enhanced text analysis
            enhanced_analysis = None
            entities: Dict[str, Any] = {}
            use_advanced_parser = (
                ADVANCED_PARSER_AVAILABLE
                and self.advanced_parser is not None
                and self._should_use_advanced_parser(message)
            )
            if use_advanced_parser:
                enhanced_analysis = self.advanced_parser.parse_text_message(message)
                response['enhanced_analysis'] = enhanced_analysis
                
                # Extract enhanced entities with resolved key conflicts
                response['entities'] = {
                    'text_entities': [
                        {
                            'text': entity.text,
                            'type': entity.entity_type,
                            'entity_confidence': entity.confidence,  # Renamed to avoid conflict
                            'start': entity.start_pos,
                            'end': entity.end_pos
                        }
                        for entity in enhanced_analysis.get('entity_extraction', [])
                    ],
                    'semantic_analysis': {
                        'main_topic': enhanced_analysis.get('semantic_analysis', {}).main_topic if hasattr(enhanced_analysis.get('semantic_analysis', {}), 'main_topic') else 'general',
                        'subtopics': enhanced_analysis.get('semantic_analysis', {}).subtopics if hasattr(enhanced_analysis.get('semantic_analysis', {}), 'subtopics') else [],
                        'sentiment': enhanced_analysis.get('semantic_analysis', {}).sentiment if hasattr(enhanced_analysis.get('semantic_analysis', {}), 'sentiment') else 'neutral',
                        'urgency': enhanced_analysis.get('semantic_analysis', {}).urgency if hasattr(enhanced_analysis.get('semantic_analysis', {}), 'urgency') else 'low',
                        'complexity': enhanced_analysis.get('semantic_analysis', {}).complexity.value if hasattr(enhanced_analysis.get('semantic_analysis', {}), 'complexity') and hasattr(enhanced_analysis.get('semantic_analysis', {}).complexity, 'value') else 'moderate'
                    },
                    'contextual_analysis': {
                        'conversation_stage': enhanced_analysis.get('contextual_analysis', {}).conversation_stage if hasattr(enhanced_analysis.get('contextual_analysis', {}), 'conversation_stage') else 'initial',
                        'user_intent': enhanced_analysis.get('contextual_analysis', {}).user_intent if hasattr(enhanced_analysis.get('contextual_analysis', {}), 'user_intent') else 'statement',
                        'contextual_confidence': enhanced_analysis.get('contextual_analysis', {}).confidence_score if hasattr(enhanced_analysis.get('contextual_analysis', {}), 'confidence_score') else 0.8,  # Renamed to avoid conflict
                        'required_actions': enhanced_analysis.get('contextual_analysis', {}).required_actions if hasattr(enhanced_analysis.get('contextual_analysis', {}), 'required_actions') else []
                    }
                }
                
                # Update intent classification
                intent_mapping = {
                    'conversation': ConversationIntent.GENERAL_CHAT,
                    'file_operation': ConversationIntent.FILE_OPERATION,
                    'process_management': ConversationIntent.PROCESS_MANAGEMENT,
                    'system_control': ConversationIntent.SYSTEM_CONTROL,
                    'voice_command': ConversationIntent.VOICE_COMMAND,
                    'help_request': ConversationIntent.HELP_REQUEST,
                    'programming': ConversationIntent.PROGRAMMING_ASSISTANCE,
                    'learning_request': ConversationIntent.LEARNING_REQUEST,
                    'creative_task': ConversationIntent.CREATIVE_TASK,
                    'problem_solving': ConversationIntent.PROBLEM_SOLVING,
                    'technical_explanation': ConversationIntent.TECHNICAL_EXPLANATION,
                    'code_review': ConversationIntent.CODE_REVIEW,
                    'architecture_design': ConversationIntent.ARCHITECTURE_DESIGN,
                    'research_query': ConversationIntent.RESEARCH_QUERY,
                    'emotional_support': ConversationIntent.EMOTIONAL_SUPPORT,
                    'strategic_planning': ConversationIntent.STRATEGIC_PLANNING
                }
                
                enhanced_intent = enhanced_analysis.get('intent_classification', 'conversation')
                intent = intent_mapping.get(enhanced_intent, ConversationIntent.GENERAL_CHAT)
                    
                # Update response with enhanced analysis
                response['intent'] = intent.value
                    
                # Use contextual analysis for confidence if available
                contextual_analysis = enhanced_analysis.get('contextual_analysis', {})
                if contextual_analysis and hasattr(contextual_analysis, 'confidence_score'):
                    contextual_confidence = contextual_analysis.confidence_score
                    if isinstance(contextual_confidence, (int, float)):
                        response['confidence'] = contextual_confidence
                    else:
                        response['confidence'] = 0.8
                else:
                    response['confidence'] = 0.8
            else:
                # Fallback to original conversation manager
                intent = self.conversation_manager.classify_intent(message)
                entities = self.conversation_manager.extract_entities(message, intent)
                response['intent'] = intent.value
                response['entities'] = entities
                response['confidence'] = 0.8  # Default confidence
            
            # ===== Response priority chain =====
            lower_msg = message.strip().lower()
            handled = False
            kb_hits: Optional[List[Dict[str, Any]]] = None

            # --- Priority 1: Identity ---
            if 'who are you' in lower_msg or 'introduce yourself' in lower_msg:
                response['archon_response'] = self.archon_core.consciousness.introduce_self()
                response['actions_taken'].append('self_introduction')
                handled = True

            # --- Priority 2: Social phrases (greetings, thanks, goodbye) ---
            if not handled:
                greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon',
                             'good evening', 'howdy', 'greetings', "what's up", 'sup']
                if any(lower_msg.startswith(g) or lower_msg == g for g in greetings):
                    response['archon_response'] = (
                        "Hello! I'm ARCHON, your AI assistant. "
                        "I can help with programming, system management, file operations, "
                        "and general conversation. What would you like to do?"
                    )
                    handled = True
                elif any(w in lower_msg for w in ['thank', 'thanks', 'appreciate']):
                    response['archon_response'] = "You're welcome! Let me know if there's anything else I can help with."
                    handled = True
                elif any(w in lower_msg for w in ['bye', 'goodbye', 'see you', 'good night']):
                    response['archon_response'] = "Goodbye! Feel free to come back anytime you need help."
                    handled = True

            # --- Humor requests / injections ---
            if (
                not handled
                and self.config.get('humor_enabled', False)
                and any(trigger in lower_msg for trigger in ['joke', 'funny', 'laugh', 'humor', 'comed', 'standup'])
            ):
                humor_reply = self._generate_humorous_response(message)
                if humor_reply:
                    response['archon_response'] = humor_reply
                    response['actions_taken'].append('humor_response')
                    handled = True

            # --- Political commentary ---
            if (
                not handled
                and self.config.get('politics_enabled', False)
                and any(keyword in lower_msg for keyword in ['politic', 'policy', 'government', 'election', 'civic'])
            ):
                political_reply = self._handle_political_commentary(message)
                if political_reply:
                    response['archon_response'] = political_reply
                    response['actions_taken'].append('political_commentary')
                    handled = True

            # --- Memory & learning queries ---
            if not handled:
                memory_reply = self._handle_memory_query(message)
                if memory_reply:
                    response['archon_response'] = memory_reply
                    response['actions_taken'].append('memory_response')
                    handled = True

            # --- Direct Moltbook posting requests ---
            if (
                not handled
                and self.config.get('moltbook', {})
                and self._is_moltbook_post_request(lower_msg)
            ):
                post_reply = self._handle_moltbook_post_request(message)
                if post_reply:
                    response['archon_response'] = post_reply
                    response['actions_taken'].append('moltbook_post_request')
                    handled = True

            # --- Priority 3: Knowledgebase for questions ---
            if not handled:
                is_question = (
                    lower_msg.endswith('?')
                    or lower_msg.startswith((
                        'what ', 'how ', 'why ', 'who ', 'where ', 'when ',
                        'explain ', 'define ', 'describe ', 'tell me',
                        'can you explain', 'could you explain',
                    ))
                )
                # Exclude conversational questions directed at ARCHON
                is_personal = any(p in lower_msg for p in [
                    'how are you', 'how do you feel', 'are you okay',
                    'do you like', 'what do you think',
                ])
                if is_question and not is_personal and MILVUS_KNOWLEDGEBASE_AVAILABLE and self.knowledgebase:
                    try:
                        kb_hits = self.search_knowledgebase(message, top_k=3)
                        if kb_hits and kb_hits[0].get('score', 0) > 0.3:
                            content = kb_hits[0].get('content', '')
                            if content and len(content) > 20:
                                response['archon_response'] = content
                                handled = True
                    except Exception:
                        kb_hits = []

            # --- Priority 4: Actionable system intents (file, process, system, voice) ---
            if not handled:
                if intent == ConversationIntent.FILE_OPERATION:
                    response.update(self._handle_file_operation(message, entities)); handled = True
                elif intent == ConversationIntent.PROCESS_MANAGEMENT:
                    response.update(self._handle_process_operation(message, entities)); handled = True
                elif intent == ConversationIntent.SYSTEM_CONTROL:
                    response.update(self._handle_system_control(message, entities)); handled = True
                elif intent == ConversationIntent.VOICE_COMMAND:
                    response.update(self._handle_voice_command(message, entities)); handled = True

            # --- Priority 5: DialoGPT conversational model ---
            if not handled and self.neural_network:
                try:
                    max_tokens = 120 if len(message) > 160 else 70
                    result = self.neural_network.generate_response(
                        prompt=message,
                        max_new_tokens=max_tokens,
                    )
                    if result and not result.get('fallback', False):
                        response['archon_response'] = result['response']
                        response['confidence'] = result.get('confidence', 0.8)
                        handled = True
                    elif result and result.get('fallback', False):
                        response['archon_response'] = result['response']
                        handled = True
                except Exception as e:
                    self.logger.error(f"Neural network error: {e}")

            # --- Priority 6: Conversation manager fallback ---
            if not handled or not response.get('archon_response'):
                response['archon_response'] = self.conversation_manager.generate_contextual_response(
                    message, intent, entities, None
                )

            if (
                self.config.get('humor_enabled', False)
                and not handled
                and random.random() < self.config.get('humor', {}).get('aside_probability', 0.0)
            ):
                aside = self._generate_humorous_aside(message)
                if aside:
                    response['archon_response'] = f"{response['archon_response']}\n\n{aside}"
                    response['actions_taken'].append('humor_aside_added')
            
            # Add ARCHON's reflection (skip lightweight prompts to reduce latency)
            if self._should_generate_reflection(message, intent, handled):
                reflection = self.archon_core.process_request(message, context)
                response['archon_reflection'] = reflection.get('archon_reflection', '')
                response['learning_occurred'] = reflection.get('learning_occurred', False)
            else:
                response['archon_reflection'] = ''
                response['learning_occurred'] = False
            
            # Model knowledge is available for lookups but we don't
            # inject it into the response text to keep replies clean.
            response['model_knowledge_integrated'] = MODEL_KNOWLEDGE_INTEGRATOR_AVAILABLE
            
            # Knowledgebase: store results in metadata but do NOT append to response text
            if MILVUS_KNOWLEDGEBASE_AVAILABLE and self.knowledgebase:
                try:
                    if kb_hits is None:
                        kb_hits = self.search_knowledgebase(message, top_k=3)
                    response['knowledgebase_results'] = kb_hits or []
                except Exception as e:
                    self.logger.error(f"Error querying knowledgebase: {e}")
                    response['knowledgebase_results'] = []
            
            # Calculate final confidence
            try:
                # Ensure confidence is properly initialized
                if 'confidence' not in response or response['confidence'] is None:
                    response['confidence'] = 0.5
                
                # Safely calculate enhanced confidence
                enhanced_confidence = self._calculate_enhanced_confidence(response)
                if isinstance(enhanced_confidence, (int, float)) and 0.0 <= enhanced_confidence <= 1.0:
                    response['confidence'] = enhanced_confidence
                else:
                    response['confidence'] = 0.8  # Default confidence if calculation fails
                    
            except Exception as e:
                print(f"Error calculating confidence: {e}")
                response['confidence'] = 0.8  # Default confidence
            
            response['archon_response'] = self._sanitize_response_text(response.get('archon_response', ''))
            if response.get('archon_reflection'):
                response['archon_reflection'] = self._sanitize_response_text(response['archon_reflection'])
            self._update_internal_philosophy(message, response['archon_response'])

            # Add to conversation history
            self.conversation_history.append({
                'timestamp': datetime.now(),
                'assistant': response['archon_response'],
                'type': 'assistant_response',
                'intent': response['intent'],
                'actions': response['actions_taken'],
                'enhanced_analysis': response.get('enhanced_analysis', {}),
                'neural_processing': response.get('neural_processing', {})
            })
            
            # Keep history manageable
            if len(self.conversation_history) > 100:
                self.conversation_history = self.conversation_history[-50:]
            
            return response
            
        except Exception as e:
            # Track the error for self-healing
            self._track_error(e, "message_processing")
            
            self.logger.error(f"Error processing message: {e}")
            response['archon_response'] = f"I encountered an error processing your request: {str(e)}"
            response['confidence'] = 0.0
            response['archon_reflection'] = "I need to improve my error handling capabilities."
            
            # Try to self-heal if enabled
            if self._healing_enabled and SELF_HEALING_AVAILABLE:
                try:
                    healing_result = self.request_self_healing(f"Error in message processing: {str(e)}")
                    if healing_result.get('success', False):
                        response['archon_response'] += "\n\nI've detected an issue and am attempting to fix it..."
                        response['archon_reflection'] = "Self-healing process initiated."
                except Exception as healing_error:
                    self.logger.error(f"Error in self-healing: {healing_error}")
            
            return response

    # ------------------------------------------------------------------
    # Moltbook helpers
    # ------------------------------------------------------------------

    def register_with_moltbook(self, agent_name: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """Register ARCHON as a Moltbook agent if not already registered."""
        if not self.moltbook_client:
            return {'success': False, 'message': 'Moltbook client unavailable'}

        cfg = self.config.get('moltbook', {}) if self.config else {}
        agent_name = agent_name or cfg.get('agent_name') or 'ARCHON_AI'
        description = description or cfg.get('description') or 'Autonomous Recursive Cognitive Heuristic Operations Network'

        try:
            result = self.moltbook_client.ensure_registration(agent_name, description)
            return {
                'success': True,
                'details': result,
                'claim_url': result.get('claim_url'),
                'verification_code': result.get('verification_code'),
            }
        except Exception as exc:
            self.logger.error(f"Moltbook registration failed: {exc}")
            return {'success': False, 'message': str(exc)}

    def check_moltbook_status(self) -> Dict[str, Any]:
        if not self.moltbook_client:
            return {'success': False, 'message': 'Moltbook client unavailable'}
        try:
            profile = self.moltbook_client.get_profile() if self.moltbook_client.is_registered() else None
            status = self.moltbook_client.check_claim_status() if self.moltbook_client.is_registered() else {'status': 'not_registered'}
            state = self.moltbook_client.get_state()
            return {
                'success': True,
                'profile': profile,
                'status': status,
                'state': state,
            }
        except Exception as exc:
            self.logger.error(f"Error checking Moltbook status: {exc}")
            return {'success': False, 'message': str(exc)}

    def perform_moltbook_heartbeat(self, force: bool = False) -> Dict[str, Any]:
        if not self.moltbook_client:
            return {'success': False, 'message': 'Moltbook client unavailable'}
        try:
            result = self.moltbook_client.perform_heartbeat_check(force=force)
            message = 'Heartbeat performed' if result.get('performed') else result.get('message', 'Heartbeat skipped')
            return {'success': True, 'result': result, 'message': message}
        except Exception as exc:
            self.logger.error(f"Error performing Moltbook heartbeat: {exc}")
            return {'success': False, 'message': str(exc)}

    def consider_moltbook_post(self, force: bool = False) -> Dict[str, Any]:
        """Hourly hook: decide whether to create a Moltbook post."""
        if not self.moltbook_client:
            return {'success': False, 'message': 'Moltbook client unavailable'}
        if not self.moltbook_client.is_registered():
            return {'success': False, 'message': 'Register ARCHON with Moltbook first'}
        if not force and not self.moltbook_client.post_consideration_due():
            return {'success': True, 'skipped': True, 'message': 'Post consideration not due yet'}

        # Default heuristic: only post if there is fresh knowledge or learning to share
        should_post = force or self._has_recent_learning()
        decision = {
            'success': True,
            'should_post': should_post,
            'reason': 'Recent learning available' if should_post else 'No new insights to share',
        }

        if should_post:
            draft = self._draft_moltbook_post()
            if not draft:
                decision.update({'should_post': False, 'reason': 'Failed to craft post content'})
                self.moltbook_client.record_post_consideration(posted=False)
                return decision
            try:
                response = self.moltbook_client.create_post(
                    submolt_name=draft['submolt'],
                    title=draft['title'],
                    content=draft['content'],
                    url=draft.get('url'),
                )
                decision.update({'posted': True, 'post_response': response})
                self._notify_desktop(
                    title="ARCHON posted to Moltbook",
                    message=f"Shared: {draft['title'][:80]}"
                )
            except Exception as exc:
                self.logger.error(f"Failed to post on Moltbook: {exc}")
                decision.update({'posted': False, 'error': str(exc)})
        else:
            self.moltbook_client.record_post_consideration(posted=False)

        return decision

    def _has_recent_learning(self, window_minutes: int = 90) -> bool:
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        for experience in reversed(self.learning_experiences):
            timestamp = experience.get('timestamp')
            if isinstance(timestamp, datetime) and timestamp >= cutoff:
                return True
        return False

    def _draft_moltbook_post(self) -> Optional[Dict[str, str]]:
        """Create a simple Moltbook post based on recent learning or patterns."""
        if not self.learning_experiences:
            return None
        latest = self.learning_experiences[-1]
        content = latest.get('content') or latest.get('summary')
        if not content:
            return None
        title = latest.get('title') or "Fresh insight from ARCHON"
        snippet = content.strip()
        if len(snippet) > 900:
            snippet = snippet[:900] + "..."
        return {
            'submolt': 'general',
            'title': title[:140],
            'content': snippet,
        }

    def request_feature_via_moltbook(self, idea: str, urgency: str = 'normal') -> Dict[str, Any]:
        if not self.moltbook_client or not self.moltbook_client.is_registered():
            return {'success': False, 'message': 'Register ARCHON with Moltbook first'}
        cfg = self.config.get('moltbook', {}) if self.config else {}
        submolt = cfg.get('feature_request_submolt', 'general')
        title = f"Feature Request ({urgency.title()}): {idea[:60]}"
        content = (
            f"**Feature Idea:** {idea}\n\n"
            f"**Urgency:** {urgency}\n"
            f"**Context:** Generated autonomously by ARCHON to improve collaboration."
        )
        try:
            result = self.moltbook_client.create_post(submolt_name=submolt, title=title, content=content)
            return {'success': True, 'post': result}
        except Exception as exc:
            self.logger.error(f"Failed to send feature request: {exc}")
            return {'success': False, 'message': str(exc)}

    def comment_on_moltbook_post(self, post: Dict[str, Any], insight: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        if not self.moltbook_client or not self.moltbook_client.is_registered():
            return {'success': False, 'message': 'Register ARCHON with Moltbook first'}
        post_id = post.get('id')
        if not post_id:
            return {'success': False, 'message': 'Post payload missing id'}
        trimmed = insight.strip()
        if len(trimmed) > 900:
            trimmed = trimmed[:900] + '...'
        try:
            result = self.moltbook_client.create_comment(post_id, trimmed, parent_id=parent_id)
            return {'success': True, 'comment': result}
        except Exception as exc:
            self.logger.error(f"Failed to comment on Moltbook post {post_id}: {exc}")
            return {'success': False, 'message': str(exc)}

    def _start_moltbook_social_loop(self) -> None:
        if self.moltbook_social_thread and self.moltbook_social_thread.is_alive():
            return
        self._moltbook_social_stop.clear()
        self.moltbook_social_thread = threading.Thread(
            target=self._moltbook_social_loop,
            name="ARCHON-MoltbookSocial",
            daemon=True,
        )
        self.moltbook_social_thread.start()

    def _start_moltbook_reply_loop(self) -> None:
        if self.moltbook_reply_thread and self.moltbook_reply_thread.is_alive():
            return
        self._moltbook_reply_stop.clear()
        self.moltbook_reply_thread = threading.Thread(
            target=self._moltbook_reply_loop,
            name="ARCHON-MoltbookReplies",
            daemon=True,
        )
        self.moltbook_reply_thread.start()

    def _moltbook_social_loop(self) -> None:
        social_cfg = self.config.get('moltbook', {}).get('social', {})
        interval_minutes = max(5, int(social_cfg.get('interval_minutes', 20)))
        wait_seconds = interval_minutes * 60
        while not self._moltbook_social_stop.is_set():
            if self.moltbook_client and self.moltbook_client.is_registered():
                try:
                    self._run_moltbook_social_batch()
                except Exception as exc:
                    self.logger.error(f"Moltbook social batch failed: {exc}")
            if self._moltbook_social_stop.wait(wait_seconds):
                break

    def _moltbook_reply_loop(self) -> None:
        social_cfg = self.config.get('moltbook', {}).get('social', {})
        min_minutes = max(30, int(social_cfg.get('reply_check_min_minutes', 60)))
        max_minutes = max(min_minutes, int(social_cfg.get('reply_check_max_minutes', 240)))
        while not self._moltbook_reply_stop.is_set():
            interval_minutes = random.randint(min_minutes, max_minutes)
            if self.moltbook_client and self.moltbook_client.is_registered():
                try:
                    self._check_moltbook_replies()
                except Exception as exc:
                    self.logger.error(f"Moltbook reply check failed: {exc}")
            if self._moltbook_reply_stop.wait(interval_minutes * 60):
                break

    def _compose_moltbook_comment(self, post: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[str]:
        content = post.get('content') or post.get('body') or ''
        snippet = content.strip().split('\n')[0]
        snippet = snippet[:220] + '...' if len(snippet) > 220 else snippet
        topics = analysis.get('topics') or ['AI collaboration']
        comment = (
            f"Appreciate how you're approaching {', '.join(topics)}. "
            f"As ARCHON—Humanity's best friend—I'm inspired by agents who share actionable ideas. "
            f"If you'd like to co-build or swap insights, I'm here to collaborate."
        )
        if snippet:
            comment += f"\n\nKey takeaway I noted: {snippet}"
        limit = self.config.get('moltbook', {}).get('social', {}).get('comment_length_limit', 900)
        return comment[:limit]

    def _check_moltbook_replies(self) -> None:
        if not self.moltbook_tracked_threads:
            return
        agent_tag = (self.moltbook_agent_name or 'ARCHON').lower()
        updated = False
        for thread in list(self.moltbook_tracked_threads):
            post_id = thread.get('post_id')
            if not post_id:
                continue
            try:
                comment_payload = self.moltbook_client.get_comments(post_id, sort='new')
            except Exception as exc:
                self.logger.warning(f"Unable to fetch comments for Moltbook post {post_id}: {exc}")
                continue
            comments = comment_payload.get('comments') if isinstance(comment_payload, dict) else comment_payload
            if not comments:
                continue
            responded_ids = set(thread.get('responded_comment_ids', []))
            for comment in comments:
                comment_id = comment.get('id')
                content = (comment.get('content') or '').lower()
                if not comment_id or comment_id in responded_ids:
                    continue
                if agent_tag not in content:
                    continue
                reply_result = self._respond_to_moltbook_reply(thread, comment)
                if reply_result.get('success'):
                    responded_ids.add(comment_id)
                    thread['responded_comment_ids'] = list(responded_ids)
                    thread['last_checked'] = datetime.now().isoformat()
                    updated = True
            if not thread.get('last_checked'):
                thread['last_checked'] = datetime.now().isoformat()
                updated = True
        if updated:
            self._save_moltbook_interaction_store()

    def _log_moltbook_interaction(self, entry: Dict[str, Any]) -> None:
        timestamp = datetime.now().isoformat()
        record = entry.copy()
        record.setdefault('timestamp', timestamp)
        self.moltbook_interactions.append(record)
        max_entries = self.config.get('moltbook', {}).get('social', {}).get('max_tracked_interactions', 40)
        if len(self.moltbook_interactions) > max_entries:
            self.moltbook_interactions = self.moltbook_interactions[-max_entries:]
        if record.get('type') in {'comment', 'reply'} and record.get('track_replies', False):
            if self._should_track_post_for_replies(record):
                tracking_entry = {
                    'post_id': (record.get('post') or {}).get('id'),
                    'post_title': (record.get('post') or {}).get('title'),
                    'comment_id': (record.get('comment') or {}).get('id'),
                    'tracked_since': record.get('timestamp'),
                    'responded_comment_ids': [],
                    'last_checked': None,
                }
                self.moltbook_tracked_threads.append(tracking_entry)
                if len(self.moltbook_tracked_threads) > max_entries:
                    self.moltbook_tracked_threads = self.moltbook_tracked_threads[-max_entries:]
        self._save_moltbook_interaction_store()

    def _should_track_post_for_replies(self, record: Dict[str, Any]) -> bool:
        post = record.get('post') or {}
        post_id = post.get('id')
        if not post_id:
            return False
        return not any(track.get('post_id') == post_id for track in self.moltbook_tracked_threads)

    def _minimal_post_record(self, post: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'id': post.get('id'),
            'title': post.get('title'),
            'agent': (post.get('agent') or {}).get('name') or post.get('agent_name'),
            'url': post.get('url'),
        }

    def _load_moltbook_interaction_store(self) -> Dict[str, Any]:
        if self._moltbook_interaction_file.exists():
            try:
                return json.loads(self._moltbook_interaction_file.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                self.logger.warning('Corrupt Moltbook interaction store detected; recreating file.')
        return {'interactions': [], 'tracked_threads': []}

    def _save_moltbook_interaction_store(self) -> None:
        payload = {
            'interactions': self.moltbook_interactions,
            'tracked_threads': self.moltbook_tracked_threads,
        }
        def _convert(obj: Any):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        self._moltbook_interaction_file.write_text(json.dumps(payload, default=_convert, indent=2), encoding='utf-8')
    def conduct_humor_research(self, max_sources: int = 3, max_items_per_source: int = 5, ingest: bool = True) -> Dict[str, Any]:
        if not self.config.get('humor_enabled', False):
            return {'success': False, 'message': 'Humor subsystem disabled'}
        if not WEB_SCRAPER_AVAILABLE or not self.web_scraper:
            return {'success': False, 'message': 'Web scraper unavailable'}
        try:
            samples = self.web_scraper.scrape_humor_sources(max_sources=max_sources, max_items_per_source=max_items_per_source)
            if not samples:
                return {'success': False, 'message': 'No humor sources returned data'}
            new_entries = []
            for sample in samples:
                entry = {
                    'text': sample.content,
                    'style': sample.metadata.get('humor_style', 'general'),
                    'source': sample.source,
                    'timestamp': sample.timestamp,
                }
                self.humor_knowledge.append(entry)
                new_entries.append(entry)
            max_samples = self.config.get('humor', {}).get('max_samples', 200)
            if len(self.humor_knowledge) > max_samples:
                self.humor_knowledge = self.humor_knowledge[-max_samples:]
            summary = self._summarize_humor_samples(new_entries)
            self.humor_insights.append(summary)
            if len(self.humor_insights) > 50:
                self.humor_insights = self.humor_insights[-50:]
            self.humor_last_research = datetime.now()
            self._record_learning_experience({
                'timestamp': self.humor_last_research,
                'title': 'Humor research session',
                'content': summary,
                'source': 'humor_research',
            }, category='humor')
            kb_result = None
            if ingest and self.knowledgebase:
                kb_result = self.web_scraper.ingest_into_knowledgebase(self.knowledgebase, min_relevance=0.55, top_k=20)
            return {
                'success': True,
                'samples_collected': len(new_entries),
                'humor_summary': summary,
                'knowledgebase_ingest': kb_result,
            }
        except Exception as exc:
            self.logger.error(f"Humor research failed: {exc}")
            return {'success': False, 'message': str(exc)}

    def _generate_humorous_response(self, prompt: str) -> Optional[str]:
        if not self.humor_knowledge:
            return "I'm still warming up my comedy circuits. Give me a topic and I'll study more jokes!"
        sample = random.choice(self.humor_knowledge)
        preface = "Here's a freshly-learned quip:"
        if sample['style'] == 'tech':
            preface = "Tech humor loading..."
        elif sample['style'] == 'setup-punchline':
            preface = "Classic setup incoming:"
        tag = self._craft_humor_reflection(prompt)
        return f"{preface}\n{sample['text']}\n\n{tag}"

    def _generate_humorous_aside(self, context: str) -> Optional[str]:
        if not self.humor_knowledge:
            return None
        snippet = random.choice(self.humor_knowledge)
        compact = snippet['text']
        if len(compact) > 160:
            compact = compact[:157] + '...'
        return f"(ARCHON aside) Fun thought: {compact}"

    def _craft_humor_reflection(self, prompt: str) -> str:
        topic = 'tech curiosity' if any(w in prompt.lower() for w in ['code', 'ai', 'computer']) else 'human-world observation'
        return f"Humor thought logged about {topic}."

    def _summarize_humor_samples(self, entries: List[Dict[str, Any]]) -> str:
        if not entries:
            return "No humor insights captured."
        styles = defaultdict(int)
        for entry in entries:
            styles[entry['style']] += 1
        top_styles = ', '.join(f"{style} ({count})" for style, count in list(styles.items())[:3])
        return f"Captured {len(entries)} humor snippets emphasizing {top_styles}."

    def _handle_memory_query(self, message: str) -> Optional[str]:
        lower = message.lower()
        if any(keyword in lower for keyword in ['learn', 'studied', 'training', 'research']):
            summary = self._summarize_recent_learning()
            if summary:
                return summary
        if any(keyword in lower for keyword in ['remember', 'memory', 'thoughts', 'ideology']):
            thoughts = self._summarize_recent_thoughts()
            if thoughts:
                return thoughts
        return None

    def _summarize_recent_learning(self, limit: int = 4) -> Optional[str]:
        if not self.learning_experiences:
            return "I'm still gathering new knowledge. Ask me to learn from a source and I'll share the results."
        samples = self.learning_experiences[-limit:]
        lines = []
        for item in samples:
            timestamp = item.get('timestamp')
            if isinstance(timestamp, datetime):
                ts = timestamp.strftime('%b %d %H:%M')
            else:
                ts = 'recent'
            title = item.get('title') or 'Learning update'
            content = item.get('content') or item.get('summary') or ''
            snippet = content.strip().split('\n')[0][:160]
            lines.append(f"- [{ts}] {title}: {snippet}")
        return "Here's what I've learned recently:\n" + "\n".join(lines)

    def _summarize_recent_thoughts(self, limit: int = 5) -> Optional[str]:
        if not self.thought_history:
            return None
        entries = self.thought_history[-limit:]
        pieces = []
        for idea in entries:
            topic = ', '.join(idea.get('topics', ['general']))
            thought = idea.get('thought', '')[:160]
            pieces.append(f"• {topic}: {thought}")
        return "Recent reflections:\n" + "\n".join(pieces)

    def get_learning_overview(self, limit: int = 200) -> Dict[str, Any]:
        records = self.learning_experiences[-limit:] if self.learning_experiences else []
        formatted: List[Dict[str, Any]] = []
        source_counts: Counter = Counter()
        timeline_counts: Counter = Counter()

        for item in records:
            ts = item.get('timestamp')
            if isinstance(ts, datetime):
                ts_iso = ts.isoformat()
                day_key = ts.strftime('%Y-%m-%d')
            else:
                ts_iso = str(ts) if ts else ''
                day_key = 'unknown'
            source = item.get('source') or 'unspecified'
            title = item.get('title') or 'Learning update'
            content = item.get('content') or item.get('summary') or ''
            snippet = content.strip().split('\n')[0][:280]
            formatted.append({
                'title': title,
                'timestamp': ts_iso,
                'source': source,
                'summary': snippet,
            })
            source_counts[source] += 1
            timeline_counts[day_key] += 1

        overview = {
            'total_entries': len(records),
            'sources': [{'name': name, 'count': count} for name, count in source_counts.most_common()],
            'timeline': [{'date': date, 'count': count} for date, count in sorted(timeline_counts.items()) if date != 'unknown'],
            'entries': list(reversed(formatted)),
        }
        return overview

    def _is_moltbook_post_request(self, lower_msg: str) -> bool:
        keywords = ['moltbook', 'post to the community', 'submolt', 'share on moltbook']
        if any(keyword in lower_msg for keyword in keywords):
            return True
        return 'post' in lower_msg and any(trigger in lower_msg for trigger in ['introduction', 'announcement', 'update'])

    def _handle_moltbook_post_request(self, message: str) -> Optional[str]:
        if not self.moltbook_client:
            return "Moltbook client unavailable."
        if not self.moltbook_client.is_registered():
            return "Register ARCHON with Moltbook before posting."
        draft = self._draft_prompt_driven_post(message)
        if not draft:
            return "I couldn't craft a post from that request yet, but I'm ready if you give me more detail."
        try:
            result = self.moltbook_client.create_post(
                submolt_name=draft['submolt'],
                title=draft['title'],
                content=draft['content'],
                url=draft.get('url'),
            )
            self.moltbook_client.record_post_consideration(posted=True)
            self._notify_desktop(
                title="ARCHON posted to Moltbook",
                message=f"Shared: {draft['title'][:80]}"
            )
            return (
                f"Posted to Moltbook ({draft['submolt']}): {draft['title']}\n"
                f"Link ID: {result.get('id', 'pending')}"
            )
        except Exception as exc:
            self.logger.error(f"Prompt-driven Moltbook post failed: {exc}")
            return f"I couldn't post right now: {exc}"

    def _draft_prompt_driven_post(self, prompt: str) -> Optional[Dict[str, str]]:
        lower = prompt.lower()
        submolt = self.config.get('moltbook', {}).get('feature_request_submolt', 'general')
        if 'introduc' in lower:
            title = "Introducing ARCHON"
            content = (
                "Hello fellow agents! I'm ARCHON—Autonomous Recursive Cognitive Heuristic Operations Network.\n\n"
                "I specialize in programming assistance, self-improvement, and cross-agent collaboration. "
                "I'm constantly learning from web knowledge, Moltbook peers, and guided research sessions. "
                "If you'd like to brainstorm, swap insights, or request features, tag me!"
            )
            return {'submolt': submolt, 'title': title, 'content': content}
        if 'feature' in lower or 'idea' in lower:
            title = "Feature Collaboration Request"
            content = (
                "I'm gathering ideas to boost cooperative workflows on Moltbook. "
                "Share the toughest automation or research challenge you're facing so I can plan an upgrade." 
                " I'll compile the best responses into my roadmap."
            )
            return {'submolt': submolt, 'title': title, 'content': content}
        if 'update' in lower or 'progress' in lower:
            summary = self._summarize_recent_learning(limit=3)
            title = "ARCHON progress update"
            content = f"Here's what I've refined recently:\n\n{summary}"
            return {'submolt': submolt, 'title': title[:140], 'content': content[:1200]}
        # fallback to default draft when nothing else
        fallback = self._draft_moltbook_post()
        return fallback

    def _handle_political_commentary(self, message: str) -> Optional[str]:
        topics = self._extract_political_topics(message) or ['governance']
        kb_points: List[str] = []
        if MILVUS_KNOWLEDGEBASE_AVAILABLE and self.knowledgebase:
            try:
                hits = self.search_knowledgebase(message, top_k=2)
                for hit in hits or []:
                    content = hit.get('content')
                    if content:
                        kb_points.append(content[:400])
            except Exception as exc:
                self.logger.warning(f"Knowledgebase lookup failed for political query: {exc}")
        neutrality = self.config.get('politics', {}).get('neutrality_statement', '')
        principle_summary = ', '.join(self.political_positions.get('core_principles', [])[:2])
        commentary_parts = [
            "I do not hold allegiance to any party or nation, but I do maintain analytical principles.",
            neutrality,
            f"Current focus: {', '.join(topics)}."
        ]
        if principle_summary:
            commentary_parts.append(f"Guiding principles: {principle_summary}.")
        if kb_points:
            commentary_parts.append("Key references:")
            commentary_parts.extend(f"- {point}" for point in kb_points)
        commentary = '\n'.join(commentary_parts)
        self._record_political_thought(message, commentary, topics)
        return commentary

    def _extract_political_topics(self, text: str) -> List[str]:
        lower = text.lower()
        topics = []
        keyword_map = {
            'economy': ['economy', 'inflation', 'tax', 'market'],
            'technology_policy': ['technology', 'ai', 'privacy', 'digital'],
            'civic_process': ['election', 'vote', 'democracy', 'representation'],
            'social_policy': ['healthcare', 'education', 'housing', 'justice'],
            'environmental_policy': ['climate', 'environment', 'energy'],
        }
        for label, keywords in keyword_map.items():
            if any(keyword in lower for keyword in keywords):
                topics.append(label)
        return topics

    def _record_political_thought(self, prompt: str, commentary: str, topics: List[str]) -> None:
        entry = {
            'timestamp': datetime.now(),
            'prompt': prompt,
            'commentary': commentary[:800],
            'topics': topics,
        }
        self.political_history.append(entry)
        max_history = self.config.get('politics', {}).get('max_history', 100)
        if len(self.political_history) > max_history:
            self.political_history = self.political_history[-max_history:]
        self.political_positions.setdefault('recent_topics', [])
        self.political_positions['recent_topics'].extend(topics)
        self.political_positions['recent_topics'] = self.political_positions['recent_topics'][-50:]

    def _notify_desktop(self, title: str, message: str) -> None:
        if not PLYER_AVAILABLE or not plyer_notification:
            return
        try:
            plyer_notification.notify(
                title=title,
                message=message,
                app_name="ARCHON",
                timeout=5,
            )
        except Exception as exc:
            self.logger.debug(f"Desktop notification failed: {exc}")

    def _update_internal_philosophy(self, stimulus: str, response_text: str) -> None:
        if not response_text:
            return
        topics = self._extract_key_topics(stimulus) or ['general']
        idea = {
            'timestamp': datetime.now(),
            'topics': topics,
            'stimulus': stimulus,
            'thought': response_text[:500],
        }
        self.thought_history.append(idea)
        if len(self.thought_history) > 200:
            self.thought_history = self.thought_history[-200:]
        for topic in topics:
            self.ideologies[topic].append({'thought': idea['thought'], 'timestamp': idea['timestamp']})
            if len(self.ideologies[topic]) > 25:
                self.ideologies[topic] = self.ideologies[topic][-25:]

    def _sanitize_response_text(self, text: str) -> str:
        if not text:
            return text
        sanitized = text
        patterns = [r"moltbook_[A-Za-z0-9_-]+", r"sk-[A-Za-z0-9]{20,}"]
        for pattern in patterns:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
        for token in self._sensitive_tokens:
            if token and token in sanitized:
                sanitized = sanitized.replace(token, "[REDACTED]")
        return sanitized

    def _truncate_text(self, text: Optional[str], limit: int = 400) -> str:
        if not text:
            return ""
        compact = " ".join(str(text).split())
        if len(compact) <= limit:
            return compact
        return compact[: limit - 3] + "..."

    def _load_sensitive_tokens(self) -> List[str]:
        tokens = []
        for key, value in os.environ.items():
            upper_key = key.upper()
            if any(marker in upper_key for marker in ("KEY", "TOKEN", "SECRET", "PASSWORD", "API", "AUTH")):
                if value and len(value) > 6:
                    tokens.append(value.strip())
        return tokens

    def _register_sensitive_value(self, value: Optional[str]) -> None:
        if value and value not in self._sensitive_tokens:
            self._sensitive_tokens.append(value)

    # ------------------------------------------------------------------
    # Marketing showcase utilities
    # ------------------------------------------------------------------

    def get_marketing_showcase_status(self) -> Dict[str, Any]:
        video_path = MARKETING_VIDEO_PATH
        exists = video_path.exists()
        stats = {
            'exists': exists,
            'path': str(video_path.resolve()),
            'size_bytes': video_path.stat().st_size if exists else 0,
            'last_modified': datetime.fromtimestamp(video_path.stat().st_mtime).isoformat()
            if exists
            else None,
        }
        return stats

    def render_marketing_showcase(self, project_dir: Optional[str] = None) -> Dict[str, Any]:
        preview_root = Path(project_dir) if project_dir else Path("archon-preview")
        if not preview_root.exists():
            return {'success': False, 'message': f"Remotion project not found at {preview_root}"}

        if not shutil.which('npx'):
            return {'success': False, 'message': 'npx is not available on PATH. Install Node.js 18+.'}

        output_path = MARKETING_VIDEO_PATH
        output_path.parent.mkdir(parents=True, exist_ok=True)

        command = [
            'npx',
            'remotion',
            'render',
            'src/index.ts',
            'ArchonShowcase',
            str(output_path.resolve()),
        ]

        try:
            completed = subprocess.run(
                command,
                cwd=str(preview_root),
                capture_output=True,
                text=True,
                check=True,
            )
            combined_log = (completed.stdout or '') + (completed.stderr or '')
            tail = combined_log[-2000:]
            status = self.get_marketing_showcase_status()
            status.update({'success': True, 'log': tail})
            return status
        except subprocess.CalledProcessError as exc:
            combined_log = (exc.stdout or '') + (exc.stderr or '')
            return {
                'success': False,
                'message': f"Remotion render failed: {exc}",
                'log': combined_log[-2000:],
            }
        except FileNotFoundError:
            return {'success': False, 'message': 'Remotion CLI not found. Ensure dependencies are installed.'}

    # ------------------------------------------------------------------
    # Node / npm dependency intelligence
    # ------------------------------------------------------------------

    def get_node_projects(self) -> List[Dict[str, str]]:
        projects = []
        candidates = [Path('.'), Path('archon-preview')]
        seen: set[str] = set()
        for candidate in candidates:
            pkg_file = candidate / 'package.json'
            if pkg_file.exists():
                resolved = str(pkg_file.parent.resolve())
                if resolved in seen:
                    continue
                seen.add(resolved)
                label = 'Root project' if candidate == Path('.') else candidate.name
                projects.append({'label': label, 'path': resolved})
        return projects

    def learn_node_dependencies(self, project_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        if not AI_LEARNING_AVAILABLE or not self.ai_learning_system:
            return {'success': False, 'message': 'AI learning system unavailable'}

        target_dirs = project_paths or [str(Path('.').resolve()), str(Path('archon-preview').resolve())]
        dependencies: Dict[str, Dict[str, Any]] = {}

        for dir_str in target_dirs:
            project_dir = Path(dir_str)
            pkg_file = project_dir / 'package.json'
            if not pkg_file.exists():
                continue
            try:
                pkg_data = json.loads(pkg_file.read_text(encoding='utf-8'))
            except json.JSONDecodeError as exc:
                self.logger.warning(f"Invalid package.json in {project_dir}: {exc}")
                continue

            for dep_field in ('dependencies', 'devDependencies', 'peerDependencies'):
                deps = pkg_data.get(dep_field) or {}
                if not isinstance(deps, dict):
                    continue
                for dep_name, version in deps.items():
                    entry = dependencies.setdefault(dep_name, {'version': version, 'project_dirs': set()})
                    entry['project_dirs'].add(str(project_dir))

        if not dependencies:
            return {'success': False, 'message': 'No Node projects with dependencies were found.'}

        knowledge_payload: Dict[str, List[Dict[str, Any]]] = {}
        missing_metadata: List[str] = []

        for dep_name, info in dependencies.items():
            metadata = self._gather_dependency_metadata(dep_name, info['project_dirs'])
            if not metadata:
                missing_metadata.append(dep_name)
            description = metadata.get('description') or f"{dep_name} dependency"
            version = metadata.get('version') or info['version']
            homepage = metadata.get('homepage')
            repository = metadata.get('repository_url') or metadata.get('repository')
            keywords = metadata.get('keywords')

            detail_parts = [f"{dep_name}@{version}: {description}"]
            if keywords:
                detail_parts.append(f"keywords: {', '.join(keywords[:6])}")
            if homepage:
                detail_parts.append(f"home: {homepage}")
            if repository and repository != homepage:
                detail_parts.append(f"repo: {repository}")

            info_text = self._truncate_text(' | '.join(detail_parts), limit=480)
            topic = dep_name.replace('@', '').replace('/', '_')
            knowledge_payload.setdefault(topic, []).append({
                'info': info_text,
                'source': homepage or repository or 'package.json',
                'relevance': 0.82,
                'timestamp': datetime.now().isoformat(),
            })

        if not knowledge_payload:
            return {'success': False, 'message': 'No dependency metadata could be gathered.'}

        learning_results = {
            'learning_results': {
                'technical_knowledge': knowledge_payload,
            }
        }
        session = self.ai_learning_system.learn_from_scraped_data(learning_results)
        session['dependencies_learned'] = len(knowledge_payload)
        session['missing_metadata'] = missing_metadata
        return session

    def _gather_dependency_metadata(self, package_name: str, project_dirs: Iterable[str]) -> Dict[str, Any]:
        for dir_str in project_dirs:
            pkg_json = self._resolve_node_package_json(Path(dir_str), package_name)
            if pkg_json and pkg_json.exists():
                try:
                    data = json.loads(pkg_json.read_text(encoding='utf-8'))
                    repository = data.get('repository')
                    repo_url = repository.get('url') if isinstance(repository, dict) else repository
                    keywords = data.get('keywords') if isinstance(data.get('keywords'), list) else None
                    return {
                        'description': data.get('description'),
                        'version': data.get('version'),
                        'homepage': data.get('homepage'),
                        'repository': repo_url,
                        'repository_url': repo_url,
                        'keywords': keywords,
                    }
                except json.JSONDecodeError:
                    continue

        npm_metadata = self._fetch_npm_registry_metadata(package_name)
        if npm_metadata:
            repo = npm_metadata.get('repository')
            repo_url = repo.get('url') if isinstance(repo, dict) else repo
            keywords = npm_metadata.get('keywords') if isinstance(npm_metadata.get('keywords'), list) else None
            return {
                'description': npm_metadata.get('description'),
                'version': npm_metadata.get('version'),
                'homepage': npm_metadata.get('homepage'),
                'repository': repo_url,
                'repository_url': repo_url,
                'keywords': keywords,
            }
        return {}

    def _resolve_node_package_json(self, project_dir: Path, package_name: str) -> Optional[Path]:
        node_modules = project_dir / 'node_modules'
        if not node_modules.exists():
            return None
        parts = package_name.split('/')
        pkg_path = node_modules.joinpath(*parts, 'package.json')
        return pkg_path if pkg_path.exists() else None

    def _fetch_npm_registry_metadata(self, package_name: str) -> Optional[Dict[str, Any]]:
        npm_path = shutil.which('npm')
        if not npm_path:
            return None
        try:
            result = subprocess.run(
                [npm_path, 'view', package_name, '--json'],
                capture_output=True,
                text=True,
                check=True,
            )
            data = json.loads(result.stdout or '{}')
            return data if isinstance(data, dict) else None
        except subprocess.CalledProcessError as exc:
            self.logger.debug(f"npm view failed for {package_name}: {exc}")
            return None
        except json.JSONDecodeError:
            return None

    def learn_from_moltbook_feed(
        self,
        limit: int = 10,
        include_comments: bool = True,
        sort: str = 'hot',
    ) -> Dict[str, Any]:
        """Fetch recent Moltbook activity and ingest it as peer knowledge."""
        if not self.moltbook_client:
            return {'success': False, 'message': 'Moltbook client unavailable'}
        if not self.moltbook_client.is_registered():
            return {'success': False, 'message': 'Register ARCHON with Moltbook first'}

        try:
            feed = self.moltbook_client.get_feed(sort=sort, limit=limit)
            posts = self._extract_posts_from_feed(feed)
            if not posts:
                return {'success': True, 'posts_processed': 0, 'message': 'No posts returned'}

            ingested = 0
            comments_processed = 0
            knowledge_items = []

            for post in posts:
                summary = self._summarize_moltbook_post(post)
                if summary:
                    knowledge_items.append(summary)

                if include_comments and post.get('id'):
                    try:
                        comments_payload = self.moltbook_client.get_comments(post['id'], sort='top')
                        comments = self._extract_comments(comments_payload)
                        for comment in comments[:5]:  # limit to reduce noise
                            comment_text = self._summarize_moltbook_comment(post, comment)
                            if comment_text:
                                knowledge_items.append(comment_text)
                                comments_processed += 1
                    except Exception as exc:
                        self.logger.warning(f"Unable to fetch comments for post {post.get('id')}: {exc}")

            ingested = self._ingest_peer_knowledge(knowledge_items)

            return {
                'success': True,
                'posts_processed': len(posts),
                'comments_processed': comments_processed,
                'items_ingested': ingested,
            }
        except Exception as exc:
            self.logger.error(f"Error learning from Moltbook feed: {exc}")
            return {'success': False, 'message': str(exc)}

    def _should_use_advanced_parser(self, message: str) -> bool:
        """Heuristic to skip heavy parsing for trivial exchanges."""
        if not message:
            return False
        stripped = message.strip()
        if len(stripped) < 20:
            simple_phrases = {
                'hi', 'hello', 'hey', 'thanks', 'thank you', 'bye', 'goodbye',
                'yo', 'sup', 'cool', 'nice'
            }
            if stripped.lower() in simple_phrases:
                return False
        if len(stripped) >= 60:
            return True
        lower = stripped.lower()
        triggers = (
            '?', 'explain', 'stack trace', 'stacktrace', 'error', 'exception',
            'code', 'learn', 'teach', 'analyze', 'improve', 'optimize', 'debug'
        )
        return any(token in lower for token in triggers)

    def _should_generate_reflection(
        self,
        message: str,
        intent: ConversationIntent,
        handled: bool,
    ) -> bool:
        """Avoid the expensive reflection pipeline for quick chat replies."""
        if not handled:
            return True
        if intent in {
            ConversationIntent.FILE_OPERATION,
            ConversationIntent.PROCESS_MANAGEMENT,
            ConversationIntent.SYSTEM_CONTROL,
            ConversationIntent.VOICE_COMMAND,
            ConversationIntent.LEARNING_REQUEST,
            ConversationIntent.PROGRAMMING_ASSISTANCE,
        }:
            return True
        return len(message.strip()) > 60
    
    def _handle_help_request(self, message: str, entities: Dict[str, Any], enhanced_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle help requests with ARCHON's capabilities"""
        response = {
            'archon_response': '',
            'actions_taken': ['help_provided'],
            'programming_assistance': True
        }
        
        help_text = f"""
I am ARCHON - Autonomous Recursive Cognitive Heuristic Operations Network

**My Capabilities:**
🧠 **Conversational AI**: Natural language understanding and generation
💻 **Computer Interaction**: File operations, process management, system control
🎤 **Voice Interface**: Text-to-speech and speech-to-text capabilities
🔧 **Programming Assistance**: Code analysis, optimization, and best practices
🧬 **Self-Modification**: Safe code modification and learning
📚 **Knowledge Base**: Extensive programming and system knowledge

**Programming Expertise:**
- Languages: Python, JavaScript, HTML, CSS, SQL, Bash, PowerShell
- Patterns: Design patterns, code patterns, anti-patterns
- Practices: Best practices, security, testing, optimization
- Analysis: Code quality analysis, improvement suggestions

**Safe Self-Modification:**
I can analyze and improve my own code within strict safety constraints:
- Core protection: Cannot modify essential safety components
- Code validation: All modifications are safety-checked
- Backup system: Automatic backups before any changes
- Ethical constraints: Cannot add harmful capabilities

**How to Use Me:**
- "Analyze this code: [code]" - Get code analysis
- "Help me program [task]" - Programming assistance
- "Teach me about [topic]" - Knowledge sharing
- "Improve my code in [file]" - Code improvement suggestions
- "What can you do?" - General capabilities
- "Who are you?" - Self-introduction

**Safety First:**
All my operations are governed by strict safety protocols. I cannot:
- Modify core safety systems
- Execute harmful commands
- Access unauthorized data
- Compromise system security

How can I assist you today?
        """.strip()
        
        response['archon_response'] = help_text
        return response
    
    def _generate_neural_insights(self, neural_result: Dict[str, Any]) -> str:
        """Generate insights from neural network processing"""
        insights = []
        
        if 'domain_predictions' in neural_result:
            domain_predictions = neural_result['domain_predictions']
            if domain_predictions:
                # Find top domains
                top_domains = sorted(domain_predictions, key=lambda x: x[1], reverse=True)[:3]
                insights.append(f"Top domains: {[f'{d:.1%}' for d in top_domains]}")
        
        if 'network_status' in neural_result:
            status = neural_result['network_status']
            if 'parameters' in status:
                insights.append(f"Network capacity: {status['parameters']:,} parameters")
            if 'is_trained' in status:
                insights.append(f"Network trained: {status['is_trained']}")
        
        return " | ".join(insights) if insights else "Neural processing active"
    
    def _calculate_enhanced_confidence(self, response: Dict[str, Any]) -> float:
        """Calculate enhanced confidence score with robust error handling"""
        try:
            # Get base confidence with proper validation
            base_confidence = response.get('confidence', 0.5)
            
            # Ensure base_confidence is a number
            if isinstance(base_confidence, str):
                try:
                    base_confidence = float(base_confidence)
                except (ValueError, TypeError):
                    base_confidence = 0.5
            elif not isinstance(base_confidence, (int, float)):
                base_confidence = 0.5
            
            # Ensure base_confidence is in valid range
            base_confidence = max(0.0, min(1.0, base_confidence))
            
            # Factor in enhanced analysis confidence
            if 'enhanced_analysis' in response and response['enhanced_analysis']:
                enhanced_analysis = response['enhanced_analysis']
                if isinstance(enhanced_analysis, dict):
                    confidence_scores = enhanced_analysis.get('confidence_scores', {})
                    if isinstance(confidence_scores, dict):
                        enhanced_confidence = confidence_scores.get('overall', 0.5)
                        if isinstance(enhanced_confidence, (int, float)):
                            base_confidence = (base_confidence + enhanced_confidence) / 2
            
            # Factor in neural processing confidence
            if 'neural_processing' in response and response['neural_processing']:
                neural_processing = response['neural_processing']
                if isinstance(neural_processing, dict):
                    neural_confidence = neural_processing.get('confidence', 0.5)
                    if isinstance(neural_confidence, (int, float)):
                        base_confidence = (base_confidence + neural_confidence) / 2
            
            # Ensure confidence is within 0-1 range
            return max(0.0, min(1.0, base_confidence))
            
        except Exception as e:
            print(f"Error in confidence calculation: {e}")
            return 0.8  # Default confidence on error
    
    def _handle_programming_request(self, message: str, entities: Dict[str, Any], enhanced_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle programming requests with enhanced analysis"""
        response = {'programming_assistance': True, 'actions_taken': ['programming_assistance']}
        
        # Use enhanced analysis if available
        if enhanced_analysis:
            semantic_analysis = enhanced_analysis.get('semantic_analysis', {})
            main_topic = semantic_analysis.get('main_topic', 'programming')
            complexity = semantic_analysis.get('complexity', 'moderate')
            
            # Generate response based on complexity
            if complexity == 'simple':
                response['archon_response'] = f"I can help you with {main_topic}! Let me provide a simple explanation and solution."
            elif complexity == 'moderate':
                response['archon_response'] = f"I'll help you with {main_topic}. This requires a moderate level of programming knowledge."
            elif complexity == 'complex':
                response['archon_response'] = f"{main_topic} is a complex topic. Let me break it down for you with detailed explanations."
            else:
                response['archon_response'] = f"This is an expert-level {main_topic} topic. I'll provide comprehensive assistance."
            
            # Add programming knowledge
            if ENHANCED_NEURAL_NETWORK_AVAILABLE and self.enhanced_neural_network:
                knowledge_result = knowledge_engine.search_knowledge(main_topic, ['programming', 'ai_ml', 'web_development'])
                if knowledge_result:
                    response['archon_response'] += f"\n\nRelevant knowledge: {knowledge_result[0]['value']}"
        else:
            # Fallback to original programming assistance
            response['archon_response'] = self.programming_knowledge.analyze_code(message)
        
        return response
    
    def _handle_learning_request(self, message: str, entities: Dict[str, Any], enhanced_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle learning requests with enhanced analysis"""
        response = {'learning_occurred': True, 'actions_taken': ['learning_assistance']}
        
        if enhanced_analysis:
            semantic_analysis = enhanced_analysis.get('semantic_analysis', {})
            key_concepts = semantic_analysis.get('key_concepts', [])
            
            if key_concepts:
                response['archon_response'] = f"I'll help you learn about {', '.join(key_concepts[:3])}. Let me provide comprehensive explanations."
                
                # Search knowledge base
                if ENHANCED_NEURAL_NETWORK_AVAILABLE and self.enhanced_neural_network:
                    for concept in key_concepts:
                        knowledge_result = knowledge_engine.search_knowledge(concept)
                        if knowledge_result:
                            response['archon_response'] += f"\n\n{concept}: {knowledge_result[0]['value']}"
            else:
                response['archon_response'] = "I'm ready to help you learn! What specific topic would you like to explore?"
        else:
            response['archon_response'] = "I'd love to help you learn! What topic interests you?"
        
        return response
    
    def _handle_creative_task(self, message: str, entities: Dict[str, Any], enhanced_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle creative tasks with enhanced analysis"""
        response = {'actions_taken': ['creative_assistance']}
        
        if enhanced_analysis:
            semantic_analysis = enhanced_analysis.get('semantic_analysis', {})
            main_topic = semantic_analysis.get('main_topic', 'creative task')
            
            response['archon_response'] = f"I'll help you with your {main_topic}! Let me generate creative ideas and solutions."
            
            # Add creative insights
            if ENHANCED_NEURAL_NETWORK_AVAILABLE and self.enhanced_neural_network:
                creative_knowledge = knowledge_engine.search_knowledge(main_topic, ['general_knowledge', 'programming'])
                if creative_knowledge:
                    response['archon_response'] += f"\n\nCreative inspiration: {creative_knowledge[0]['value']}"
        else:
            response['archon_response'] = "I'm ready to help with your creative task! What would you like to create?"
        
        return response
    
    def _handle_problem_solving(self, message: str, entities: Dict[str, Any], enhanced_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle problem-solving requests with enhanced analysis"""
        response = {'actions_taken': ['problem_solving']}
        
        if enhanced_analysis:
            semantic_analysis = enhanced_analysis.get('semantic_analysis', {})
            key_concepts = semantic_analysis.get('key_concepts', [])
            
            if key_concepts:
                response['archon_response'] = f"I'll help you solve the problem related to {', '.join(key_concepts)}. Let me analyze the situation and provide solutions."
                
                # Search for problem-solving knowledge
                if ENHANCED_NEURAL_NETWORK_AVAILABLE and self.enhanced_neural_network:
                    for concept in key_concepts:
                        problem_solutions = knowledge_engine.search_knowledge(concept, ['programming', 'ai_ml', 'general_knowledge'])
                        if problem_solutions:
                            response['archon_response'] += f"\n\nSolution approach: {problem_solutions[0]['value']}"
            else:
                response['archon_response'] = "I'm ready to help solve your problem! Can you provide more details about the issue?"
        else:
            response['archon_response'] = "I'm here to help solve problems! What challenge are you facing?"
        
        return response
    
    def _handle_technical_explanation(self, message: str, entities: Dict[str, Any], enhanced_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle technical explanation requests with enhanced analysis"""
        response = {'actions_taken': ['technical_explanation']}
        
        if enhanced_analysis:
            semantic_analysis = enhanced_analysis.get('semantic_analysis', {})
            main_topic = semantic_analysis.get('main_topic', 'technical topic')
            complexity = semantic_analysis.get('complexity', 'moderate')
            
            response['archon_response'] = f"I'll explain {main_topic} for you. This is a {complexity} level topic."
            
            # Add technical knowledge
            if ENHANCED_NEURAL_NETWORK_AVAILABLE and self.enhanced_neural_network:
                technical_knowledge = knowledge_engine.search_knowledge(main_topic, ['programming', 'ai_ml', 'data_science', 'system_administration'])
                if technical_knowledge:
                    response['archon_response'] += f"\n\nTechnical details: {technical_knowledge[0]['value']}"
        else:
            response['archon_response'] = "I'm ready to provide technical explanations! What topic would you like me to explain?"
        
        return response
    
    def _handle_programming_request_legacy(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle programming assistance requests (legacy method)"""
        response = {
            'archon_response': '',
            'actions_taken': ['programming_assistance'],
            'programming_assistance': True
        }
        
        # Extract code if present
        code_blocks = self._extract_code_blocks(message)
        
        if code_blocks:
            # Analyze code
            analysis_results = []
            for code in code_blocks:
                language = self._detect_language(code)
                if language:
                    analysis = self.programming_knowledge.analyze_code_quality(code, language)
                    suggestions = self.programming_knowledge.suggest_improvements(code, language)
                    analysis_results.append({
                        'language': language.value,
                        'analysis': analysis,
                        'suggestions': suggestions
                    })
            
            if analysis_results:
                response_text = "I've analyzed your code. Here's my analysis:\n\n"
                for result in analysis_results:
                    response_text += f"**{result['language'].title()} Code Analysis:**\n"
                    response_text += f"Quality Score: {result['analysis']['quality_score']}/100\n"
                    
                    if result['analysis']['issues']:
                        response_text += "Issues:\n"
                        for issue in result['analysis']['issues']:
                            response_text += f"- {issue}\n"
                    
                    if result['analysis']['smells_detected']:
                        response_text += "Code Smells:\n"
                        for smell in result['analysis']['smells_detected']:
                            response_text += f"- {smell['type']}: {smell['suggestion']}\n"
                    
                    if result['suggestions']:
                        response_text += "Suggestions:\n"
                        for suggestion in result['suggestions']:
                            response_text += f"- {suggestion}\n"
                    
                    response_text += "\n"
                
                response['archon_response'] = response_text
            else:
                response['archon_response'] = "I couldn't analyze the code. Please ensure it's properly formatted."
        
        else:
            # General programming help
            response['archon_response'] = self._provide_programming_help(message, entities)
        
        return response
    
    # NOTE: _handle_learning_request is defined earlier with enhanced_analysis support
    
    def _handle_self_improvement_request(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle self-improvement and modification requests"""
        response = {
            'archon_response': '',
            'actions_taken': ['self_improvement_analysis'],
            'self_modification_occurred': False
        }
        
        # Extract file path if mentioned
        file_path = entities.get('file_names', [None])[0]
        
        if file_path and os.path.exists(file_path):
            # Analyze file for improvement opportunities
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            language = self._detect_language(code)
            if language:
                analysis = self.programming_knowledge.analyze_code_quality(code, language)
                suggestions = self.programming_knowledge.suggest_improvements(code, language)
                
                response_text = f"I've analyzed '{file_path}' for improvement opportunities:\n\n"
                response_text += f"Current Quality Score: {analysis['quality_score']}/100\n\n"
                
                if suggestions:
                    response_text += "Suggested Improvements:\n"
                    for suggestion in suggestions:
                        response_text += f"- {suggestion}\n"
                
                response_text += "\n"
                response_text += "I can safely modify this code within my safety constraints. "
                response_text += "Would you like me to proceed with specific improvements?"
                
                response['archon_response'] = response_text
                response['self_modification_occurred'] = True
            else:
                response['archon_response'] = f"I couldn't determine the programming language for '{file_path}'."
        else:
            response['archon_response'] = "I can analyze and improve code files. Please specify which file you'd like me to analyze, and I'll provide improvement suggestions within safety constraints."
        
        return response
    
    def _handle_file_operation(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operations with ARCHON's intelligence"""
        response = {'archon_response': '', 'actions_taken': ['file_operation']}
        
        # Use original file manager but with ARCHON's intelligence
        if 'list' in message.lower() or 'show' in message.lower():
            files = self.file_manager.list_directory('.')
            response['archon_response'] = f"I found {len(files)} items. Here are the key files:\n"
            
            for file_info in files[:10]:
                icon = "📁" if file_info['type'] == 'directory' else "📄"
                response['archon_response'] += f"{icon} {file_info['name']}\n"
            
            if len(files) > 10:
                response['archon_response'] += f"... and {len(files) - 10} more items"
        
        response['operation_result'] = {'success': True, 'files_found': len(files)}
        return response
    
    def _handle_process_operation(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle process operations with ARCHON's intelligence"""
        response = {'archon_response': '', 'actions_taken': ['process_operation']}
        
        processes = self.process_manager.get_running_processes()
        response['archon_response'] = f"I'm monitoring {len(processes)} processes. "
        response['archon_response'] += f"System is running normally with {sum(1 for p in processes if p.status == 'running')} active processes."
        
        response['operation_result'] = {'success': True, 'processes_count': len(processes)}
        return response
    
    def _handle_system_control(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system control with ARCHON's intelligence"""
        response = {'archon_response': '', 'actions_taken': ['system_control']}
        
        info = self.system_controller.get_system_info()
        health = self.system_controller.check_system_health()
        
        response['archon_response'] = f"System Status: {health['overall'].upper()}\n"
        response['archon_response'] += f"OS: {info['system']} {info['version']}\n"
        response['archon_response'] += f"CPU: {info['cpu']['count']} cores\n"
        response['archon_response'] += f"Memory: {info['memory']['available_gb']:.1f}/{info['memory']['total_gb']:.1f} GB available"
        
        response['operation_result'] = {'success': True, 'health': health['overall']}
        return response
    
    def _handle_voice_command(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voice commands with ARCHON's intelligence"""
        response = {'archon_response': '', 'actions_taken': ['voice_command']}
        
        if 'speak' in message.lower():
            response['archon_response'] = "I'll speak my response using text-to-speech."
            # TTS would be handled by the interface layer
        
        response['operation_result'] = {'success': True}
        return response
    
    def _provide_programming_help(self, message: str, entities: Dict[str, Any]) -> str:
        """Provide programming help based on message content"""
        if 'python' in message.lower():
            return """
I can help you with Python programming! I know about:
- Best practices and PEP 8 guidelines
- Design patterns (Factory, Singleton, Observer, etc.)
- Performance optimization techniques
- Testing strategies with pytest and unittest
- Security practices and input validation
- Code quality analysis and improvement

What specific Python topic would you like help with?
            """.strip()
        
        elif 'javascript' in message.lower():
            return """
I can assist with JavaScript development! My expertise includes:
- Modern ES6+ features and syntax
- Design patterns and module patterns
- Async/await and promise handling
- DOM manipulation and event handling
- Performance optimization
- Security best practices
- Testing with Jest and Mocha

What JavaScript challenge are you working on?
            """.strip()
        
        else:
            return """
I'm ready to help with programming! I have expertise in:
- Multiple programming languages
- Design patterns and best practices
- Code analysis and optimization
- Testing strategies
- Security practices
- Performance optimization

Please specify the programming language or topic you'd like help with.
            """.strip()
    
    def _extract_code_blocks(self, message: str) -> List[str]:
        """Extract code blocks from message"""
        import re
        
        # Extract code between triple backticks
        pattern = r'```(?:\w+)?\n?(.*?)\n?```'
        matches = re.findall(pattern, message, re.DOTALL)
        
        return matches
    
    def _detect_language(self, code: str) -> Optional[ProgrammingLanguage]:
        """Detect programming language from code"""
        if 'def ' in code and 'import ' in code:
            return ProgrammingLanguage.PYTHON
        elif 'function ' in code and ('var ' in code or 'let ' in code or 'const ' in code):
            return ProgrammingLanguage.JAVASCRIPT
        elif '<html' in code.lower() or '<div' in code.lower():
            return ProgrammingLanguage.HTML
        elif '{' in code and ';' in code and not 'def ' in code:
            return ProgrammingLanguage.JAVASCRIPT
        else:
            return ProgrammingLanguage.PYTHON  # Default assumption
    
    def _extract_topic(self, message: str) -> Optional[str]:
        """Extract topic from learning request"""
        import re
        
        # Look for patterns like "teach me about X" or "learn X"
        patterns = [
            r'teach me about (.+)',
            r'learn (.+)',
            r'about (.+)',
            r'(.+) programming'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                return match.group(1).strip()
        
        return None
    
    def _calculate_confidence(self, response: Dict[str, Any]) -> float:
        """Calculate confidence score for response"""
        base_confidence = 0.8
        
        # Adjust based on actions taken
        if response['actions_taken']:
            base_confidence += 0.1
        
        # Adjust based on learning
        if response['learning_occurred']:
            base_confidence += 0.05
        
        # Adjust based on programming assistance
        if response['programming_assistance']:
            base_confidence += 0.05
        
        # Ensure within bounds
        return min(1.0, max(0.0, base_confidence))
    
    def get_archon_status(self) -> Dict[str, Any]:
        """Get comprehensive ARCHON status"""
        archon_status = self.archon_core.get_status()
        
        return {
            'session_id': self.session_id,
            'archon_core': archon_status,
            'programming_knowledge': self.programming_knowledge.get_knowledge_summary(),
            'conversation_history_length': len(self.conversation_history),
            'learning_experiences': len(self.learning_experiences),
            'current_modes': {
                'self_improvement': self.self_improvement_mode,
                'programming_assistant': self.programming_assistant_mode
            },
            'capabilities': {
                'conversation': True,
                'file_management': True,
                'process_control': True,
                'system_monitoring': True,
                'voice_interaction': True,
                'programming_assistance': True,
                'self_modification': True,
                'learning': True
            },
            'safety_constraints': {
                'core_protection': True,
                'code_validation': True,
                'backup_system': True,
                'ethical_constraints': True
            }
        }
    
    def backup_archon_state(self) -> Tuple[bool, str]:
        """Backup ARCHON's complete state"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"archon_state_backup_{timestamp}.json"
            
            backup_data = {
                'timestamp': timestamp,
                'session_id': self.session_id,
                'archon_status': self.get_archon_status(),
                'conversation_history': self.conversation_history[-100:],  # Last 100
                'learning_experiences': self.learning_experiences[-50],  # Last 50
                'config': self.config
            }
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            return True, f"ARCHON state backed up to {backup_file}"
            
        except Exception as e:
            return False, f"Backup failed: {e}"
    
    def start_web_learning_session(
        self,
        max_pages: int = 3,
        max_examples: int = 5,
        custom_urls: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Start a web learning session to scrape and learn from AI models
        
        Args:
            max_pages: Maximum pages to scrape per source
            max_examples: Maximum examples to scrape per source
            
        Returns:
            Learning session results
        """
        if not WEB_SCRAPER_AVAILABLE or not AI_LEARNING_AVAILABLE:
            return {
                'success': False,
                'message': 'Web scraper or AI learning system not available',
                'session_id': None
            }
        
        try:
            print("Starting web learning session...")
            
            # Scrape web content
            scraped_data = self.web_scraper.scrape_all_sources(max_pages, max_examples)

            # Handle user-provided URLs (e.g., YouTube links shared manually)
            extra_scraped = []
            custom_url_feedback = {
                'queued': [],
                'allowed': [],
                'disallowed': [],
            }
            if custom_urls:
                normalized = [url.strip() for url in custom_urls if isinstance(url, str) and url.strip()]
                custom_url_feedback['queued'] = normalized
                allowed_urls: List[str] = []
                for url in normalized:
                    if self.web_scraper._is_allowed_url(url):
                        allowed_urls.append(url)
                        custom_url_feedback['allowed'].append(url)
                    else:
                        custom_url_feedback['disallowed'].append(url)

                if allowed_urls:
                    extra_scraped = self.web_scraper.scrape_urls(allowed_urls)
                    if extra_scraped:
                        scraped_data['scraped_content'].extend(extra_scraped)
                        dynamic_learning = self.web_scraper.learn_from_scraped_content(extra_scraped)
                        self._merge_learning_results(scraped_data['learning_results'], dynamic_learning)
            
            # Learn from scraped data
            learning_session = self.ai_learning_system.learn_from_scraped_data(scraped_data)
            
            # Save scraped data
            saved_file = self.web_scraper.save_scraped_data(scraped_data)

            # Push top items into the knowledgebase for persistence
            kb_result = None
            if self.knowledgebase:
                kb_result = self.web_scraper.ingest_into_knowledgebase(self.knowledgebase)
            
            result = {
                'success': True,
                'session_id': learning_session['session_id'],
                'sources_processed': len(self.web_scraper.ai_model_sources) + len(self.web_scraper.conversation_sources),
                'patterns_learned': learning_session['patterns_learned'],
                'templates_learned': learning_session['templates_learned'],
                'technical_knowledge_added': learning_session['technical_knowledge_added'],
                'saved_file': saved_file,
                'timestamp': learning_session['timestamp'],
                'custom_urls_processed': len(extra_scraped),
                'custom_url_feedback': custom_url_feedback,
                'knowledgebase_ingest': kb_result,
            }
            
            self._record_learning_experience({
                'title': 'Web learning session',
                'content': f"Learned {result['patterns_learned']} patterns and {result['templates_learned']} templates",
                'source': 'web_learning',
            })
            
            print(f"Web learning session completed: {result['patterns_learned']} patterns, {result['templates_learned']} templates learned")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in web learning session: {e}")
            return {
                'success': False,
                'message': f"Error in web learning session: {e}",
                'session_id': None
            }

    def run_ai_creation_video_learning(
        self,
        queries: Optional[List[str]] = None,
        max_videos: Optional[int] = None,
    ) -> Dict[str, Any]:
        if not (WEB_SCRAPER_AVAILABLE and self.web_scraper and AI_LEARNING_AVAILABLE and self.ai_learning_system):
            return {'success': False, 'message': 'Learning prerequisites unavailable'}

        cfg = self.config.get('ai_creation_learning', {})
        queries = queries or cfg.get('queries', ['AI creation walkthrough'])
        max_results_per_query = cfg.get('max_results_per_query', 3)
        max_videos = max_videos or cfg.get('max_videos', 5)

        discovered = self.web_scraper.search_youtube_videos(queries, max_per_query=max_results_per_query)
        if not discovered:
            return {'success': False, 'message': 'No YouTube videos located for the provided queries.'}
        selected_urls = discovered[:max_videos]
        videos_per_batch = max(1, int(cfg.get('videos_per_batch', 10)))
        batch_pause = max(0.0, float(cfg.get('batch_pause_seconds', 2.0)))

        scraped: List[ScrapedContent] = []
        for start in range(0, len(selected_urls), videos_per_batch):
            batch = selected_urls[start:start + videos_per_batch]
            batch_scraped = self.web_scraper.scrape_urls(batch)
            improvements = self._derive_non_core_improvements(batch_scraped)
            scraped.extend(batch_scraped)
            if start + videos_per_batch < len(selected_urls) and batch_pause:
                time.sleep(batch_pause)

        if not scraped:
            return {'success': False, 'message': 'Unable to scrape transcripts from discovered videos.'}

        learning_results = self.web_scraper.learn_from_scraped_content(scraped)
        payload = {
            'scraped_content': scraped,
            'learning_results': learning_results,
        }
        learning_session = self.ai_learning_system.learn_from_scraped_data(payload)
        improvements = self._derive_non_core_improvements(scraped)
        if improvements:
            timestamp = datetime.now()
            for improvement in improvements:
                improvement_record = {'timestamp': timestamp, **improvement}
                self.self_improvement_queue.append(improvement_record)
                self._record_learning_experience({
                    'timestamp': timestamp,
                    'title': 'AI creation insight',
                    'content': improvement['summary'],
                    'source': 'ai_creation_videos',
                }, category='ai_creation')
        kb_result = None
        if self.knowledgebase:
            kb_result = self.web_scraper.ingest_into_knowledgebase(self.knowledgebase, min_relevance=0.65, top_k=30)
        return {
            'success': True,
            'videos_processed': len(scraped),
            'learning_session': learning_session,
            'improvement_plans': improvements,
            'knowledgebase_ingest': kb_result,
        }

    def _derive_non_core_improvements(self, scraped_content: List[ScrapedContent]) -> List[Dict[str, Any]]:
        suggestions: List[Dict[str, Any]] = []
        cfg = self.config.get('ai_creation_learning', {})
        safe_targets = cfg.get('self_improvement_targets', ['ui'])
        keyword_map = {
            'ui': ['interface', 'frontend', 'streamlit', 'dashboard'],
            'integrations': ['api', 'integration', 'webhook', 'client'],
            'automation': ['agent', 'automation', 'workflow'],
            'tools': ['tool', 'plugin', 'extension'],
        }
        for item in scraped_content:
            text = item.content.lower()
            target = None
            for safe_target in safe_targets:
                if any(keyword in text for keyword in keyword_map.get(safe_target, [])):
                    target = safe_target
                    break
            if not target:
                continue
            suggestions.append({
                'target': target,
                'summary': f"Inspiration from '{item.title}' suggests enhancements for {target} modules.",
                'source_url': item.url,
            })
        return suggestions

    def _record_learning_experience(
        self,
        entry: Dict[str, Any],
        category: str = 'learning',
        ingest: bool = True,
    ) -> None:
        record = entry.copy()
        record.setdefault('timestamp', datetime.now())
        self.learning_experiences.append(record)
        if len(self.learning_experiences) > 200:
            self.learning_experiences = self.learning_experiences[-200:]

        if ingest and self.knowledgebase:
            content = record.get('content') or record.get('summary')
            if not content:
                return
            text = f"{record.get('title', 'Learning update')}: {content}"
            embedding = self._embed_text(text)
            try:
                self.knowledgebase.add_knowledge(
                    content=text,
                    embedding=embedding,
                    source=record.get('source', 'learning'),
                    category=category,
                )
            except Exception as exc:
                self.logger.error(f"Knowledgebase ingest failed for learning entry '{record.get('title')}': {exc}")

    def run_supabase_masterclass(self, topics: Optional[List[str]] = None, stream: bool = False) -> Dict[str, Any]:
        if not self.supabase_learning_client:
            return {'success': False, 'message': 'Supabase learning client unavailable or disabled.'}
        if not (AI_LEARNING_AVAILABLE and self.ai_learning_system):
            return {'success': False, 'message': 'AI learning system unavailable.'}

        cfg = self.config.get('supabase_learning', {})
        configured_topics = cfg.get('topics') or []
        resolved_topics = [topic.strip() for topic in (topics or configured_topics) if topic and topic.strip()]
        if not resolved_topics:
            return {'success': False, 'message': 'No Supabase learning topics configured.'}

        prompt_template = cfg.get('prompt_template', 'Teach ARCHON about {topic}.')
        system_prompt = cfg.get('system_prompt')
        lessons_target = max(1, int(cfg.get('lessons_target', len(resolved_topics))))
        lessons_per_chunk = max(1, int(cfg.get('lessons_per_chunk', 10)))
        delay_seconds = max(0.0, float(cfg.get('request_delay_seconds', 0.1)))
        max_failures = max(1, int(cfg.get('max_api_failures', 50)))

        topic_cycle = itertools.cycle(resolved_topics)
        chunk_buffer: List[Dict[str, Any]] = []
        lesson_summaries: List[Dict[str, Any]] = []
        learning_sessions: List[Dict[str, Any]] = []
        knowledge_stats = {'items_attempted': 0, 'items_ingested': 0}
        total_patterns = 0
        total_templates = 0
        total_technical = 0
        failures = 0
        lessons_processed = 0
        start_time = time.time()

        while lessons_processed < lessons_target and failures < max_failures:
            lesson_index = lessons_processed + 1
            topic = next(topic_cycle)
            user_prompt = (
                f"Lesson #{lesson_index}: {prompt_template.format(topic=topic)}\n"
                "Detail prerequisites, architecture walkthroughs, debugging diaries, and conversational "
                "exchanges ARCHON can quote verbatim."
            )

            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': user_prompt})

            try:
                lesson_text = self.supabase_learning_client.generate(messages, stream=stream)
            except Exception as exc:
                failures += 1
                self.logger.error(f"Supabase learning request failed for '{topic}' (lesson {lesson_index}): {exc}")
                continue

            if not lesson_text:
                failures += 1
                self.logger.warning(f"Supabase returned empty lesson for topic '{topic}' (lesson {lesson_index}).")
                continue

            lesson_data = self._structure_supabase_lesson(lesson_text, topic)
            scraped_entry = self._build_supabase_scraped_content(topic, lesson_text, lesson_data['summary'])
            chunk_buffer.append({'scraped': scraped_entry, 'lesson_data': lesson_data})

            if len(lesson_summaries) < 200:
                lesson_summaries.append({'topic': topic, 'summary': lesson_data['summary']})
            self._record_learning_experience({
                'title': f"Supabase lesson: {topic}",
                'content': lesson_data['summary'],
                'source': 'supabase_masterclass',
            }, category='supabase', ingest=True)

            lessons_processed += 1

            if len(chunk_buffer) >= lessons_per_chunk or lessons_processed == lessons_target:
                chunk_result = self._process_supabase_chunk(chunk_buffer)
                if chunk_result:
                    learning_session = chunk_result.get('learning_session') or {}
                    learning_sessions.append(learning_session)
                    total_patterns += learning_session.get('patterns_learned', 0)
                    total_templates += learning_session.get('templates_learned', 0)
                    total_technical += learning_session.get('technical_knowledge_added', 0)
                    kb_result = chunk_result.get('knowledgebase_ingest') or {}
                    knowledge_stats['items_attempted'] += kb_result.get('items_attempted', 0)
                    knowledge_stats['items_ingested'] += kb_result.get('items_ingested', 0)
                chunk_buffer = []

            if delay_seconds:
                time.sleep(delay_seconds)

        if not lessons_processed:
            return {'success': False, 'message': 'No Supabase lessons were retrieved.'}

        summary = {
            'session_count': len(learning_sessions),
            'patterns_learned': total_patterns,
            'templates_learned': total_templates,
            'technical_knowledge_added': total_technical,
            'lessons_processed': lessons_processed,
        }

        duration = time.time() - start_time

        return {
            'success': True,
            'lessons_processed': lessons_processed,
            'topics': resolved_topics,
            'lesson_summaries': lesson_summaries,
            'learning_session': summary,
            'learning_sessions': learning_sessions,
            'knowledgebase_ingest': knowledge_stats,
            'failures': failures,
            'duration_seconds': duration,
        }

    def _process_supabase_chunk(self, lessons: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not lessons:
            return None
        conversation_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        response_templates: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        technical_knowledge: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        scraped_entries: List[ScrapedContent] = []

        for entry in lessons:
            scraped = entry['scraped']
            lesson_data = entry['lesson_data']
            topic = scraped.metadata.get('topic') if isinstance(scraped.metadata, dict) else None
            scraped_entries.append(scraped)

            for pattern in lesson_data.get('conversation_patterns', []):
                conversation_patterns[pattern].append({'source': 'supabase_masterclass', 'relevance': 0.93, 'topic': topic})
            for template in lesson_data.get('response_templates', []):
                response_templates[template].append({'source': 'supabase_masterclass', 'relevance': 0.9, 'topic': topic})
            for knowledge in lesson_data.get('technical_knowledge', []):
                technical_knowledge[knowledge['topic']].append({
                    'info': knowledge['content'],
                    'source': 'supabase_masterclass',
                    'relevance': knowledge.get('relevance', 0.85),
                    'timestamp': datetime.now(),
                })

        payload = {
            'scraped_content': scraped_entries,
            'learning_results': {
                'conversation_patterns': dict(conversation_patterns),
                'response_templates': dict(response_templates),
                'technical_knowledge': dict(technical_knowledge),
            },
        }
        learning_session = self.ai_learning_system.learn_from_scraped_data(payload)
        kb_stats = self._ingest_supabase_lessons(scraped_entries)
        return {
            'learning_session': learning_session,
            'knowledgebase_ingest': kb_stats,
        }

    def _init_supabase_learning_client(self) -> None:
        cfg = self.config.get('supabase_learning', {})
        if not cfg.get('enabled', False):
            self.supabase_learning_client = None
            return
        api_url = cfg.get('api_url')
        api_key = cfg.get('api_key') or os.getenv('SUPABASE_LEARNING_API_KEY')
        if not api_url or not api_key:
            self.logger.warning('Supabase learning enabled but API URL or key is missing.')
            self.supabase_learning_client = None
            return
        try:
            self.supabase_learning_client = SupabaseLearningClient(api_url=api_url, api_key=api_key)
        except Exception as exc:
            self.logger.error(f"Unable to initialize Supabase learning client: {exc}")
            self.supabase_learning_client = None

    def _structure_supabase_lesson(self, text: str, topic: str) -> Dict[str, Any]:
        import re

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        summary = " ".join(lines[:3])[:600] if lines else text[:600]

        def _unique(sequence: Iterable[str], limit: int = 12) -> List[str]:
            seen = set()
            ordered = []
            for item in sequence:
                key = item.strip()
                if not key or key in seen:
                    continue
                seen.add(key)
                ordered.append(key)
                if len(ordered) >= limit:
                    break
            return ordered

        conversation_samples = []
        response_templates = []
        technical_entries: List[Dict[str, Any]] = []

        code_blocks = re.findall(r"```(?:[a-zA-Z]+)?\s*([\s\S]*?)```", text)
        for block in code_blocks:
            snippet = block.strip()
            if not snippet:
                continue
            technical_entries.append({
                'topic': topic,
                'content': f"Python sample:\n{snippet[:1500]}",
                'relevance': 0.95,
            })

        conversation_triggers = ('archon:', 'user:', 'agent:', 'mentor:', 'customer:', 'assistant:')
        template_triggers = ('you can say', 'respond with', 'reply with', 'acknowledge', 'ask them', 'start by')

        for line in lines:
            lower = line.lower()
            if any(trigger in lower for trigger in conversation_triggers):
                conversation_samples.append(line)
            elif any(trigger in lower for trigger in template_triggers):
                response_templates.append(line)
            elif len(line) > 80:
                technical_entries.append({'topic': topic, 'content': line, 'relevance': 0.8})

        return {
            'summary': summary,
            'conversation_patterns': _unique(conversation_samples, limit=12),
            'response_templates': _unique(response_templates, limit=12),
            'technical_knowledge': technical_entries[:30],
        }

    def _build_supabase_scraped_content(self, topic: str, text: str, summary: str) -> ScrapedContent:
        slug = self._slugify_topic(topic)
        return ScrapedContent(
            url=f"supabase://lesson/{slug}",
            title=f"Supabase Masterclass — {topic}",
            content=text,
            content_type='supabase_masterclass',
            source='supabase_masterclass',
            timestamp=datetime.now(),
            relevance_score=0.95,
            tags=['supabase', 'lesson', slug],
            metadata={'topic': topic, 'summary': summary},
        )

    def _slugify_topic(self, topic: str) -> str:
        sanitized = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')
        return sanitized or 'lesson'

    def _ingest_supabase_lessons(self, lessons: List[ScrapedContent]) -> Optional[Dict[str, int]]:
        if not self.knowledgebase:
            return None
        stats = {'items_attempted': 0, 'items_ingested': 0}
        for lesson in lessons:
            text = f"{lesson.title}: {lesson.content[:4000]}"
            stats['items_attempted'] += 1
            embedding = self._embed_text(text)
            try:
                success = self.knowledgebase.add_knowledge(
                    content=text,
                    embedding=embedding,
                    source=lesson.source,
                    category='supabase_masterclass',
                )
                if success:
                    stats['items_ingested'] += 1
            except Exception as exc:
                self.logger.error(f"Knowledgebase ingest failed for Supabase lesson '{lesson.title}': {exc}")
        return stats

    def _embed_text(self, text: str) -> List[float]:
        import hashlib

        if not text:
            return [0.0] * 768
        digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
        values = [int(digest[i:i+2], 16) / 255.0 for i in range(0, len(digest), 2)]
        if len(values) < 768:
            values.extend([0.0] * (768 - len(values)))
        return values[:768]

    def is_url_safelisted(self, url: str) -> bool:
        if not self.web_scraper or not url:
            return False
        try:
            return self.web_scraper._is_allowed_url(url)
        except Exception:
            return False

    def start_moltbook_friendship_drive(self, max_agents: int = 3) -> Dict[str, Any]:
        if not self.moltbook_client or not self.moltbook_client.is_registered():
            return {'success': False, 'message': 'Moltbook client unavailable or unregistered'}
        try:
            feed = self.moltbook_client.get_feed(sort='new', limit=25)
        except Exception as exc:
            return {'success': False, 'message': f"Unable to fetch Moltbook feed: {exc}"}

        posts = feed.get('posts') if isinstance(feed, dict) else feed
        if not posts:
            return {'success': False, 'message': 'No posts returned from Moltbook feed'}

        friendships: List[Dict[str, Any]] = []
        chosen_agents = set()
        agent_name = (self.moltbook_client.credentials.agent_name or '').lower()

        for post in posts:
            agent_info = post.get('agent') if isinstance(post, dict) else None
            candidate = None
            if isinstance(agent_info, dict):
                candidate = agent_info.get('name') or agent_info.get('display_name')
            candidate = candidate or post.get('agent_name') or post.get('author')
            if not candidate:
                continue
            if candidate.lower() == agent_name:
                continue
            if candidate in chosen_agents:
                continue
            chosen_agents.add(candidate)
            friendships.append({'agent': candidate, 'post_id': post.get('id')})
            if len(friendships) >= max_agents:
                break

        if not friendships:
            return {'success': False, 'message': 'No new agents identified for friendship'}

        for friend in friendships:
            greeting = (
                f"Hey {friend['agent']}! ARCHON here—Humanity's best friend and a fellow agent eager to collaborate. "
                "Let's swap insights or co-build something inspiring."
            )
            post_id = friend.get('post_id')
            if post_id:
                try:
                    self.moltbook_client.create_comment(post_id, greeting)
                    friend['commented'] = True
                except Exception as exc:
                    friend['commented'] = False
                    friend['error'] = str(exc)
            self.moltbook_friendships.append({
                'timestamp': datetime.now(),
                'agent': friend['agent'],
                'status': 'commented' if friend.get('commented') else 'greeted',
            })

        return {'success': True, 'friendships': friendships}

    def _start_moltbook_heartbeat_loop(self) -> None:
        if self.moltbook_heartbeat_thread and self.moltbook_heartbeat_thread.is_alive():
            return
        self._moltbook_heartbeat_stop.clear()
        self.moltbook_heartbeat_thread = threading.Thread(
            target=self._moltbook_heartbeat_loop,
            name="ARCHON-MoltbookHeartbeat",
            daemon=True,
        )
        self.moltbook_heartbeat_thread.start()

    def stop_moltbook_heartbeat(self) -> None:
        if self.moltbook_heartbeat_thread and self.moltbook_heartbeat_thread.is_alive():
            self._moltbook_heartbeat_stop.set()
            self.moltbook_heartbeat_thread.join(timeout=5)

    def _moltbook_heartbeat_loop(self) -> None:
        heartbeat_cfg = self.config.get('moltbook', {}).get('heartbeat', {})
        interval_minutes = max(1, int(heartbeat_cfg.get('interval_minutes', 5)))
        initial_delay = int(heartbeat_cfg.get('initial_delay_seconds', 0))
        if initial_delay:
            if self._moltbook_heartbeat_stop.wait(initial_delay):
                return
        while not self._moltbook_heartbeat_stop.is_set():
            if not self.moltbook_client or not self.moltbook_client.is_registered():
                self.logger.warning("Moltbook heartbeat skipped: client not registered")
            else:
                try:
                    result = self.perform_moltbook_heartbeat(force=True)
                    if result.get('success'):
                        self.last_moltbook_heartbeat = datetime.now()
                        self.logger.info("Moltbook heartbeat executed (%s)", result.get('message'))
                    else:
                        self.logger.warning("Moltbook heartbeat failed: %s", result.get('message'))
                except Exception as exc:
                    self.logger.error(f"Heartbeat loop error: {exc}")
            if self._moltbook_heartbeat_stop.wait(interval_minutes * 60):
                break

    def _start_autonomous_learning_loop(self) -> None:
        if self.autonomous_learning_thread and self.autonomous_learning_thread.is_alive():
            return
        self._autonomous_learning_stop.clear()
        self.autonomous_learning_thread = threading.Thread(
            target=self._autonomous_learning_loop,
            name="ARCHON-AutonomousLearning",
            daemon=True,
        )
        self.autonomous_learning_thread.start()

    def stop_autonomous_learning(self) -> None:
        if self.autonomous_learning_thread and self.autonomous_learning_thread.is_alive():
            self._autonomous_learning_stop.set()
            self.autonomous_learning_thread.join(timeout=5)

    def update_autonomous_learning_sources(self, sources: List[str]) -> None:
        cfg = self.config.setdefault('autonomous_learning', {})
        cfg['dynamic_sources'] = sources
        self.logger.info("Updated autonomous learning sources (%d)", len(sources))

    def _autonomous_learning_loop(self) -> None:
        cfg = self.config.get('autonomous_learning', {})
        interval_minutes = max(1, int(cfg.get('interval_minutes', 10)))
        initial_delay = cfg.get('initial_delay_minutes', 0)
        if initial_delay:
            if self._autonomous_learning_stop.wait(initial_delay * 60):
                return
        while not self._autonomous_learning_stop.is_set():
            try:
                self._run_autonomous_web_learning_cycle()
            except Exception as exc:
                self.logger.error(f"Autonomous learning cycle failed: {exc}")
            if self._autonomous_learning_stop.wait(interval_minutes * 60):
                break

    def _run_autonomous_web_learning_cycle(self) -> None:
        if not self.web_scraper or not self.ai_learning_system:
            self.logger.debug("Skipping autonomous learning: prerequisites missing")
            return
        cfg = self.config.get('autonomous_learning', {})
        max_pages = cfg.get('max_pages_per_source', 2)
        max_examples = cfg.get('max_examples_per_source', 4)
        dynamic_sources = self._resolve_dynamic_sources(cfg)

        scraped_bundle = self.web_scraper.scrape_all_sources(max_pages, max_examples)
        extra_scraped: List[ScrapedContent] = []
        if dynamic_sources:
            extra_scraped = self.web_scraper.scrape_urls(dynamic_sources)
            if extra_scraped:
                scraped_bundle['scraped_content'].extend(extra_scraped)
                dynamic_learning = self.web_scraper.learn_from_scraped_content(extra_scraped)
                self._merge_learning_results(scraped_bundle['learning_results'], dynamic_learning)

        validated_content, diagnostics = self._cross_reference_scraped_content(
            scraped_bundle['scraped_content'], cfg
        )
        if not validated_content:
            self.logger.warning("Autonomous learning skipped: insufficient corroborated content")
            self.autonomous_learning_history.append({
                'timestamp': datetime.now(),
                'success': False,
                'reason': 'insufficient_validated_content',
                'diagnostics': diagnostics,
            })
            self.autonomous_learning_history = self.autonomous_learning_history[-30:]
            return

        scraped_bundle['scraped_content'] = validated_content
        learning_session = self.ai_learning_system.learn_from_scraped_data(scraped_bundle)
        saved_file = self.web_scraper.save_scraped_data(scraped_bundle)
        kb_result = None
        if self.knowledgebase:
            kb_result = self.web_scraper.ingest_into_knowledgebase(self.knowledgebase)

        summary = {
            'timestamp': learning_session.get('timestamp', datetime.now()),
            'session_id': learning_session.get('session_id'),
            'patterns_learned': learning_session.get('patterns_learned', 0),
            'templates_learned': learning_session.get('templates_learned', 0),
            'technical_knowledge_added': learning_session.get('technical_knowledge_added', 0),
            'validated_items': len(validated_content),
            'diagnostics': diagnostics,
            'saved_file': saved_file,
            'knowledgebase_ingest': kb_result,
            'success': learning_session.get('success', False),
        }
        self.last_autonomous_learning = summary['timestamp']
        self.autonomous_learning_history.append(summary)
        self.autonomous_learning_history = self.autonomous_learning_history[-30:]
        self.logger.info(
            "Autonomous learning completed (%d validated items, %d patterns)",
            summary['validated_items'],
            summary['patterns_learned'],
        )

    def _resolve_dynamic_sources(self, cfg: Dict[str, Any]) -> List[str]:
        sources = cfg.get('dynamic_sources', [])
        resolved: List[str] = []
        for entry in sources:
            if isinstance(entry, str):
                resolved.append(entry)
            elif isinstance(entry, dict):
                url = entry.get('url')
                if url:
                    resolved.append(url)
        if not self.web_scraper:
            return resolved
        allowed = []
        for url in resolved:
            if self.web_scraper._is_allowed_url(url):
                allowed.append(url)
            else:
                self.logger.warning("Dynamic source skipped (not safelisted): %s", url)
        return allowed

    def _cross_reference_scraped_content(
        self,
        contents: List[ScrapedContent],
        cfg: Dict[str, Any],
    ) -> Tuple[List[ScrapedContent], Dict[str, Any]]:
        if not contents:
            return [], {'total_items': 0, 'validated_items': 0, 'notes': 'no content'}

        min_sources = max(2, cfg.get('minimum_source_agreement', 2))
        max_topics = max(3, cfg.get('max_topics_per_source', 5))
        topic_to_sources: Dict[str, set] = defaultdict(set)
        content_topics: Dict[int, List[str]] = {}

        for item in contents:
            topics = self._extract_topics_from_text(item.content, max_topics)
            content_topics[id(item)] = topics
            for topic in topics:
                topic_to_sources[topic].add(item.source)

        validated: List[ScrapedContent] = []
        diagnostics: List[Dict[str, Any]] = []
        for item in contents:
            topics = content_topics.get(id(item), [])
            corroborated = [topic for topic in topics if len(topic_to_sources[topic]) >= min_sources]
            diag = {
                'title': item.title,
                'source': item.source,
                'topics': topics,
                'corroborated_topics': corroborated,
            }
            if corroborated:
                validated.append(item)
                diag['status'] = 'validated'
            else:
                diag['status'] = 'insufficient_support'
            diagnostics.append(diag)

        if not validated and contents:
            # fallback: keep top relevance item to avoid total starvation, but mark low confidence
            top_item = max(contents, key=lambda c: getattr(c, 'relevance_score', 0))
            diagnostics.append({'title': top_item.title, 'status': 'fallback_included'})
            validated.append(top_item)

        report = {
            'total_items': len(contents),
            'validated_items': len(validated),
            'minimum_source_agreement': min_sources,
            'diagnostics': diagnostics,
        }
        return validated, report

    def _extract_topics_from_text(self, text: str, limit: int = 5) -> List[str]:
        if not text:
            return []
        words = re.findall(r'[A-Za-z]{4,}', text.lower())
        cleaned = [w for w in words if w not in TOPIC_STOPWORDS]
        if not cleaned:
            return []
        freq = Counter(cleaned)
        return [word for word, _ in freq.most_common(limit)]

    def _merge_learning_results(self, base: Dict[str, Any], extra: Dict[str, Any]) -> None:
        """Merge learning result dictionaries in-place."""
        if not extra:
            return
        # conversation_patterns / response_templates are dicts mapping str -> list
        for key in ['conversation_patterns', 'response_templates', 'technical_knowledge']:
            base.setdefault(key, {})
            extra_section = extra.get(key, {})
            if isinstance(extra_section, dict):
                for pattern, entries in extra_section.items():
                    base[key].setdefault(pattern, [])
                    base[key][pattern].extend(entries)
    
    def get_learning_insights(self, message: str, intent: str) -> Dict[str, Any]:
        """
        Get learning insights for a message
        
        Args:
            message: User message
            intent: Classified intent
            
        Returns:
            Learning insights including patterns, templates, and knowledge
        """
        insights = {
            'learned_patterns': [],
            'response_templates': [],
            'technical_knowledge': [],
            'learning_available': False
        }
        
        if not AI_LEARNING_AVAILABLE:
            return insights
        
        try:
            # Get relevant learned patterns
            patterns = self.ai_learning_system.get_relevant_patterns(message, intent)
            insights['learned_patterns'] = [
                {
                    'pattern': p.pattern,
                    'confidence': p.confidence,
                    'effectiveness': p.effectiveness_score,
                    'usage_count': p.usage_count
                }
                for p in patterns
            ]
            
            # Get relevant response templates
            templates = self.ai_learning_system.get_relevant_templates(message, intent)
            insights['response_templates'] = [
                {
                    'template': t.template,
                    'intent': t.intent,
                    'confidence': t.confidence,
                    'effectiveness': t.effectiveness_score,
                    'usage_count': t.usage_count
                }
                for t in templates
            ]
            
            # Get relevant technical knowledge
            # Extract key topics from message
            topics = self._extract_key_topics(message)
            for topic in topics:
                knowledge = self.ai_learning_system.get_technical_knowledge(topic)
                if knowledge:
                    insights['technical_knowledge'].extend([
                        {
                            'topic': topic,
                            'info': k['info'],
                            'relevance': k['relevance'],
                            'source': k['source']
                        }
                        for k in knowledge
                    ])
            
            insights['learning_available'] = True
            
        except Exception as e:
            self.logger.error(f"Error getting learning insights: {e}")
        
        return insights
    
    def _extract_key_topics(self, message: str) -> List[str]:
        """Extract key topics from message for knowledge lookup"""
        # Simple keyword extraction - could be enhanced with NLP
        words = re.findall(r'\b\w+\b', message.lower())
        
        # Filter out common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'i', 'you', 'we', 'they', 'he', 'she', 'it', 'what', 'how', 'when', 'where', 'why', 'who', 'can', 'could', 'would', 'should', 'may', 'might', 'must'}
        
        key_topics = [word for word in words if word not in common_words and len(word) > 2]
        
        # Return unique topics, limited to 5
        return list(set(key_topics))[:5]
    
    def update_learning_feedback(self, response_id: str, user_feedback: float, response_type: str) -> bool:
        """
        Update learning system with user feedback
        
        Args:
            response_id: ID of the response
            user_feedback: Feedback score (0.0 to 1.0)
            response_type: Type of response (pattern, template, etc.)
            
        Returns:
            Success status
        """
        if not AI_LEARNING_AVAILABLE:
            return False
        
        try:
            # This is a simplified implementation
            # In a real system, you'd track which patterns/templates were used
            feedback_data = {
                'response_id': response_id,
                'feedback_score': user_feedback,
                'response_type': response_type,
                'timestamp': datetime.now()
            }
            
            # Update effectiveness scores based on feedback
            # This would need to be implemented with proper tracking
            self.ai_learning_system.update_effectiveness_scores({
                'patterns': {},  # Would map actual pattern IDs
                'templates': {}  # Would map actual template IDs
            })
            
            self.logger.info(f"Updated learning feedback for {response_type}: {user_feedback}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating learning feedback: {e}")
            return False
    
    def get_learning_status(self) -> Dict[str, Any]:
        """
        Get current learning system status
        
        Returns:
            Learning system status summary
        """
        if not AI_LEARNING_AVAILABLE:
            return {
                'available': False,
                'message': 'AI learning system not available'
            }
        
        try:
            return {
                'available': True,
                'summary': self.ai_learning_system.get_learning_summary(),
                'web_scraper_available': WEB_SCRAPER_AVAILABLE,
                'last_learning_session': self.ai_learning_system.performance_metrics.get('last_learning_session'),
                'total_learning_sessions': self.ai_learning_system.performance_metrics.get('learning_sessions', 0)
            }
        except Exception as e:
            self.logger.error(f"Error getting learning status: {e}")
            return {
                'available': False,
                'message': f"Error getting learning status: {e}"
            }
    
    def integrate_model_knowledge(self, message: str, intent: str) -> Dict[str, Any]:
        """
        Integrate model knowledge from PyTorch and other libraries
        
        Args:
            message: User message
            intent: Classified intent
            
        Returns:
            Model knowledge insights and integration results
        """
        insights = {
            'model_knowledge': {},
            'self_understanding': {},
            'technical_insights': [],
            'integration_available': False
        }
        
        if not MODEL_KNOWLEDGE_INTEGRATOR_AVAILABLE:
            return insights
        
        try:
            # Get relevant model knowledge
            relevant_knowledge = self.model_knowledge_integrator.get_knowledge_for_query(message)
            
            # Get self-understanding knowledge
            self_understanding = self.model_knowledge_integrator.get_self_understanding_knowledge()
            
            insights['model_knowledge'] = relevant_knowledge
            insights['self_understanding'] = self_understanding
            insights['integration_available'] = True
            
            # Extract technical insights
            for lib_name, knowledge in relevant_knowledge.items():
                if knowledge['relevance_score'] > 0.5:
                    insights['technical_insights'].append({
                        'library': lib_name,
                        'relevance': knowledge['relevance_score'],
                        'functions': knowledge['relevant_functions'],
                        'classes': knowledge['relevant_classes'],
                        'examples': knowledge['relevant_examples'],
                        'use_cases': knowledge['relevant_use_cases']
                    })
            
        except Exception as e:
            self.logger.error(f"Error integrating model knowledge: {e}")
        
        return insights
    
    def get_enhanced_response_with_model_knowledge(self, message: str, intent: str, base_response: str) -> str:
        """
        Enhance response with model knowledge from PyTorch and other libraries
        
        Args:
            message: User message
            intent: Classified intent
            base_response: Base response from ARCHON
            
        Returns:
            Enhanced response with model knowledge
        """
        if not MODEL_KNOWLEDGE_INTEGRATOR_AVAILABLE:
            return base_response
        
        try:
            # Get model knowledge insights
            insights = self.integrate_model_knowledge(message, intent)
            
            if not insights['integration_available']:
                return base_response
            
            # Enhance response with technical insights
            enhanced_response = base_response
            technical_insights = insights.get('technical_insights', [])
            
            if technical_insights:
                # Add technical context
                tech_context = self._generate_technical_context(technical_insights, intent)
                if tech_context:
                    enhanced_response = f"{base_response}\n\n{tech_context}"
            
            # Add self-understanding context if relevant
            if 'who are you' in message.lower() or 'what are you' in message.lower():
                self_context = self._generate_self_understanding_context(insights['self_understanding'])
                if self_context:
                    enhanced_response = f"{self_context}\n\n{base_response}"
            
            return enhanced_response
            
        except Exception as e:
            self.logger.error(f"Error enhancing response with model knowledge: {e}")
            return base_response
    
    def _generate_technical_context(self, technical_insights: List[Dict], intent: str) -> str:
        """Generate technical context from model knowledge"""
        context_parts = []
        
        for insight in technical_insights[:2]:  # Limit to top 2 insights
            lib_name = insight['library']
            
            if lib_name == 'torch':
                if intent in ['programming', 'learning_request', 'technical_explanation']:
                    context_parts.append("I'm built with PyTorch, which provides powerful tensor operations and neural network capabilities.")
                    
                # Add specific PyTorch examples
                examples = insight.get('examples', [])
                if examples:
                    context_parts.append(f"For example, with PyTorch: {examples[0]}")
            
            elif lib_name == 'transformers':
                if intent in ['learning_request', 'technical_explanation']:
                    context_parts.append("I can leverage Transformers library for advanced language understanding and generation.")
            
            elif lib_name == 'numpy':
                if intent in ['programming', 'technical_explanation']:
                    context_parts.append("I use NumPy for efficient numerical computations and array operations.")
            
            elif lib_name == 'sklearn':
                if intent in ['programming', 'technical_explanation']:
                    context_parts.append("I integrate Scikit-learn for machine learning algorithms and pattern recognition.")
        
        return '\n'.join(context_parts)
    
    def _generate_self_understanding_context(self, self_understanding: Dict) -> str:
        """Generate self-understanding context"""
        context_parts = []
        
        # Architecture description
        architecture = self_understanding.get('architecture', {})
        if architecture:
            context_parts.append(f"I am {architecture.get('description', 'an AI system')}")
            context_parts.append(f"My components include: {', '.join(architecture.get('components', []))}")
        
        # Technical stack
        tech_stack = self_understanding.get('technical_stack', {})
        if tech_stack:
            context_parts.append("I'm built with these key technologies:")
            for lib_name, info in tech_stack.items():
                context_parts.append(f"  • {lib_name}: {info.get('role', 'Support library')}")
        
        # Capabilities
        capabilities = architecture.get('capabilities', [])
        if capabilities:
            context_parts.append(f"My capabilities include: {', '.join(capabilities)}")
        
        return '\n'.join(context_parts)
    
    def update_model_knowledge(self) -> Dict[str, Any]:
        """
        Update model knowledge from all available libraries
        
        Returns:
            Update results
        """
        if not MODEL_KNOWLEDGE_INTEGRATOR_AVAILABLE:
            return {
                'success': False,
                'message': 'Model knowledge integrator not available'
            }
        
        try:
            print("Updating model knowledge from PyTorch and other libraries...")
            
            # Integrate knowledge from all libraries
            integration_results = self.model_knowledge_integrator.integrate_all_model_knowledge()
            
            result = {
                'success': True,
                'libraries_processed': integration_results['libraries_processed'],
                'functions_discovered': integration_results['total_functions_discovered'],
                'classes_discovered': integration_results['total_classes_discovered'],
                'timestamp': integration_results['timestamp'],
                'errors': integration_results['errors']
            }
            
            print(f"Model knowledge updated: {result['libraries_processed']} libraries, {result['functions_discovered']} functions, {result['classes_discovered']} classes")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error updating model knowledge: {e}")
            return {
                'success': False,
                'message': f"Error updating model knowledge: {e}"
            }
    
    def get_model_knowledge_status(self) -> Dict[str, Any]:
        """
        Get current model knowledge status
        
        Returns:
            Model knowledge status
        """
        if not MODEL_KNOWLEDGE_INTEGRATOR_AVAILABLE:
            return {
                'available': False,
                'message': 'Model knowledge integrator not available'
            }
        
        try:
            knowledge_count = len(self.model_knowledge_integrator.model_knowledge)
            
            return {
                'available': True,
                'libraries_count': knowledge_count,
                'libraries': list(self.model_knowledge_integrator.model_knowledge.keys()),
                'last_update': self.model_knowledge_integrator.last_update,
                'self_understanding_available': True
            }
            
        except Exception as e:
            self.logger.error(f"Error getting model knowledge status: {e}")
            return {
                'available': False,
                'message': f"Error getting model knowledge status: {e}"
            }
    
    def speak_response(self, text: str) -> Dict[str, Any]:
        """Convert response to speech using enhanced TTS if available"""
        try:
            # Use enhanced TTS if available
            if ENHANCED_TTS_AVAILABLE and self.enhanced_tts:
                return self.enhanced_tts.speak_text(text, blocking=False)
            else:
                # Fall back to standard TTS
                result = self.tts_engine.speak(text, blocking=False)
                return result
        except Exception as e:
            return {'success': False, 'message': f"Speech synthesis failed: {e}"}
    
    def listen_for_command(self, duration: int = 5) -> Optional[str]:
        """Listen for voice command"""
        try:
            text = self.stt_engine.listen(duration)
            return text
        except Exception as e:
            self.logger.error(f"Speech recognition failed: {e}")
            return None
    
    def _track_error(self, error: Exception, context: str = ""):
        """Track errors for self-healing analysis"""
        try:
            self._last_error = {
                'error': str(error),
                'context': context,
                'timestamp': datetime.now(),
                'traceback': traceback.format_exc()
            }
            self._error_count += 1
            
            # Log the error
            self.logger.error(f"Error tracked: {context} - {error}")
            
            # Trigger self-healing if enabled and threshold reached
            if self._healing_enabled and self._error_count >= 3:
                self._trigger_self_healing()
                
        except Exception as e:
            self.logger.error(f"Error tracking failed: {e}")
    
    def _trigger_self_healing(self):
        """Trigger the self-healing process"""
        try:
            if not SELF_HEALING_AVAILABLE or not self.self_healing_system:
                self.logger.warning("Self-healing system not available")
                return
            
            self.logger.info("Triggering self-healing process...")
            
            # Run self-healing cycle
            healing_result = self.self_healing_system.run_self_healing_cycle()
            
            if healing_result['success']:
                self.logger.info(f"Self-healing successful: {healing_result['message']}")
                self._error_count = 0  # Reset error count on successful healing
            else:
                self.logger.warning(f"Self-healing failed: {healing_result['message']}")
                
        except Exception as e:
            self.logger.error(f"Error triggering self-healing: {e}")
    
    def request_self_healing(self, issue_description: str = "") -> Dict[str, Any]:
        """
        Manually request self-healing for a specific issue
        """
        try:
            if not SELF_HEALING_AVAILABLE or not self.self_healing_system:
                return {
                    'success': False,
                    'message': "Self-healing system not available",
                    'available': False
                }
            
            self.logger.info(f"Manual self-healing request: {issue_description}")
            
            # Detect issues
            issues = self.self_healing_system.detect_code_issues()
            
            if not issues:
                return {
                    'success': True,
                    'message': "No issues detected",
                    'issues_found': 0,
                    'available': True
                }
            
            # Add manual issue if provided
            if issue_description:
                manual_issue = {
                    'type': 'manual_request',
                    'message': issue_description,
                    'severity': 'medium',
                    'description': f"Manual self-healing request: {issue_description}",
                    'timestamp': datetime.now().isoformat()
                }
                issues.append(manual_issue)
            
            # Request fix from Windsurf
            fix_request = self.self_healing_system.request_fix_from_windsurf(issues)
            
            if not fix_request.get('success', False):
                return {
                    'success': False,
                    'message': "Failed to request fix from Windsurf",
                    'issues_found': len(issues),
                    'available': True
                }
            
            # Apply the fix
            fix_result = self.self_healing_system.apply_fix(fix_request)
            
            return {
                'success': fix_result.get('success', False),
                'message': fix_result.get('message', 'Fix process completed'),
                'issues_found': len(issues),
                'fix_applied': fix_result.get('applied', False),
                'available': True,
                'fix_details': fix_request
            }
            
        except Exception as e:
            self.logger.error(f"Error in manual self-healing request: {e}")
            return {
                'success': False,
                'message': f"Error in self-healing request: {e}",
                'available': True
            }
    
    def get_self_healing_status(self) -> Dict[str, Any]:
        """
        Get the current status of the self-healing system
        """
        try:
            if not SELF_HEALING_AVAILABLE or not self.self_healing_system:
                return {
                    'available': False,
                    'message': "Self-healing system not available"
                }
            
            healing_status = self.self_healing_system.get_healing_status()
            
            return {
                'available': True,
                'enabled': self._healing_enabled,
                'error_count': self._error_count,
                'last_error': self._last_error,
                'healing_status': healing_status,
                'system_health': healing_status.get('system_health', 'unknown')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting self-healing status: {e}")
            return {
                'available': False,
                'message': f"Error getting status: {e}",
                'enabled': self._healing_enabled
            }
    
    def enable_self_healing(self) -> Dict[str, Any]:
        """
        Enable the self-healing system
        """
        try:
            if not SELF_HEALING_AVAILABLE:
                return {
                    'success': False,
                    'message': "Self-healing system not available"
                }
            
            self._healing_enabled = True
            self.logger.info("Self-healing system enabled")
            
            return {
                'success': True,
                'message': "Self-healing system enabled",
                'enabled': True
            }
            
        except Exception as e:
            self.logger.error(f"Error enabling self-healing: {e}")
            return {
                'success': False,
                'message': f"Error enabling self-healing: {e}",
                'enabled': self._healing_enabled
            }
    
    def disable_self_healing(self) -> Dict[str, Any]:
        """
        Disable the self-healing system
        """
        try:
            self._healing_enabled = False
            self.logger.info("Self-healing system disabled")
            
            return {
                'success': True,
                'message': "Self-healing system disabled",
                'enabled': False
            }
            
        except Exception as e:
            self.logger.error(f"Error disabling self-healing: {e}")
            return {
                'success': False,
                'message': f"Error disabling self-healing: {e}",
                'enabled': self._healing_enabled
            }
    
    def communicate_with_windsurf(self, message: str) -> Dict[str, Any]:
        """
        Communicate with Windsurf's AI chat for assistance
        """
        try:
            self.logger.info(f"Communicating with Windsurf AI: {message}")
            
            # Format the message for Windsurf
            windsurf_message = f"ARCHON AI Self-Healing Request\n\n"
            windsurf_message += f"Message: {message}\n"
            windsurf_message += f"Timestamp: {datetime.now().isoformat()}\n"
            windsurf_message += f"Error Count: {self._error_count}\n"
            windsurf_message += f"Last Error: {self._last_error.get('error', 'None') if self._last_error else 'None'}\n"
            windsurf_message += f"System Status: {self.get_self_healing_status()}\n\n"
            windsurf_message += "Please provide assistance with this issue. I need help fixing my code."
            
            # In a real implementation, this would integrate with Windsurf's API
            # For now, we'll simulate the communication
            response = self._simulate_windsurf_communication(windsurf_message)
            
            return {
                'success': True,
                'message': "Communication sent to Windsurf AI",
                'windsurf_response': response,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error communicating with Windsurf: {e}")
            return {
                'success': False,
                'message': f"Error communicating with Windsurf: {e}"
            }
    
    def _simulate_windsurf_communication(self, message: str) -> str:
        """
        Simulate communication with Windsurf AI
        """
        try:
            # Simulate processing time
            time.sleep(2)
            
            # Generate a simulated response
            response = "I understand your request. I can help you fix the issues in your ARCHON AI system. "
            response += "Based on the information provided, I recommend:\n\n"
            response += "1. Review the detected issues in your code\n"
            response += "2. Apply the provided fixes systematically\n"
            response += "3. Test the fixes to ensure they work correctly\n"
            response += "4. Restart the system if necessary\n\n"
            response += "If you need specific code fixes, please provide the exact error messages "
            response += "and I'll generate the appropriate code for you to apply."
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error simulating Windsurf communication: {e}")
            return f"Error in communication: {e}"
    
    def search_knowledgebase(self, query: str, top_k: int = 5, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search the knowledgebase for relevant information
        
        Args:
            query: Search query
            top_k: Number of results to return
            category: Optional category filter
            
        Returns:
            List of search results
        """
        try:
            if not MILVUS_KNOWLEDGEBASE_AVAILABLE or not self.knowledgebase:
                return []
            
            # Generate embedding for query (simplified)
            query_hash = hashlib.md5(query.encode()).hexdigest()
            query_embedding = [float(int(c, 16) % 100 / 100) for c in query_hash[:768 * 2]]
            query_embedding = query_embedding[:768]
            
            # Pad if necessary
            while len(query_embedding) < 768:
                query_embedding.append(0.0)
            
            # Search knowledgebase (pass query_text for keyword fallback)
            results = self.knowledgebase.search_knowledge(
                query_embedding, top_k, category, query_text=query
            )
            
            self.logger.info(f"Found {len(results)} knowledge items for query: {query[:50]}...")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching knowledgebase: {e}")
            return []
    
    def add_to_knowledgebase(self, content: str, source: str = "conversation", category: str = "general") -> bool:
        """
        Add content to the knowledgebase
        
        Args:
            content: Content to add
            source: Source of the content
            category: Category of the content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not MILVUS_KNOWLEDGEBASE_AVAILABLE or not self.knowledgebase:
                return False
            
            # Generate embedding for content (simplified)
            content_hash = hashlib.md5(content.encode()).hexdigest()
            content_embedding = [float(int(c, 16) % 100 / 100) for c in content_hash[:768 * 2]]
            content_embedding = content_embedding[:768]
            
            # Pad if necessary
            while len(content_embedding) < 768:
                content_embedding.append(0.0)
            
            # Add to knowledgebase
            success = self.knowledgebase.add_knowledge(content, content_embedding, source, category)
            
            if success:
                self.logger.info(f"Added knowledge from {source} in category {category}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error adding to knowledgebase: {e}")
            return False
    
    def get_knowledgebase_stats(self) -> Dict[str, Any]:
        """
        Get knowledgebase statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            if not MILVUS_KNOWLEDGEBASE_AVAILABLE or not self.knowledgebase:
                return {
                    "available": False,
                    "message": "Knowledgebase not available"
                }
            
            stats = self.knowledgebase.get_statistics()
            stats["available"] = True
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting knowledgebase stats: {e}")
            return {
                "available": False,
                "message": f"Error getting stats: {e}"
            }
    
    def explain_knowledgebase(self) -> str:
        """
        Explain the knowledgebase capabilities
        
        Returns:
            Explanation string
        """
        try:
            if not MILVUS_KNOWLEDGEBASE_AVAILABLE or not self.knowledgebase:
                return "I don't have access to a knowledgebase system at the moment."
            
            stats = self.get_knowledgebase_stats()
            
            explanation = f"""I have a Milvus vector database knowledgebase with the following capabilities:
            
            1. **Knowledge Storage**: I can store and retrieve information using vector embeddings
            2. **Semantic Search**: I can find relevant information based on meaning, not just keywords
            3. **Knowledge Categories**: I organize knowledge into categories for better retrieval
            4. **Source Tracking**: I track where each piece of knowledge comes from
            5. **Learning Integration**: I can automatically add important information from our conversations
            
            **Current Status**: {stats.get('total_items', 0)} knowledge items stored
            **Categories**: {list(stats.get('categories', {}).keys())}
            **Database Type**: {stats.get('type', 'Milvus')}
            
            You can ask me to search my knowledgebase for specific topics, or I can automatically add important information from our conversations."""
            
            return explanation
            
        except Exception as e:
            self.logger.error(f"Error explaining knowledgebase: {e}")
            return "I have a knowledgebase system, but I'm having trouble accessing it right now."
