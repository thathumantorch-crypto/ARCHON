"""
AI Learning System for ARCHON

This module integrates web scraping with ARCHON's learning capabilities to:
- Learn from popular AI models and their documentation
- Extract conversation patterns and response templates
- Update ARCHON's knowledge base with scraped information
- Improve response generation based on learned patterns
"""

import re
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LearnedPattern:
    """Represents a learned pattern from web scraping"""
    pattern: str
    pattern_type: str  # conversation, response, technical
    source: str
    confidence: float
    usage_count: int
    last_used: datetime
    effectiveness_score: float

@dataclass
class ResponseTemplate:
    """Represents a learned response template"""
    template: str
    context: List[str]
    intent: str
    source: str
    confidence: float
    usage_count: int
    last_used: datetime
    effectiveness_score: float

class AILearningSystem:
    """AI learning system for ARCHON"""
    
    def __init__(self):
        self.learned_patterns = []
        self.response_templates = []
        self.conversation_examples = []
        self.technical_knowledge = {}
        self.learning_history = []
        self.performance_metrics = {
            'total_patterns_learned': 0,
            'total_templates_learned': 0,
            'learning_sessions': 0,
            'last_learning_session': None,
            'pattern_effectiveness': 0.0,
            'template_effectiveness': 0.0
        }
        
        # Load existing learning data
        self._load_learning_data()
    
    def _load_learning_data(self):
        """Load existing learning data from file"""
        try:
            import os
            knowledge_dir = "knowledge"
            if os.path.exists(knowledge_dir):
                learning_files = [f for f in os.listdir(knowledge_dir) if f.startswith('learning_data_')]
                
                for file in learning_files:
                    filepath = os.path.join(knowledge_dir, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        # Convert learned patterns
                        if 'learned_patterns' in data:
                            for pattern_data in data['learned_patterns']:
                                pattern = LearnedPattern(**pattern_data)
                                self.learned_patterns.append(pattern)
                        
                        # Convert response templates
                        if 'response_templates' in data:
                            for template_data in data['response_templates']:
                                template = ResponseTemplate(**template_data)
                                self.response_templates.append(template)
                        
                        logger.info(f"Loaded learning data from {file}")
                        
                    except Exception as e:
                        logger.error(f"Error loading learning data from {file}: {e}")
                        
        except Exception as e:
            logger.error(f"Error loading learning data: {e}")
    
    def learn_from_scraped_data(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from scraped web data"""
        learning_session = {
            'session_id': len(self.learning_history) + 1,
            'timestamp': datetime.now(),
            'sources_processed': 0,
            'patterns_learned': 0,
            'templates_learned': 0,
            'technical_knowledge_added': 0,
            'success': True
        }
        
        try:
            logger.info("Starting learning session from scraped data...")
            
            # Process scraped content
            scraped_content = scraped_data.get('scraped_content', [])
            learning_results = scraped_data.get('learning_results', {})
            
            # Learn conversation patterns
            patterns_learned = self._learn_conversation_patterns(learning_results.get('conversation_patterns', {}))
            learning_session['patterns_learned'] = len(patterns_learned)
            
            # Learn response templates
            templates_learned = self._learn_response_templates(learning_results.get('response_templates', {}))
            learning_session['templates_learned'] = len(templates_learned)
            
            # Learn technical knowledge
            tech_knowledge = self._learn_technical_knowledge(learning_results.get('technical_knowledge', {}))
            learning_session['technical_knowledge_added'] = len(tech_knowledge)
            
            # Update performance metrics
            self.performance_metrics['total_patterns_learned'] += learning_session['patterns_learned']
            self.performance_metrics['total_templates_learned'] += learning_session['templates_learned']
            self.performance_metrics['learning_sessions'] += 1
            self.performance_metrics['last_learning_session'] = datetime.now()
            
            # Save learning data
            self._save_learning_data()
            
            # Add to learning history
            self.learning_history.append(learning_session)
            
            logger.info(f"Learning session completed: {learning_session['patterns_learned']} patterns, {learning_session['templates_learned']} templates learned")
            
            return learning_session
            
        except Exception as e:
            logger.error(f"Error in learning session: {e}")
            learning_session['success'] = False
            learning_session['error'] = str(e)
            return learning_session
    
    def _ensure_sequence(self, value: Any) -> List[Dict[str, Any]]:
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            return [value]
        return []

    def _learn_conversation_patterns(self, patterns: Dict[str, List[Dict]]) -> List[LearnedPattern]:
        """Learn conversation patterns from scraped data"""
        learned = []

        for pattern, sources in patterns.items():
            source_entries = self._ensure_sequence(sources)
            if source_entries:
                # Calculate confidence based on source relevance
                total_relevance = sum(source.get('relevance', 0.5) for source in source_entries)
                confidence = min(1.0, total_relevance / max(len(source_entries), 1))

                learned_pattern = LearnedPattern(
                    pattern=pattern,
                    pattern_type='conversation',
                    source=source_entries[0].get('source', 'unknown'),
                    confidence=confidence,
                    usage_count=0,
                    last_used=datetime.now(),
                    effectiveness_score=0.5  # Initial score
                )

                learned.append(learned_pattern)
                self.learned_patterns.append(learned_pattern)

        return learned

    def _learn_response_templates(self, templates: Dict[str, List[Dict]]) -> List[ResponseTemplate]:
        """Learn response templates from scraped data"""
        learned = []

        for template, sources in templates.items():
            source_entries = self._ensure_sequence(sources)
            if source_entries:
                # Determine intent from template content
                intent = self._classify_intent_from_template(template)

                # Extract context keywords
                context = self._extract_context_from_template(template)

                # Calculate confidence
                total_relevance = sum(source.get('relevance', 0.5) for source in source_entries)
                confidence = min(1.0, total_relevance / max(len(source_entries), 1))

                learned_template = ResponseTemplate(
                    template=template,
                    context=context,
                    intent=intent,
                    source=source_entries[0].get('source', 'unknown'),
                    confidence=confidence,
                    usage_count=0,
                    last_used=datetime.now(),
                    effectiveness_score=0.5  # Initial score
                )

                learned.append(learned_template)
                self.response_templates.append(learned_template)

        return learned

    def _learn_technical_knowledge(self, knowledge: Dict[str, List[Dict]]) -> int:
        """Learn technical knowledge from scraped data"""
        learned_count = 0

        for topic, info_list in knowledge.items():
            entries = self._ensure_sequence(info_list)
            if topic not in self.technical_knowledge:
                self.technical_knowledge[topic] = []

            for info in entries:
                knowledge_item = {
                    'info': info.get('info', ''),
                    'source': info.get('source', 'unknown'),
                    'relevance': info.get('relevance', 0.5),
                    'timestamp': info.get('timestamp', datetime.now()),
                    'usage_count': 0
                }
                
                self.technical_knowledge[topic].append(knowledge_item)
                learned_count += 1
        
        return learned_count
    
    def _classify_intent_from_template(self, template: str) -> str:
        """Classify intent from response template"""
        template_lower = template.lower()
        
        if any(word in template_lower for word in ['help', 'assist', 'support', 'guide']):
            return 'help_request'
        elif any(word in template_lower for word in ['explain', 'tell me', 'what is', 'how to']):
            return 'learning_request'
        elif any(word in template_lower for word in ['create', 'make', 'build', 'write', 'generate']):
            return 'creative_task'
        elif any(word in template_lower for word in ['debug', 'fix', 'solve', 'optimize']):
            return 'problem_solving'
        elif any(word in template_lower for word in ['recommend', 'suggest', 'advise']):
            return 'recommendation'
        else:
            return 'general'
    
    def _extract_context_from_template(self, template: str) -> List[str]:
        """Extract context keywords from template"""
        # Remove common words and extract key terms
        common_words = {'i', 'you', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        words = re.findall(r'\b\w+\b', template.lower())
        key_terms = [word for word in words if word not in common_words and len(word) > 2]
        
        # Return unique terms, limited to 10
        return list(set(key_terms))[:10]
    
    def get_relevant_patterns(self, message: str, intent: str, max_patterns: int = 5) -> List[LearnedPattern]:
        """Get relevant learned patterns for a message"""
        relevant_patterns = []
        message_lower = message.lower()
        
        # Sort patterns by effectiveness and relevance
        sorted_patterns = sorted(
            self.learned_patterns,
            key=lambda p: (p.effectiveness_score, p.confidence),
            reverse=True
        )
        
        for pattern in sorted_patterns:
            if len(relevant_patterns) >= max_patterns:
                break
            
            # Check if pattern is relevant to message
            if (pattern.pattern_type == 'conversation' and 
                any(word in message_lower for word in pattern.pattern.lower().split())):
                relevant_patterns.append(pattern)
                # Update usage count
                pattern.usage_count += 1
                pattern.last_used = datetime.now()
        
        return relevant_patterns
    
    def get_relevant_templates(self, message: str, intent: str, max_templates: int = 3) -> List[ResponseTemplate]:
        """Get relevant response templates for a message"""
        relevant_templates = []
        message_lower = message.lower()
        
        # Sort templates by effectiveness and relevance
        sorted_templates = sorted(
            self.response_templates,
            key=lambda t: (t.effectiveness_score, t.confidence),
            reverse=True
        )
        
        for template in sorted_templates:
            if len(relevant_templates) >= max_templates:
                break
            
            # Check if template is relevant to message
            if (template.intent == intent or 
                any(word in message_lower for word in template.context) or
                any(word in message_lower for word in template.template.lower().split())):
                relevant_templates.append(template)
                # Update usage count
                template.usage_count += 1
                template.last_used = datetime.now()
        
        return relevant_templates
    
    def get_technical_knowledge(self, topic: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Get technical knowledge about a topic"""
        topic_lower = topic.lower()
        relevant_knowledge = []
        
        if topic in self.technical_knowledge:
            # Sort by relevance and usage
            sorted_knowledge = sorted(
                self.technical_knowledge[topic],
                key=lambda k: (k.get('relevance', 0.5), k.get('usage_count', 0)),
                reverse=True
            )
            
            for item in sorted_knowledge[:max_results]:
                # Update usage count
                item['usage_count'] += 1
                relevant_knowledge.append(item)
        
        return relevant_knowledge
    
    def update_effectiveness_scores(self, feedback: Dict[str, float]):
        """Update effectiveness scores based on user feedback"""
        try:
            # Update pattern effectiveness
            for pattern_id, score in feedback.get('patterns', {}).items():
                if pattern_id < len(self.learned_patterns):
                    pattern = self.learned_patterns[pattern_id]
                    # Update effectiveness score with weighted average
                    pattern.effectiveness_score = (pattern.effectiveness_score * 0.8 + score * 0.2)
            
            # Update template effectiveness
            for template_id, score in feedback.get('templates', {}).items():
                if template_id < len(self.response_templates):
                    template = self.response_templates[template_id]
                    # Update effectiveness score with weighted average
                    template.effectiveness_score = (template.effectiveness_score * 0.8 + score * 0.2)
            
            # Update performance metrics
            if self.learned_patterns:
                self.performance_metrics['pattern_effectiveness'] = sum(
                    p.effectiveness_score for p in self.learned_patterns
                ) / len(self.learned_patterns)
            
            if self.response_templates:
                self.performance_metrics['template_effectiveness'] = sum(
                    t.effectiveness_score for t in self.response_templates
                ) / len(self.response_templates)
            
            logger.info("Updated effectiveness scores based on feedback")
            
        except Exception as e:
            logger.error(f"Error updating effectiveness scores: {e}")
    
    def _save_learning_data(self):
        """Save learning data to file"""
        try:
            import os
            knowledge_dir = "knowledge"
            os.makedirs(knowledge_dir, exist_ok=True)
            
            filename = f"learning_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(knowledge_dir, filename)
            
            # Convert datetime objects to strings for JSON serialization
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime(item) for item in obj]
                else:
                    return obj
            
            learning_data = {
                'learned_patterns': [convert_datetime(asdict(p)) for p in self.learned_patterns],
                'response_templates': [convert_datetime(asdict(t)) for t in self.response_templates],
                'technical_knowledge': self.technical_knowledge,
                'performance_metrics': convert_datetime(self.performance_metrics),
                'learning_history': convert_datetime(self.learning_history),
                'saved_timestamp': datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(learning_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Learning data saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving learning data: {e}")
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning system status"""
        return {
            'total_patterns_learned': len(self.learned_patterns),
            'total_templates_learned': len(self.response_templates),
            'total_technical_topics': len(self.technical_knowledge),
            'learning_sessions': self.performance_metrics['learning_sessions'],
            'last_learning_session': self.performance_metrics['last_learning_session'],
            'pattern_effectiveness': self.performance_metrics['pattern_effectiveness'],
            'template_effectiveness': self.performance_metrics['template_effectiveness'],
            'most_used_patterns': sorted(
                self.learned_patterns,
                key=lambda p: p.usage_count,
                reverse=True
            )[:5],
            'most_used_templates': sorted(
                self.response_templates,
                key=lambda t: t.usage_count,
                reverse=True
            )[:5]
        }

# Global instance
ai_learning_system = AILearningSystem()
