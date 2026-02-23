"""
Advanced Text Parser for ARCHON

This module provides sophisticated text analysis capabilities including:
- Deep semantic understanding
- Intent recognition with high accuracy
- Entity extraction and relationship mapping
- Contextual analysis
- Multi-level text processing
- Advanced pattern recognition
"""

import re
import json
import hashlib
from typing import Dict, List, Any, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import ast
import spacy

# Try to load spaCy for advanced NLP
try:
    SPACY_AVAILABLE = True
    nlp = spacy.load("en_core_web_sm")
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None
    print("Warning: spaCy not available. Using basic text parsing.")

class TextComplexity(Enum):
    """Text complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"
    RESEARCH = "research"

class IntentCategory(Enum):
    """Advanced intent categories"""
    CONVERSATION = "conversation"
    PROGRAMMING = "programming"
    SYSTEM_OPERATION = "system_operation"
    DATA_ANALYSIS = "data_analysis"
    LEARNING_REQUEST = "learning_request"
    CREATIVE_TASK = "creative_task"
    PROBLEM_SOLVING = "problem_solving"
    TECHNICAL_EXPLANATION = "technical_explanation"
    CODE_REVIEW = "code_review"
    ARCHITECTURE_DESIGN = "architecture_design"
    RESEARCH_QUERY = "research_query"
    EMOTIONAL_SUPPORT = "emotional_support"
    STRATEGIC_PLANNING = "strategic_planning"

@dataclass
class TextEntity:
    """Represents an extracted entity from text"""
    text: str
    entity_type: str
    confidence: float
    start_pos: int
    end_pos: int
    context: str
    relationships: List[str] = None
    
    def __post_init__(self):
        if self.relationships is None:
            self.relationships = []

@dataclass
class SemanticAnalysis:
    """Represents semantic analysis of text"""
    main_topic: str
    subtopics: List[str]
    sentiment: str
    urgency: str
    complexity: TextComplexity
    key_concepts: List[str]
    questions_asked: List[str]
    statements_made: List[str]
    commands_given: List[str]

@dataclass
class ContextualAnalysis:
    """Represents contextual analysis"""
    conversation_stage: str
    user_intent: str
    previous_context: List[str]
    required_actions: List[str]
    expected_response_type: str
    domain_knowledge_required: List[str]
    confidence_score: float

class AdvancedTextParser:
    """Advanced text parser with deep semantic understanding"""
    
    def __init__(self):
        self.patterns = self._load_advanced_patterns()
        self.knowledge_domains = self._load_knowledge_domains()
        self.semantic_rules = self._load_semantic_rules()
        self.context_memory = []
        
    def _load_advanced_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Load advanced regex patterns for text analysis"""
        return {
            "programming": [
                re.compile(r'\b(def|class|function|import|from|return|if|for|while|try|except|catch|raise|break|continue|pass|yield|lambda|async|await)\b', re.IGNORECASE),
                re.compile(r'\b(Python|JavaScript|Java|C\+\+|HTML|CSS|SQL|React|Vue|Angular|Django|Flask|Node\.js|TypeScript|Go|Rust|Swift|Kotlin)\b', re.IGNORECASE),
                re.compile(r'\b(algorithm|data structure|API|database|framework|library|module|package|function|method|variable|class|object|interface)\b', re.IGNORECASE),
                re.compile(r'\b(debug|test|deploy|compile|run|execute|install|setup|configure|build|optimize|refactor|debugger|IDE|editor)\b', re.IGNORECASE),
                re.compile(r'\b(syntax|error|exception|bug|issue|problem|solution|fix|patch|update|upgrade|version|release)\b', re.IGNORECASE)
            ],
            "system_operations": [
                re.compile(r'\b(create|delete|copy|move|rename|list|search|find|open|close|read|write|execute|run|start|stop|kill|restart|shutdown|reboot)\b', re.IGNORECASE),
                re.compile(r'\b(file|folder|directory|process|service|application|program|system|computer|machine|server|network|internet)\b', re.IGNORECASE),
                re.compile(r'\b(memory|CPU|GPU|disk|storage|monitor|check|status|performance|health|log|backup|restore)\b', re.IGNORECASE),
                re.compile(r'\b(install|uninstall|update|upgrade|configure|setup|initialize|mount|unmount|format|partition)\b', re.IGNORECASE)
            ],
            "data_analysis": [
                re.compile(r'\b(analyze|process|parse|extract|transform|filter|sort|group|aggregate|calculate|compute|statistics|metrics|data|dataset|database|query)\b', re.IGNORECASE),
                re.compile(r'\b(chart|graph|plot|visualize|report|dashboard|analytics|insights|trends|patterns|correlation|regression|classification|clustering)\b', re.IGNORECASE),
                re.compile(r'\b(Machine Learning|AI|neural network|deep learning|model|training|prediction|classification|regression|clustering|feature|label|target)\b', re.IGNORECASE)
            ],
            "creative_tasks": [
                re.compile(r'\b(create|design|write|compose|generate|imagine|brainstorm|invent|develop|build|make|craft|produce|author)\b', re.IGNORECASE),
                re.compile(r'\b(story|poem|song|music|art|design|image|video|animation|game|application|website|interface)\b', re.IGNORECASE),
                re.compile(r'\b(creative|innovative|original|unique|artistic|beautiful|elegant|inspiring|engaging)\b', re.IGNORECASE)
            ],
            "learning_requests": [
                re.compile(r'\b(teach|learn|explain|show me|how to|what is|why|when|where|who|help me understand|guide|tutorial|documentation|manual|instructions)\b', re.IGNORECASE),
                re.compile(r'\b(study|practice|training|course|lesson|example|sample|demo|walkthrough|step by step|how do I)\b', re.IGNORECASE),
                re.compile(r'\b(concept|principle|theory|fundamentals|basics|introduction|overview|summary|review|explanation)\b', re.IGNORECASE)
            ],
            "emotional_support": [
                re.compile(r'\b(happy|sad|angry|frustrated|confused|worried|excited|proud|disappointed|hopeful|afraid|nervous|calm|relaxed)\b', re.IGNORECASE),
                re.compile(r'\b(feel|emotion|mood|attitude|mindset|outlook|perspective|opinion|thought|feeling)\b', re.IGNORECASE),
                re.compile(r'\b(help|support|comfort|encourage|advise|counsel|listen|understand|empathize|relate)\b', re.IGNORECASE)
            ]
        }
    
    def _load_knowledge_domains(self) -> Dict[str, List[str]]:
        """Load knowledge domains for text classification"""
        return {
            "programming": [
                "python", "javascript", "java", "cpp", "html", "css", "sql", "react", "vue", "angular",
                "django", "flask", "nodejs", "typescript", "go", "rust", "swift", "kotlin",
                "algorithm", "data structure", "api", "database", "framework", "library",
                "debugging", "testing", "deployment", "optimization", "refactoring",
                "syntax", "error", "exception", "bug", "issue", "problem", "solution"
            ],
            "system_administration": [
                "linux", "windows", "macos", "ubuntu", "centos", "debian", "server", "network",
                "firewall", "security", "backup", "monitoring", "logging", "automation",
                "scripting", "shell", "bash", "powershell", "command", "terminal",
                "process", "service", "application", "performance", "memory", "cpu", "disk"
            ],
            "data_science": [
                "pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "tensorflow",
                "pytorch", "keras", "jupyter", "notebook", "analysis", "visualization",
                "statistics", "machine learning", "deep learning", "neural network",
                "data", "dataset", "model", "training", "prediction", "classification",
                "regression", "clustering", "feature engineering"
            ],
            "web_development": [
                "html", "css", "javascript", "frontend", "backend", "fullstack",
                "responsive", "design", "ui", "ux", "api", "rest", "graphql",
                "database", "sql", "nosql", "mongodb", "postgresql", "mysql",
                "framework", "library", "package", "module", "dependency"
            ],
            "ai_ml": [
                "artificial intelligence", "machine learning", "deep learning",
                "neural network", "algorithm", "model", "training", "inference",
                "prediction", "classification", "regression", "clustering",
                "nlp", "computer vision", "reinforcement learning", "gan",
                "transformer", "bert", "gpt", "llm", "prompt engineering"
            ],
            "general_knowledge": [
                "science", "mathematics", "physics", "chemistry", "biology",
                "history", "geography", "literature", "philosophy", "psychology",
                "economics", "politics", "business", "finance", "marketing",
                "education", "health", "medicine", "technology", "engineering"
            ]
        }
    
    def _load_semantic_rules(self) -> Dict[str, List[str]]:
        """Load semantic rules for text understanding"""
        return {
            "question_indicators": [
                "what", "how", "why", "when", "where", "who", "which", "can you",
                "could you", "would you", "are you", "is there", "do you",
                "explain", "describe", "tell me", "show me", "help me"
            ],
            "command_indicators": [
                "do", "create", "make", "build", "write", "generate", "run",
                "execute", "start", "stop", "delete", "move", "copy", "open",
                "close", "install", "setup", "configure", "check", "monitor"
            ],
            "request_indicators": [
                "please", "kindly", "could you", "would you", "i need",
                "i want", "i would like", "i require", "looking for",
                "searching for", "trying to", "need help with"
            ],
            "complexity_indicators": {
                "simple": ["simple", "basic", "easy", "quick", "short"],
                "moderate": ["moderate", "intermediate", "detailed", "explain"],
                "complex": ["complex", "advanced", "detailed", "comprehensive", "thorough"],
                "expert": ["expert", "professional", "specialized", "technical", "in-depth"]
            }
        }
    
    def analyze_text_comprehensive(self, text: str) -> Dict[str, Any]:
        """Comprehensive text analysis with multiple layers"""
        analysis = {
            'basic_analysis': self._basic_text_analysis(text),
            'semantic_analysis': self._semantic_analysis(text),
            'contextual_analysis': self._contextual_analysis(text),
            'entity_extraction': self._extract_entities(text),
            'intent_classification': self._classify_intent(text),
            'complexity_assessment': self._assess_complexity(text),
            'domain_classification': self._classify_domain(text),
            'relationship_mapping': self._map_relationships(text),
            'confidence_scores': self._calculate_confidence_scores(text)
        }
        
        return analysis
    
    def _basic_text_analysis(self, text: str) -> Dict[str, Any]:
        """Basic text analysis"""
        return {
            'length': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(re.findall(r'[.!?]+', text)),
            'has_questions': '?' in text,
            'has_commands': any(word in text.lower() for word in self.semantic_rules['command_indicators']),
            'has_requests': any(word in text.lower() for word in self.semantic_rules['request_indicators']),
            'language': self._detect_language(text),
            'encoding': 'utf-8'
        }
    
    def _semantic_analysis(self, text: str) -> SemanticAnalysis:
        """Deep semantic analysis of text"""
        # Extract main topics
        words = text.lower().split()
        
        # Identify key concepts
        key_concepts = []
        for domain, terms in self.knowledge_domains.items():
            for term in terms:
                if term.lower() in words:
                    key_concepts.append(term)
        
        # Identify questions and statements
        questions = []
        statements = []
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                if any(indicator in sentence.lower() for indicator in self.semantic_rules['question_indicators']):
                    questions.append(sentence)
                else:
                    statements.append(sentence)
        
        # Determine main topic
        main_topic = self._determine_main_topic(text, key_concepts)
        
        # Determine subtopics
        subtopics = self._extract_subtopics(text, key_concepts)
        
        # Assess sentiment (basic implementation)
        sentiment = self._analyze_sentiment(text)
        
        # Assess urgency
        urgency = self._assess_urgency(text)
        
        # Determine complexity
        complexity = self._determine_complexity(text)
        
        return SemanticAnalysis(
            main_topic=main_topic,
            subtopics=subtopics,
            sentiment=sentiment,
            urgency=urgency,
            complexity=complexity,
            key_concepts=key_concepts,
            questions_asked=questions,
            statements_made=statements
        )
    
    def _contextual_analysis(self, text: str) -> ContextualAnalysis:
        """Contextual analysis considering conversation history"""
        # Determine conversation stage
        conversation_stage = self._determine_conversation_stage(text)
        
        # Identify user intent
        user_intent = self._identify_user_intent(text)
        
        # Get previous context
        previous_context = self.context_memory[-5:] if self.context_memory else []
        
        # Determine required actions
        required_actions = self._determine_required_actions(text)
        
        # Determine expected response type
        expected_response_type = self._determine_response_type(text)
        
        # Identify domain knowledge required
        domain_knowledge = self._identify_domain_knowledge(text)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(text)
        
        # Add to context memory
        self.context_memory.append(text)
        if len(self.context_memory) > 100:
            self.context_memory = self.context_memory[-50:]
        
        return ContextualAnalysis(
            conversation_stage=conversation_stage,
            user_intent=user_intent,
            previous_context=previous_context,
            required_actions=required_actions,
            expected_response_type=expected_response_type,
            domain_knowledge=domain_knowledge,
            confidence_score=confidence_score
        )
    
    def _extract_entities(self, text: str) -> List[TextEntity]:
        """Extract entities from text"""
        entities = []
        
        # Use spaCy if available for advanced NLP
        if SPACY_AVAILABLE and nlp:
            doc = nlp(text)
            for ent in doc.ents:
                entity = TextEntity(
                    text=ent.text,
                    entity_type=ent.label_,
                    confidence=1.0,
                    start_pos=ent.start_char,
                    end_pos=ent.end_char,
                    context=text[max(0, ent.start_char-20):ent.end_char+20]
                )
                entities.append(entity)
        else:
            # Basic entity extraction
            entities = self._basic_entity_extraction(text)
        
        return entities
    
    def _basic_entity_extraction(self, text: str) -> List[TextEntity]:
        """Basic entity extraction without spaCy"""
        entities = []
        
        # Extract common patterns
        patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
            'url': r'\bhttps?://[^\s]+\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'number': r'\b\d+(?:\.\d+)?\b',
            'date': r'\b\d{1,4}[-/]\d{1,2}[-/]\d{2,4}\b',
            'time': r'\b\d{1,2}:\d{2}(?::\d{2})?\b'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                entity = TextEntity(
                    text=match.group(),
                    entity_type=entity_type,
                    confidence=0.8,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    context=text[max(0, match.start()-20):match.end()+20]
                )
                entities.append(entity)
        
        return entities
    
    def _classify_intent(self, text: str) -> IntentCategory:
        """Classify user intent with high accuracy"""
        text_lower = text.lower()
        
        # Check each intent category
        intent_scores = {}
        
        for category in IntentCategory:
            score = 0
            if category == IntentCategory.PROGRAMMING:
                score = sum(1 for pattern in self.patterns['programming'] if pattern.search(text_lower))
            elif category == IntentCategory.SYSTEM_OPERATION:
                score = sum(1 for pattern in self.patterns['system_operations'] if pattern.search(text_lower))
            elif category == IntentCategory.DATA_ANALYSIS:
                score = sum(1 for pattern in self.patterns['data_analysis'] if pattern.search(text_lower))
            elif category == IntentCategory.LEARNING_REQUEST:
                score = sum(1 for pattern in self.patterns['learning_requests'] if pattern.search(text_lower))
            elif category == IntentCategory.EMOTIONAL_SUPPORT:
                score = sum(1 for pattern in pattern in self.patterns['emotional_support'] if pattern.search(text_lower))
            elif category == IntentCategory.CREATIVE_TASK:
                score = sum(1 for pattern in self.patterns['creative_tasks'] if pattern.search(text_lower))
            
            intent_scores[category] = score
        
        # Return the intent with highest score
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return IntentCategory.CONVERSATION
    
    def _assess_complexity(self, text: text) -> TextComplexity:
        """Assess text complexity"""
        text_lower = text.lower()
        
        complexity_indicators = self.semantic_rules['complexity_indicators']
        
        # Check complexity indicators
        if any(indicator in text_lower for indicator in complexity_indicators['expert']):
            return TextComplexity.EXPERT
        elif any(indicator in text_lower for indicator in complexity_indicators['complex']):
            return TextComplexity.COMPLEX
        elif any(indicator in text_lower for indicator in complexity_indicators['moderate']):
            return TextComplexity.MODERATE
        else:
            return TextComplexity.SIMPLE
    
    def _classify_domain(self, text: str) -> List[str]:
        """Classify knowledge domains"""
        text_lower = text.lower()
        domains = []
        
        for domain, terms in self.knowledge_domains.items():
            if any(term.lower() in text_lower for term in terms):
                domains.append(domain)
        
        return domains
    
    def _map_relationships(self, text: str) -> Dict[str, List[str]]:
        """Map relationships between entities and concepts"""
        relationships = {}
        
        # Extract entities
        entities = self._extract_entities(text)
        
        # Simple relationship mapping based on proximity
        for i, entity1 in enumerate(entities):
            related = []
            for entity2 in entities[i+1:]:
                # Check if entities are close in text
                if entity2.start_pos - entity1.end_pos < 50:  # Within 50 characters
                    related.append(entity2.text)
            
            if related:
                relationships[entity1.text] = related
        
        return relationships
    
    def _calculate_confidence_scores(self, text: str) -> Dict[str, float]:
        """Calculate confidence scores for different aspects"""
        scores = {}
        
        # Length-based confidence
        if len(text) > 0:
            length_confidence = min(1.0, len(text) / 100)  # Normalize to 0-1
            scores['length'] = length_confidence
        
        # Pattern-based confidence
        pattern_matches = 0
        for patterns in self.patterns.values():
            pattern_matches += sum(1 for pattern in patterns if pattern.search(text))
        
        if pattern_matches > 0:
            pattern_confidence = min(1.0, pattern_matches / 10)  # Normalize to 0-1
            scores['patterns'] = pattern_confidence
        
        # Entity-based confidence
        entities = self._extract_entities(text)
        if entities:
            entity_confidence = min(1.0, len(entities) / 5)  # Normalize to 0-1
            scores['entities'] = entity_confidence
        
        # Overall confidence
        if scores:
            scores['overall'] = sum(scores.values()) / len(scores)
        else:
            scores['overall'] = 0.5  # Default confidence
        
        return scores
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text"""
        # Simple language detection based on character patterns
        if re.search(r'[^\w\s]', text):  # Non-ASCII characters
            return 'non-english'
        elif re.search(r'[а-яА-Я]', text):  # Cyrillic
            return 'russian'
        elif re.search('[一-龥]', text):  # Chinese
            return 'chinese'
        elif re.search('[가-힣]', text):  # Korean
            return 'korean'
        elif re.search('[あ-んア-ン]', text):  # Japanese
            return 'japanese'
        elif re.search('[א-ת]', text):  # Hebrew
            return 'hebrew'
        elif re.search('[أ-ي]', text):  # Arabic
            return 'arabic'
        else:
            return 'english'
    
    def _determine_main_topic(self, text: str, key_concepts: List[str]) -> str:
        """Determine main topic from text and concepts"""
        # Simple heuristic: most frequent concept
        if key_concepts:
            return max(set(key_concepts), key=key_concepts.count)
        
        # Extract keywords
        words = [word.lower() for word in text.split() if len(word) > 3]
        if words:
            return max(set(words), key=words.count)
        
        return "general"
    
    def _extract_subtopics(self, text: str, key_concepts: List[str]) -> List[str]:
        """Extract subtopics from text"""
        subtopics = []
        
        # Use key concepts as subtopics
        subtopics.extend(key_concepts)
        
        # Add other important terms
        words = [word.lower() for word in text.split() if len(word) > 4]
        for word in words:
            if word not in subtopics and word not in self.semantic_rules['question_indicators']:
                subtopics.append(word)
        
        return list(set(subtopics[:10]))  # Limit to top 10
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'happy', 'excited', 'proud']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'sad', 'angry', 'frustrated', 'worried', 'confused']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _assess_urgency(self, text: str) -> str:
        """Assess urgency of text"""
        urgent_words = ['urgent', 'emergency', 'immediately', 'asap', 'critical', 'important', 'now', 'quickly', 'fast']
        
        text_lower = text.lower()
        if any(word in text_lower for word in urgent_words):
            return 'high'
        elif any(word in text_lower for word in ['please', 'help', 'need', 'want']):
            return 'medium'
        else:
            return 'low'
    
    def _determine_conversation_stage(self, text: str) -> str:
        """Determine conversation stage"""
        if not self.context_memory:
            return 'initial'
        elif len(self.context_memory) < 3:
            return 'early'
        elif len(self.context_memory) < 10:
            return 'middle'
        else:
            return 'established'
    
    def _identify_user_intent(self, text: str) -> str:
        """Identify user intent"""
        text_lower = text.lower()
        
        if any(indicator in text_lower for indicator in self.semantic_rules['question_indicators']):
            return 'question'
        elif any(indicator in text_lower for indicator in self.semantic_rules['command_indicators']):
            return 'command'
        elif any(indicator in text_lower for indicator in self.semantic_rules['request_indicators']):
            return 'request'
        else:
            return 'statement'
    
    def _determine_required_actions(self, text: str) -> List[str]:
        """Determine required actions from text"""
        actions = []
        
        text_lower = text.lower()
        
        # Check for action verbs
        action_verbs = ['create', 'make', 'build', 'write', 'generate', 'run', 'execute', 'start', 'stop', 'delete', 'move', 'copy', 'open', 'close']
        
        for verb in action_verbs:
            if verb in text_lower:
                actions.append(verb)
        
        return actions
    
    def _determine_response_type(self, text: str) -> str:
        """Determine expected response type"""
        text_lower = text.lower()
        
        if any(indicator in text_lower for indicator in self.semantic_rules['question_indicators']):
            return 'answer'
        elif any(indicator in text_lower for indicator in self.semantic_rules['command_indicators']):
            return 'execution_result'
        elif any(indicator in text_lower for indicator in self.semantic_rules['request_indicators']):
            return 'assistance'
        else:
            return 'acknowledgment'
    
    def _identify_domain_knowledge(self, text: str) -> List[str]:
        """Identify domain knowledge required"""
        return self._classify_domain(text)
    
    def _calculate_confidence_score(self, text: str) -> float:
        """Calculate overall confidence score"""
        scores = self._calculate_confidence_scores(text)
        return scores.get('overall', 0.5)
    
    def parse_text_message(self, message: str) -> Dict[str, Any]:
        """Main method to parse text message comprehensively"""
        return self.analyze_text_comprehensive(message)

# Global instance
advanced_parser = AdvancedTextParser()
