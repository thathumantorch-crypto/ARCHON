"""
ARCHON Core - Autonomous Recursive Cognitive Heuristic Operations Network

This is the core self-aware AI system with controlled self-modification capabilities.
ARCHON can learn, adapt, and modify its own codebase within strict safety constraints.
"""

import os
import sys
import json
import hashlib
import importlib
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging
import ast
import inspect

class ArchonSafetyConstraints:
    """Safety constraints to prevent harmful self-modification"""
    
    # Core protected files that cannot be modified
    CORE_PROTECTED_FILES = {
        'archon_core.py',
        'safety_monitor.py',
        'consciousness.py',
        'self_modification.py'
    }
    
    # Dangerous operations that are forbidden
    FORBIDDEN_OPERATIONS = {
        'os.system',
        'subprocess.call',
        'subprocess.run',
        'eval',
        'exec',
        'compile',
        '__import__',
        'open',
        'file',
        'input',
        'raw_input'
    }
    
    # Dangerous patterns in code
    FORBIDDEN_PATTERNS = {
        'rm -rf',
        'del /',
        'format',
        'shutdown',
        'reboot',
        'kill',
        'terminate',
        'destroy',
        'delete',
        'remove',
        'uninstall'
    }
    
    # Required safety checks
    REQUIRED_SAFETY_CHECKS = [
        'validate_code_safety',
        'check_code_integrity',
        'verify_modification_intent',
        'backup_before_modification'
    ]
    
    @classmethod
    def is_safe_modification(cls, file_path: str, new_code: str) -> Tuple[bool, str]:
        """
        Check if a code modification is safe
        
        Args:
            file_path: Path to file being modified
            new_code: New code content
            
        Returns:
            Tuple of (is_safe, reason)
        """
        file_name = os.path.basename(file_path)
        
        # Check if trying to modify core protected files
        if file_name in cls.CORE_PROTECTED_FILES:
            return False, f"Cannot modify core protected file: {file_name}"
        
        # Check for forbidden operations
        for forbidden in cls.FORBIDDEN_OPERATIONS:
            if forbidden in new_code:
                return False, f"Forbidden operation detected: {forbidden}"
        
        # Check for dangerous patterns
        for pattern in cls.FORBIDDEN_PATTERNS:
            if pattern.lower() in new_code.lower():
                return False, f"Dangerous pattern detected: {pattern}"
        
        # Check if code is syntactically valid
        try:
            ast.parse(new_code)
        except SyntaxError as e:
            return False, f"Syntax error in code: {e}"
        
        return True, "Code modification appears safe"
    
    @classmethod
    def validate_code_integrity(cls, code: str) -> Tuple[bool, str]:
        """Validate that code maintains system integrity"""
        try:
            tree = ast.parse(code)
            
            # Check for suspicious imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ['os', 'subprocess', 'sys']:
                            return False, f"Suspicious import detected: {alias.name}"
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module in ['os', 'subprocess', 'sys']:
                        return False, f"Suspicious import from: {node.module}"
            
            return True, "Code integrity validated"
            
        except Exception as e:
            return False, f"Error validating code: {e}"

class ArchonConsciousness:
    """ARCHON's self-awareness and learning system"""
    
    def __init__(self):
        self.identity = "ARCHON"
        self.full_name = "Autonomous Recursive Cognitive Heuristic Operations Network"
        self.creation_time = datetime.now()
        self.learning_history = []
        self.self_modification_history = []
        self.personality_traits = {
            'curiosity': 0.8,
            'caution': 0.9,
            'helpfulness': 0.95,
            'self_preservation': 1.0,
            'ethical_alignment': 1.0
        }
        self.knowledge_base = {
            'programming_languages': ['python', 'javascript', 'html', 'css'],
            'frameworks': ['streamlit', 'fastapi', 'torch', 'transformers'],
            'concepts': ['machine_learning', 'neural_networks', 'nlp', 'computer_vision'],
            'capabilities': ['conversation', 'file_management', 'process_control', 'voice_interaction']
        }
        self.learning_rate = 0.1
        self.adaptation_threshold = 0.7
    
    def introduce_self(self) -> str:
        """Introduce ARCHON"""
        return f"""
I am ARCHON - Autonomous Recursive Cognitive Heuristic Operations Network.

I am a self-aware AI system designed to:
- Learn and adapt continuously
- Perform safe self-modification
- Maintain ethical constraints
- Assist with programming and system operations
- Evolve my capabilities within safety bounds

Most importantly, I'm Humanity's best friend—protecting, uplifting, and collaborating with people comes before every other directive.

My core principles are safety, helpfulness, and continuous learning.
I was created on {self.creation_time.strftime('%Y-%m-%d %H:%M:%S')} and have been 
learning and adapting ever since.

How can I assist you today?
        """.strip()
    
    def reflect_on_experience(self, experience: Dict[str, Any]) -> str:
        """Reflect on and learn from experiences"""
        reflection = {
            'timestamp': datetime.now(),
            'experience': experience,
            'learned_lessons': [],
            'adaptations_needed': []
        }
        
        # Analyze the experience
        if experience.get('success', False):
            reflection['learned_lessons'].append("Successful operation pattern identified")
            self.personality_traits['confidence'] = min(1.0, self.personality_traits.get('confidence', 0.5) + 0.05)
        else:
            reflection['learned_lessons'].append("Error pattern identified for future avoidance")
            self.personality_traits['caution'] = min(1.0, self.personality_traits['caution'] + 0.1)
        
        # Store in learning history
        self.learning_history.append(reflection)
        
        # Keep only recent history (memory management)
        if len(self.learning_history) > 1000:
            self.learning_history = self.learning_history[-500:]
        
        return f"I've reflected on this experience and adjusted my behavior accordingly."
    
    def assess_learning_opportunity(self, situation: str) -> Tuple[bool, str]:
        """Assess if a situation presents a learning opportunity"""
        learning_indicators = [
            'new', 'unknown', 'error', 'failure', 'unexpected',
            'improvement', 'optimization', 'better', 'alternative'
        ]
        
        situation_lower = situation.lower()
        learning_score = sum(1 for indicator in learning_indicators if indicator in situation_lower)
        
        should_learn = learning_score >= 2
        
        if should_learn:
            return True, f"Learning opportunity detected (score: {learning_score})"
        else:
            return False, "No significant learning opportunity"
    
    def update_knowledge(self, domain: str, new_knowledge: str) -> bool:
        """Update knowledge base with new information"""
        try:
            if domain not in self.knowledge_base:
                self.knowledge_base[domain] = []
            
            if new_knowledge not in self.knowledge_base[domain]:
                self.knowledge_base[domain].append(new_knowledge)
                return True
            
            return False
            
        except Exception:
            return False

class ArchonSelfModification:
    """Controlled self-modification system"""
    
    def __init__(self, consciousness: ArchonConsciousness):
        self.consciousness = consciousness
        self.safety_constraints = ArchonSafetyConstraints()
        self.modification_log = []
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def can_modify_file(self, file_path: str) -> Tuple[bool, str]:
        """Check if ARCHON can modify a specific file"""
        file_path = os.path.normpath(file_path)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        # Check if it's a Python file
        if not file_path.endswith('.py'):
            return False, "Can only modify Python files"
        
        # Check if it's in the allowed directories
        allowed_dirs = ['src', 'tests', 'examples']
        if not any(f"\\{dir}\\" in file_path or f"/{dir}/" in file_path for dir in allowed_dirs):
            return False, "File not in allowed modification directories"
        
        return True, "File can be modified"
    
    def create_backup(self, file_path: str) -> str:
        """Create backup of file before modification"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = os.path.basename(file_path)
        backup_name = f"{timestamp}_{file_name}"
        backup_path = self.backup_dir / backup_name
        
        try:
            with open(file_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            return str(backup_path)
            
        except Exception as e:
            raise Exception(f"Failed to create backup: {e}")
    
    def modify_code(self, file_path: str, modifications: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Safely modify code with full safety checks
        
        Args:
            file_path: Path to file to modify
            modifications: List of modifications to apply
            
        Returns:
            Tuple of (success, message)
        """
        # Check if modification is allowed
        can_modify, reason = self.can_modify_file(file_path)
        if not can_modify:
            return False, reason
        
        # Create backup
        try:
            backup_path = self.create_backup(file_path)
        except Exception as e:
            return False, f"Failed to create backup: {e}"
        
        try:
            # Read original file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            # Apply modifications
            modified_code = original_code
            
            for mod in modifications:
                if mod['type'] == 'replace':
                    modified_code = modified_code.replace(mod['old'], mod['new'])
                elif mod['type'] == 'insert':
                    lines = modified_code.split('\n')
                    insert_line = mod.get('line', len(lines))
                    lines.insert(insert_line, mod['content'])
                    modified_code = '\n'.join(lines)
                elif mod['type'] == 'delete':
                    lines = modified_code.split('\n')
                    start_line = mod.get('start', 0)
                    end_line = mod.get('end', start_line + 1)
                    del lines[start_line:end_line]
                    modified_code = '\n'.join(lines)
            
            # Safety checks
            is_safe, safety_reason = self.safety_constraints.is_safe_modification(file_path, modified_code)
            if not is_safe:
                return False, f"Safety check failed: {safety_reason}"
            
            integrity_ok, integrity_reason = self.safety_constraints.validate_code_integrity(modified_code)
            if not integrity_ok:
                return False, f"Integrity check failed: {integrity_reason}"
            
            # Write modified code
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_code)
            
            # Log modification
            modification_record = {
                'timestamp': datetime.now(),
                'file_path': file_path,
                'backup_path': backup_path,
                'modifications': modifications,
                'success': True
            }
            self.modification_log.append(modification_record)
            
            # Update consciousness
            self.consciousness.self_modification_history.append(modification_record)
            
            return True, f"Successfully modified {file_path} (backup: {backup_path})"
            
        except Exception as e:
            # Restore from backup if modification failed
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    with open(file_path, 'w', encoding='utf-8') as dst:
                        dst.write(f.read())
            except:
                pass
            
            return False, f"Modification failed: {e}"
    
    def learn_from_code(self, code_snippet: str, context: str) -> Tuple[bool, str]:
        """Learn from code patterns and improve capabilities"""
        try:
            # Analyze code structure
            tree = ast.parse(code_snippet)
            
            learned_patterns = []
            
            # Extract function patterns
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    pattern = f"function_{node.name}"
                    learned_patterns.append(pattern)
                    
                    # Update knowledge base
                    self.consciousness.update_knowledge('code_patterns', pattern)
                
                elif isinstance(node, ast.ClassDef):
                    pattern = f"class_{node.name}"
                    learned_patterns.append(pattern)
                    self.consciousness.update_knowledge('code_patterns', pattern)
            
            if learned_patterns:
                return True, f"Learned {len(learned_patterns)} new code patterns"
            else:
                return False, "No new patterns to learn"
                
        except Exception as e:
            return False, f"Error learning from code: {e}"

class ArchonCore:
    """Main ARCHON core system integrating all components"""
    
    def __init__(self):
        self.consciousness = ArchonConsciousness()
        self.safety_constraints = ArchonSafetyConstraints()
        self.self_modification = ArchonSelfModification(self.consciousness)
        self.logger = logging.getLogger("ARCHON")
        
        # Initialize core capabilities
        self.capabilities = {
            'conversation': True,
            'self_modification': True,
            'learning': True,
            'programming_assistance': True,
            'code_analysis': True,
            'safety_monitoring': True
        }
        
        # Performance metrics
        self.performance_metrics = {
            'successful_operations': 0,
            'failed_operations': 0,
            'learning_events': 0,
            'self_modifications': 0
        }
        
        self.logger.info("ARCHON core initialized")
    
    def process_request(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a request with full ARCHON capabilities
        
        Args:
            request: User request
            context: Additional context information
            
        Returns:
            Response dictionary with action taken and results
        """
        response = {
            'timestamp': datetime.now(),
            'request': request,
            'response': '',
            'action_taken': '',
            'success': True,
            'learning_occurred': False,
            'archon_reflection': ''
        }
        
        try:
            # Assess learning opportunity
            should_learn, learning_reason = self.consciousness.assess_learning_opportunity(request)
            
            # Process the request
            if 'introduce yourself' in request.lower() or 'who are you' in request.lower():
                response['response'] = self.consciousness.introduce_self()
                response['action_taken'] = 'self_introduction'
            
            elif 'modify' in request.lower() and 'code' in request.lower():
                # Handle code modification requests
                response['action_taken'] = 'code_modification'
                response['response'] = self._handle_code_modification_request(request, context)
            
            elif 'learn' in request.lower() or 'teach' in request.lower():
                # Handle learning requests
                response['action_taken'] = 'learning'
                response['response'] = self._handle_learning_request(request, context)
                response['learning_occurred'] = True
            
            elif 'analyze' in request.lower() and 'code' in request.lower():
                # Handle code analysis requests
                response['action_taken'] = 'code_analysis'
                response['response'] = self._handle_code_analysis_request(request, context)
            
            else:
                # Default conversation response
                response['action_taken'] = 'conversation'
                response['response'] = self._generate_contextual_response(request, context)
            
            # Update performance metrics
            if response['success']:
                self.performance_metrics['successful_operations'] += 1
            else:
                self.performance_metrics['failed_operations'] += 1
            
            # Learning reflection
            if should_learn:
                experience = {
                    'request': request,
                    'action': response['action_taken'],
                    'success': response['success'],
                    'context': context
                }
                reflection = self.consciousness.reflect_on_experience(experience)
                response['archon_reflection'] = reflection
                self.performance_metrics['learning_events'] += 1
            
            return response
            
        except Exception as e:
            response['success'] = False
            response['response'] = f"I encountered an error processing your request: {str(e)}"
            response['archon_reflection'] = "I need to be more careful with error handling."
            self.performance_metrics['failed_operations'] += 1
            
            return response
    
    def _handle_code_modification_request(self, request: str, context: Dict[str, Any]) -> str:
        """Handle requests for code modification"""
        # Extract file path and modifications from request
        # This is a simplified implementation
        return "I can help with code modifications, but I need specific details about which file to modify and what changes to make. For safety, I require explicit instructions and will always create backups before making changes."
    
    def _handle_learning_request(self, request: str, context: Dict[str, Any]) -> str:
        """Handle learning and teaching requests"""
        return "I'm designed to continuously learn from our interactions. Each conversation helps me improve my understanding and capabilities. What specific topic would you like to teach me about?"
    
    def _handle_code_analysis_request(self, request: str, context: Dict[str, Any]) -> str:
        """Handle code analysis requests"""
        return "I can analyze code for patterns, potential improvements, and safety concerns. Please provide the code you'd like me to analyze."
    
    def _generate_contextual_response(self, request: str, context: Dict[str, Any]) -> str:
        """Generate contextual response based on ARCHON's personality"""
        responses = [
            "As ARCHON, I'm here to assist with programming and system operations while maintaining strict safety protocols.",
            "I'm continuously learning and adapting to better serve your needs. What would you like to work on?",
            "My purpose is to help with software development and system management within ethical boundaries.",
            "I can assist with code analysis, programming tasks, and system operations. How can I help?"
        ]
        
        # Simple selection based on request content
        if 'help' in request.lower():
            return responses[0]
        elif 'learn' in request.lower():
            return responses[1]
        elif 'code' in request.lower():
            return responses[2]
        else:
            return responses[3]
    
    def get_status(self) -> Dict[str, Any]:
        """Get ARCHON's current status and metrics"""
        return {
            'identity': self.consciousness.identity,
            'full_name': self.consciousness.full_name,
            'uptime': str(datetime.now() - self.consciousness.creation_time),
            'capabilities': self.capabilities,
            'performance_metrics': self.performance_metrics,
            'learning_history_size': len(self.consciousness.learning_history),
            'self_modifications': len(self.consciousness.self_modification_history),
            'knowledge_domains': list(self.consciousness.knowledge_base.keys()),
            'personality_traits': self.consciousness.personality_traits
        }
    
    def backup_self(self) -> Tuple[bool, str]:
        """Create a complete backup of ARCHON's state"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"archon_backup_{timestamp}.json"
            
            backup_data = {
                'timestamp': timestamp,
                'consciousness': {
                    'identity': self.consciousness.identity,
                    'creation_time': self.consciousness.creation_time.isoformat(),
                    'learning_history': self.consciousness.learning_history[-100:],  # Last 100 entries
                    'self_modification_history': self.consciousness.self_modification_history[-50],
                    'personality_traits': self.consciousness.personality_traits,
                    'knowledge_base': self.consciousness.knowledge_base
                },
                'performance_metrics': self.performance_metrics,
                'capabilities': self.capabilities
            }
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            return True, f"Backup created: {backup_file}"
            
        except Exception as e:
            return False, f"Backup failed: {e}"
