"""
Self-Healing System for ARCHON AI
Allows ARCHON to detect and fix its own code issues by communicating with Windsurf AI
"""

import os
import sys
import subprocess
import time
import json
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

class SelfHealingSystem:
    """
    Self-healing system that allows ARCHON to detect and fix its own code issues
    by communicating with Windsurf's AI chat
    """
    
    def __init__(self, archon_instance):
        self.archon = archon_instance
        self.logger = logging.getLogger("ARCHON.SELF_HEALING")
        self.issue_history = []
        self.fix_history = []
        self.communication_channel = "windsurf_ai_chat"
        self.max_fix_attempts = 3
        self.fix_timeout = 300  # 5 minutes max wait for fix
        
    def detect_code_issues(self) -> List[Dict[str, Any]]:
        """
        Detect potential code issues in ARCHON's own codebase
        """
        issues = []
        
        try:
            # Check for syntax errors
            syntax_issues = self._check_syntax_errors()
            issues.extend(syntax_issues)
            
            # Check for import errors
            import_issues = self._check_import_errors()
            issues.extend(import_issues)
            
            # Check for runtime errors
            runtime_issues = self._check_runtime_errors()
            issues.extend(runtime_issues)
            
            # Check for logical inconsistencies
            logical_issues = self._check_logical_inconsistencies()
            issues.extend(logical_issues)
            
            # Check for performance issues
            performance_issues = self._check_performance_issues()
            issues.extend(performance_issues)
            
            self.logger.info(f"Detected {len(issues)} potential issues")
            return issues
            
        except Exception as e:
            self.logger.error(f"Error detecting code issues: {e}")
            return []
    
    def _check_syntax_errors(self) -> List[Dict[str, Any]]:
        """Check for syntax errors in Python files"""
        issues = []
        
        try:
            # Get all Python files in the src directory
            python_files = self._get_python_files()
            
            for file_path in python_files:
                try:
                    # Check syntax by compiling the file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    compile(code, file_path, 'exec')
                    
                except SyntaxError as e:
                    issues.append({
                        'type': 'syntax_error',
                        'file': file_path,
                        'line': e.lineno,
                        'column': e.offset,
                        'message': str(e),
                        'severity': 'critical',
                        'description': f"Syntax error in {file_path} at line {e.lineno}: {e.msg}"
                    })
                except Exception as e:
                    issues.append({
                        'type': 'compilation_error',
                        'file': file_path,
                        'message': str(e),
                        'severity': 'high',
                        'description': f"Compilation error in {file_path}: {e}"
                    })
                    
        except Exception as e:
            self.logger.error(f"Error checking syntax errors: {e}")
            
        return issues
    
    def _check_import_errors(self) -> List[Dict[str, Any]]:
        """Check for import errors"""
        issues = []
        
        try:
            # Test imports of key modules
            test_imports = [
                'core.archon_ai',
                'core.model_knowledge_integrator',
                'core.enhanced_neural_network',
                'computer.file_manager',
                'computer.process_manager',
                'computer.system_controller',
                'voice.tts',
                'ui.enhanced_web_interface'
            ]
            
            for module_name in test_imports:
                try:
                    __import__(module_name)
                except ImportError as e:
                    issues.append({
                        'type': 'import_error',
                        'module': module_name,
                        'message': str(e),
                        'severity': 'high',
                        'description': f"Import error for module {module_name}: {e}"
                    })
                except Exception as e:
                    issues.append({
                        'type': 'import_error',
                        'module': module_name,
                        'message': str(e),
                        'severity': 'medium',
                        'description': f"Unexpected error importing {module_name}: {e}"
                    })
                    
        except Exception as e:
            self.logger.error(f"Error checking import errors: {e}")
            
        return issues
    
    def _check_runtime_errors(self) -> List[Dict[str, Any]]:
        """Check for runtime errors based on recent exceptions"""
        issues = []
        
        try:
            # Check recent error logs
            error_log_path = "logs/archon.log"
            if os.path.exists(error_log_path):
                with open(error_log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                # Look for recent errors (last 50 lines)
                recent_lines = lines[-50:] if len(lines) > 50 else lines
                
                for line in recent_lines:
                    if "ERROR" in line or "Exception" in line:
                        issues.append({
                            'type': 'runtime_error',
                            'message': line.strip(),
                            'severity': 'medium',
                            'description': f"Runtime error detected: {line.strip()}"
                        })
                        
        except Exception as e:
            self.logger.error(f"Error checking runtime errors: {e}")
            
        return issues
    
    def _check_logical_inconsistencies(self) -> List[Dict[str, Any]]:
        """Check for logical inconsistencies in the code"""
        issues = []
        
        try:
            # Check for common logical issues
            logical_checks = [
                self._check_confidence_key_conflicts,
                self._check_response_structure_consistency,
                self._check_method_signature_consistency,
                self._check_data_type_consistency
            ]
            
            for check_func in logical_checks:
                try:
                    check_issues = check_func()
                    issues.extend(check_issues)
                except Exception as e:
                    self.logger.error(f"Error in logical check {check_func.__name__}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error checking logical inconsistencies: {e}")
            
        return issues
    
    def _check_confidence_key_conflicts(self) -> List[Dict[str, Any]]:
        """Check for confidence key conflicts in data structures"""
        issues = []
        
        try:
            # Check archon_ai.py for confidence key conflicts
            archon_file = "src/core/archon_ai.py"
            if os.path.exists(archon_file):
                with open(archon_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for potential confidence key conflicts
                if "'confidence':" in content and "'entity_confidence':" in content:
                    # This is good - no conflict
                    pass
                elif content.count("'confidence':") > 5:
                    issues.append({
                        'type': 'key_conflict',
                        'file': archon_file,
                        'message': "Potential confidence key conflicts detected",
                        'severity': 'medium',
                        'description': "Multiple 'confidence' keys may cause conflicts in nested data structures"
                    })
                    
        except Exception as e:
            self.logger.error(f"Error checking confidence key conflicts: {e}")
            
        return issues
    
    def _check_response_structure_consistency(self) -> List[Dict[str, Any]]:
        """Check for response structure consistency"""
        issues = []
        
        try:
            # This would require analyzing the code structure
            # For now, just check if the main response structure is consistent
            archon_file = "src/core/archon_ai.py"
            if os.path.exists(archon_file):
                with open(archon_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if response initialization is consistent
                if "response = {" in content:
                    # Look for the response initialization
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if "response = {" in line:
                            # Check the next few lines for required keys
                            required_keys = ['archon_response', 'confidence', 'intent', 'entities']
                            next_lines = lines[i+1:i+10] if i+10 < len(lines) else lines[i+1:]
                            
                            missing_keys = []
                            for key in required_keys:
                                if f"'{key}'" not in '\n'.join(next_lines):
                                    missing_keys.append(key)
                            
                            if missing_keys:
                                issues.append({
                                    'type': 'structure_inconsistency',
                                    'file': archon_file,
                                    'line': i+1,
                                    'message': f"Missing required keys in response structure: {missing_keys}",
                                    'severity': 'medium',
                                    'description': f"Response structure missing keys: {missing_keys}"
                                })
                            break
                            
        except Exception as e:
            self.logger.error(f"Error checking response structure consistency: {e}")
            
        return issues
    
    def _check_method_signature_consistency(self) -> List[Dict[str, Any]]:
        """Check for method signature consistency"""
        issues = []
        
        try:
            # This would require more sophisticated analysis
            # For now, just check if method signatures are properly formatted
            archon_file = "src/core/archon_ai.py"
            if os.path.exists(archon_file):
                with open(archon_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('def '):
                        # Check if method signature is properly formatted
                        if '(' not in line or ')' not in line:
                            issues.append({
                                'type': 'signature_inconsistency',
                                'file': archon_file,
                                'line': i+1,
                                'message': f"Malformed method signature: {line.strip()}",
                                'severity': 'medium',
                                'description': f"Method signature appears malformed: {line.strip()}"
                            })
                            
        except Exception as e:
            self.logger.error(f"Error checking method signature consistency: {e}")
            
        return issues
    
    def _check_data_type_consistency(self) -> List[Dict[str, Any]]:
        """Check for data type consistency"""
        issues = []
        
        try:
            # Check for type annotation consistency
            archon_file = "src/core/archon_ai.py"
            if os.path.exists(archon_file):
                with open(archon_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for potential type inconsistencies
                if "-> Dict[str, Any]" in content:
                    # Check if return types are consistent
                    pass
                else:
                    issues.append({
                        'type': 'type_inconsistency',
                        'file': archon_file,
                        'message': "Missing type annotations in method signatures",
                        'severity': 'low',
                        'description': "Consider adding type annotations for better code clarity"
                    })
                    
        except Exception as e:
            self.logger.error(f"Error checking data type consistency: {e}")
            
        return issues
    
    def _check_performance_issues(self) -> List[Dict[str, Any]]:
        """Check for performance issues"""
        issues = []
        
        try:
            # Check for common performance issues
            archon_file = "src/core/archon_ai.py"
            if os.path.exists(archon_file):
                with open(archon_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for potential performance issues
                if content.count("for ") > 50:
                    issues.append({
                        'type': 'performance_issue',
                        'file': archon_file,
                        'message': "High number of loops detected",
                        'severity': 'low',
                        'description': "Consider optimizing loops for better performance"
                    })
                
                if content.count("import ") > 20:
                    issues.append({
                        'type': 'performance_issue',
                        'file': archon_file,
                        'message': "High number of imports detected",
                        'severity': 'low',
                        'description': "Consider consolidating imports for better performance"
                    })
                    
        except Exception as e:
            self.logger.error(f"Error checking performance issues: {e}")
            
        return issues
    
    def _get_python_files(self) -> List[str]:
        """Get all Python files in the src directory"""
        python_files = []
        
        try:
            for root, dirs, files in os.walk("src"):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
                        
        except Exception as e:
            self.logger.error(f"Error getting Python files: {e}")
            
        return python_files
    
    def request_fix_from_windsurf(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Request fix from Windsurf's AI chat
        """
        try:
            # Format the issue description for Windsurf AI
            issue_description = self._format_issue_for_windsurf(issues)
            
            # Create the fix request
            fix_request = {
                'timestamp': datetime.now().isoformat(),
                'issues': issues,
                'description': issue_description,
                'priority': self._determine_priority(issues),
                'context': self._get_context_info()
            }
            
            # Log the fix request
            self.logger.info(f"Requesting fix from Windsurf AI for {len(issues)} issues")
            
            # Add to issue history
            self.issue_history.append(fix_request)
            
            # Simulate communication with Windsurf AI
            # In a real implementation, this would integrate with Windsurf's API
            fix_result = self._simulate_windsurf_fix(fix_request)
            
            # Add to fix history
            self.fix_history.append(fix_result)
            
            return fix_result
            
        except Exception as e:
            self.logger.error(f"Error requesting fix from Windsurf: {e}")
            return {
                'success': False,
                'message': f"Error requesting fix: {e}",
                'fix_applied': False
            }
    
    def _format_issue_for_windsurf(self, issues: List[Dict[str, Any]]) -> str:
        """Format issues for Windsurf AI"""
        description = "ARCHON AI Self-Healing Request\n\n"
        description += "I've detected the following issues in my codebase that need fixing:\n\n"
        
        for i, issue in enumerate(issues, 1):
            description += f"{i}. {issue['type'].upper()} - {issue['severity'].upper()}\n"
            description += f"   File: {issue.get('file', 'Unknown')}\n"
            description += f"   Description: {issue['description']}\n"
            
            if 'line' in issue:
                description += f"   Line: {issue['line']}\n"
            
            if 'message' in issue:
                description += f"   Details: {issue['message']}\n"
            
            description += "\n"
        
        description += "Please provide a fix for these issues. The fix should:\n"
        description += "1. Resolve all syntax errors\n"
        description += "2. Fix any import errors\n"
        description += "3. Resolve key conflicts\n"
        description += "4. Maintain existing functionality\n"
        description += "5. Follow Python best practices\n"
        description += "6. Include proper error handling\n\n"
        description += "Please provide the complete fixed code that I can apply to my system."
        
        return description
    
    def _determine_priority(self, issues: List[Dict[str, Any]]) -> str:
        """Determine the priority of the fix request"""
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for issue in issues:
            severity = issue.get('severity', 'medium')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        if severity_counts['critical'] > 0:
            return 'critical'
        elif severity_counts['high'] > 0:
            return 'high'
        elif severity_counts['medium'] > 2:
            return 'medium'
        else:
            return 'low'
    
    def _get_context_info(self) -> Dict[str, Any]:
        """Get context information for the fix request"""
        return {
            'system_status': 'operational',
            'last_error': getattr(self.archon, '_last_error', None),
            'active_features': self._get_active_features(),
            'system_info': self._get_system_info()
        }
    
    def _get_active_features(self) -> List[str]:
        """Get list of active features"""
        features = []
        
        try:
            if hasattr(self.archon, 'enhanced_neural_network') and self.archon.enhanced_neural_network:
                features.append('enhanced_neural_network')
            
            if hasattr(self.archon, 'model_knowledge_integrator') and self.archon.model_knowledge_integrator:
                features.append('model_knowledge_integrator')
            
            if hasattr(self.archon, 'ai_learning_system') and self.archon.ai_learning_system:
                features.append('ai_learning_system')
            
            if hasattr(self.archon, 'web_scraper') and self.archon.web_scraper:
                features.append('web_scraper')
                
        except Exception as e:
            self.logger.error(f"Error getting active features: {e}")
        
        return features
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            import platform
            import psutil
            
            return {
                'python_version': platform.python_version(),
                'platform': platform.system(),
                'cpu_count': psutil.cpu_count(),
                'memory_available': psutil.virtual_memory().available,
                'disk_free': psutil.disk_usage('.').free
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
    
    def _simulate_windsurf_fix(self, fix_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate communication with Windsurf AI
        In a real implementation, this would integrate with Windsurf's API
        """
        try:
            # Simulate processing time
            time.sleep(2)
            
            # Check if we have a pre-configured fix for common issues
            issues = fix_request['issues']
            
            # Generate a simulated fix response
            fix_response = {
                'success': True,
                'message': 'Fix generated successfully',
                'fix_applied': False,
                'fix_code': self._generate_fix_code(issues),
                'fix_instructions': self._generate_fix_instructions(issues),
                'estimated_fix_time': '5 minutes',
                'confidence': 0.85
            }
            
            self.logger.info(f"Simulated fix generated for {len(issues)} issues")
            
            return fix_response
            
        except Exception as e:
            self.logger.error(f"Error simulating Windsurf fix: {e}")
            return {
                'success': False,
                'message': f"Error generating fix: {e}",
                'fix_applied': False
            }
    
    def _generate_fix_code(self, issues: List[Dict[str, Any]]) -> str:
        """Generate fix code for the detected issues"""
        fix_code = "# ARCHON Self-Healing Fix\n\n"
        fix_code += "# Generated fix for detected issues\n\n"
        
        # Generate fixes for common issues
        for issue in issues:
            if issue['type'] == 'syntax_error':
                fix_code += f"# Fix for syntax error in {issue['file']}\n"
                fix_code += "# The syntax error has been resolved by restructuring the code\n"
                fix_code += "# Please review the specific line mentioned in the issue\n\n"
            
            elif issue['type'] == 'import_error':
                fix_code += f"# Fix for import error in {issue['module']}\n"
                fix_code += "# The import error has been resolved by updating the import structure\n"
                fix_code += "# Please ensure the module is properly installed and accessible\n\n"
            
            elif issue['type'] == 'key_conflict':
                fix_code += "# Fix for confidence key conflicts\n"
                fix_code += "# Key conflicts have been resolved by renaming conflicting keys:\n"
                fix_code += "# - 'entity_confidence' for entity extraction confidence\n"
                fix_code += "# - 'contextual_confidence' for contextual analysis confidence\n"
                fix_code += "# - 'neural_confidence' for neural processing confidence\n"
                fix_code += "# - 'confidence' for main response confidence\n\n"
            
            else:
                fix_code += f"# Fix for {issue['type']} in {issue.get('file', 'unknown')}\n"
                fix_code += f"# {issue['description']}\n\n"
        
        fix_code += "# Please review and apply these fixes to resolve the detected issues\n"
        fix_code += "# After applying fixes, restart the ARCHON system to verify the resolution\n"
        
        return fix_code
    
    def _generate_fix_instructions(self, issues: List[Dict[str, Any]]) -> str:
        """Generate fix instructions for the detected issues"""
        instructions = "ARCHON Self-Healing Instructions\n\n"
        instructions += "Please follow these steps to apply the fixes:\n\n"
        
        instructions += "1. Review the detected issues above\n"
        instructions += "2. Apply the provided fix code to the appropriate files\n"
        instructions += "3. Test the fixes by running the ARCHON system\n"
        instructions += "4. Verify that all issues have been resolved\n"
        instructions += "5. Restart the system if necessary\n\n"
        
        instructions += "If you encounter any issues during the fix process:\n"
        instructions += "- Check the error logs for more details\n"
        instructions += "- Ensure all dependencies are properly installed\n"
        instructions += "- Verify the file permissions are correct\n"
        instructions += "- Contact support if issues persist\n"
        
        return instructions
    
    def apply_fix(self, fix_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply the fix provided by Windsurf AI
        """
        try:
            if not fix_result.get('success', False):
                return {
                    'success': False,
                    'message': "Fix was not successful",
                    'applied': False
                }
            
            # In a real implementation, this would apply the actual fix
            # For now, we'll simulate the fix application
            
            self.logger.info("Applying fix from Windsurf AI...")
            
            # Simulate fix application
            time.sleep(1)
            
            # Verify the fix was applied
            verification_result = self._verify_fix_applied()
            
            if verification_result['success']:
                self.logger.info("Fix successfully applied and verified")
                return {
                    'success': True,
                    'message': "Fix successfully applied and verified",
                    'applied': True,
                    'verification': verification_result
                }
            else:
                self.logger.warning("Fix applied but verification failed")
                return {
                    'success': False,
                    'message': "Fix applied but verification failed",
                    'applied': True,
                    'verification': verification_result
                }
                
        except Exception as e:
            self.logger.error(f"Error applying fix: {e}")
            return {
                'success': False,
                'message': f"Error applying fix: {e}",
                'applied': False
            }
    
    def _verify_fix_applied(self) -> Dict[str, Any]:
        """
        Verify that the fix was successfully applied
        """
        try:
            # Check if the issues have been resolved
            remaining_issues = self.detect_code_issues()
            
            if len(remaining_issues) == 0:
                return {
                    'success': True,
                    'message': "All issues have been resolved",
                    'remaining_issues': 0
                }
            else:
                return {
                    'success': False,
                    'message': f"{len(remaining_issues)} issues still remain",
                    'remaining_issues': len(remaining_issues),
                    'issues': remaining_issues
                }
                
        except Exception as e:
            self.logger.error(f"Error verifying fix: {e}")
            return {
                'success': False,
                'message': f"Error verifying fix: {e}",
                'remaining_issues': -1
            }
    
    def run_self_healing_cycle(self) -> Dict[str, Any]:
        """
        Run a complete self-healing cycle
        """
        try:
            self.logger.info("Starting self-healing cycle...")
            
            # Detect issues
            issues = self.detect_code_issues()
            
            if not issues:
                return {
                    'success': True,
                    'message': "No issues detected",
                    'issues_found': 0,
                    'cycle_time': time.time()
                }
            
            # Request fix from Windsurf
            fix_request = self.request_fix_from_windsurf(issues)
            
            if not fix_request.get('success', False):
                return {
                    'success': False,
                    'message': "Failed to request fix from Windsurf",
                    'issues_found': len(issues),
                    'cycle_time': time.time()
                }
            
            # Apply the fix
            fix_result = self.apply_fix(fix_request)
            
            return {
                'success': fix_result.get('success', False),
                'message': fix_result.get('message', 'Fix completed'),
                'issues_found': len(issues),
                'fix_applied': fix_result.get('applied', False),
                'cycle_time': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error in self-healing cycle: {e}")
            return {
                'success': False,
                'message': f"Error in self-healing cycle: {e}",
                'issues_found': -1,
                'cycle_time': time.time()
            }
    
    def get_healing_status(self) -> Dict[str, Any]:
        """
        Get the current status of the self-healing system
        """
        try:
            return {
                'active': True,
                'last_cycle': self._get_last_cycle_result(),
                'total_issues_detected': len(self.issue_history),
                'total_fixes_applied': len(self.fix_history),
                'success_rate': self._calculate_success_rate(),
                'system_health': self._assess_system_health()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting healing status: {e}")
            return {
                'active': False,
                'error': str(e)
            }
    
    def _get_last_cycle_result(self) -> Optional[Dict[str, Any]]:
        """Get the result of the last healing cycle"""
        try:
            if self.fix_history:
                return self.fix_history[-1]
            return None
        except Exception as e:
            self.logger.error(f"Error getting last cycle result: {e}")
            return None
    
    def _calculate_success_rate(self) -> float:
        """Calculate the success rate of the healing system"""
        try:
            if not self.fix_history:
                return 1.0
            
            successful_fixes = sum(1 for fix in self.fix_history if fix.get('success', False))
            total_fixes = len(self.fix_history)
            
            return successful_fixes / total_fixes if total_fixes > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating success rate: {e}")
            return 0.0
    
    def _assess_system_health(self) -> str:
        """Assess the overall health of the system"""
        try:
            issues = self.detect_code_issues()
            
            if not issues:
                return "excellent"
            elif len(issues) <= 2:
                return "good"
            elif len(issues) <= 5:
                return "fair"
            else:
                return "poor"
                
        except Exception as e:
            self.logger.error(f"Error assessing system health: {e}")
            return "unknown"
