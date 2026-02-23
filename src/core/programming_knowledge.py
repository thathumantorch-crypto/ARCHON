"""
ARCHON Programming Knowledge Base

This module contains comprehensive programming knowledge that ARCHON can use
to assist with professional software development, code analysis, and self-improvement.
"""

from typing import Dict, List, Any, Tuple
import ast
import re
from dataclasses import dataclass
from enum import Enum

class ProgrammingLanguage(Enum):
    """Programming languages ARCHON knows"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    HTML = "html"
    CSS = "css"
    SQL = "sql"
    BASH = "bash"
    POWERSHELL = "powershell"

class CodeQuality(Enum):
    """Code quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class CodePattern:
    """Represents a reusable code pattern"""
    name: str
    language: ProgrammingLanguage
    pattern: str
    description: str
    use_cases: List[str]
    complexity: str
    best_practices: List[str]

@dataclass
class CodeSmell:
    """Represents a code smell (bad practice)"""
    name: str
    description: str
    severity: str
    fix_suggestion: str
    example_bad: str
    example_good: str

class ArchonProgrammingKnowledge:
    """ARCHON's comprehensive programming knowledge base"""
    
    def __init__(self):
        self.code_patterns = self._initialize_code_patterns()
        self.code_smells = self._initialize_code_smells()
        self.best_practices = self._initialize_best_practices()
        self.design_patterns = self._initialize_design_patterns()
        self.optimization_techniques = self._initialize_optimization_techniques()
        self.testing_strategies = self._initialize_testing_strategies()
        self.security_practices = self._initialize_security_practices()
    
    def _initialize_code_patterns(self) -> Dict[ProgrammingLanguage, List[CodePattern]]:
        """Initialize common code patterns"""
        patterns = {
            ProgrammingLanguage.PYTHON: [
                CodePattern(
                    name="Context Manager",
                    language=ProgrammingLanguage.PYTHON,
                    pattern="""
class ResourceManager:
    def __enter__(self):
        # Acquire resource
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Release resource
        pass

with ResourceManager() as resource:
    # Use resource
    pass
                    """.strip(),
                    description="Manages resource acquisition and release automatically",
                    use_cases=["File handling", "Database connections", "Network connections"],
                    complexity="medium",
                    best_practices=["Always implement both __enter__ and __exit__", "Handle exceptions properly"]
                ),
                CodePattern(
                    name="Factory Pattern",
                    language=ProgrammingLanguage.PYTHON,
                    pattern="""
class AnimalFactory:
    @staticmethod
    def create_animal(animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
        else:
            raise ValueError("Unknown animal type")
                    """.strip(),
                    description="Creates objects without specifying exact class",
                    use_cases=["Object creation", "Plugin systems", "Configuration-based instantiation"],
                    complexity="medium",
                    best_practices=["Use type hints", "Validate input parameters", "Document factory methods"]
                ),
                CodePattern(
                    name="Decorator Pattern",
                    language=ProgrammingLanguage.PYTHON,
                    pattern="""
def timing_decorator(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper

@timing_decorator
def slow_function():
    # Function implementation
    pass
                    """.strip(),
                    description="Adds functionality to functions without modifying them",
                    use_cases=["Logging", "Timing", "Authentication", "Caching"],
                    complexity="medium",
                    best_practices=["Use functools.wraps", "Handle exceptions", "Preserve function metadata"]
                )
            ],
            ProgrammingLanguage.JAVASCRIPT: [
                CodePattern(
                    name="Module Pattern",
                    language=ProgrammingLanguage.JAVASCRIPT,
                    pattern="""
const MyModule = (function() {
    let privateVariable = 0;
    
    function privateFunction() {
        return privateVariable;
    }
    
    return {
        publicMethod: function() {
            return privateFunction();
        },
        publicProperty: 42
    };
})();
                    """.strip(),
                    description="Encapsulates private and public members",
                    use_cases=["Namespace creation", "Private variables", "API design"],
                    complexity="medium",
                    best_practices=["Return clear public API", "Document public methods", "Use strict mode"]
                )
            ]
        }
        return patterns
    
    def _initialize_code_smells(self) -> List[CodeSmell]:
        """Initialize common code smells"""
        return [
            CodeSmell(
                name="Long Method",
                description="Methods that are too long and do too many things",
                severity="medium",
                fix_suggestion="Break down into smaller, focused methods",
                example_bad="def process_data(data): # 50 lines of processing",
                example_good="def process_data(data):\n    cleaned = clean_data(data)\n    validated = validate_data(cleaned)\n    return transform_data(validated)"
            ),
            CodeSmell(
                name="Magic Numbers",
                description="Unnamed numeric constants",
                severity="low",
                fix_suggestion="Replace with named constants",
                example_bad="if x > 3.14159:",
                example_good="PI = 3.14159\nif x > PI:"
            ),
            CodeSmell(
                name="Deep Nesting",
                description="Too many levels of nested conditions",
                severity="medium",
                fix_suggestion="Use early returns or extract methods",
                example_bad="if a:\n    if b:\n        if c:\n            if d:",
                example_good="if not a or not b or not c or not d:\n    return\n# Main logic"
            )
        ]
    
    def _initialize_best_practices(self) -> Dict[str, List[str]]:
        """Initialize programming best practices"""
        return {
            "python": [
                "Use type hints for better code documentation",
                "Follow PEP 8 style guidelines",
                "Write docstrings for all public functions and classes",
                "Use virtual environments for dependency management",
                "Implement proper error handling with try/except blocks",
                "Use list comprehensions for simple transformations",
                "Prefer composition over inheritance",
                "Use context managers for resource management",
                "Write unit tests for all critical functionality",
                "Use logging instead of print statements"
            ],
            "general": [
                "Write readable, self-documenting code",
                "Keep functions small and focused",
                "Use meaningful variable and function names",
                "Don't repeat yourself (DRY principle)",
                "Comment why, not what",
                "Handle edge cases and errors gracefully",
                "Write tests before writing code (TDD)",
                "Review and refactor code regularly",
                "Use version control properly",
                "Document APIs and interfaces"
            ]
        }
    
    def _initialize_design_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize design patterns knowledge"""
        return {
            "creational": {
                "Factory": {
                    "purpose": "Create objects without specifying exact class",
                    "when_to_use": ["Cannot anticipate class types", "Want to hide creation logic"],
                    "python_example": """
class DatabaseFactory:
    @staticmethod
    def create(db_type):
        if db_type == "mysql":
            return MySQLConnection()
        elif db_type == "postgresql":
            return PostgreSQLConnection()
                        """
                },
                "Singleton": {
                    "purpose": "Ensure only one instance exists",
                    "when_to_use": ["Exactly one instance needed", "Global access point"],
                    "python_example": """
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
                        """
                }
            },
            "structural": {
                "Adapter": {
                    "purpose": "Allow incompatible interfaces to work together",
                    "when_to_use": ["Need to integrate legacy code", "Third-party libraries"],
                    "python_example": """
class LegacyAdapter:
    def __init__(self, legacy_system):
        self.legacy = legacy_system
    
    def modern_method(self):
        return self.legacy.legacy_method()
                        """
                }
            },
            "behavioral": {
                "Observer": {
                    "purpose": "Notify multiple objects about state changes",
                    "when_to_use": ["Event handling", "UI updates", "Distributed systems"],
                    "python_example": """
class Observer:
    def update(self, subject):
        pass

class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def notify(self):
        for observer in self._observers:
            observer.update(self)
                        """
                }
            }
        }
    
    def _initialize_optimization_techniques(self) -> Dict[str, List[str]]:
        """Initialize performance optimization techniques"""
        return {
            "python": [
                "Use built-in functions and libraries (they're implemented in C)",
                "Use generators for large datasets to save memory",
                "Cache expensive function results with functools.lru_cache",
                "Use list comprehensions instead of loops for simple operations",
                "Avoid string concatenation in loops (use join)",
                "Use appropriate data structures (sets for membership testing)",
                "Profile code before optimizing",
                "Use numpy for numerical computations",
                "Consider multiprocessing for CPU-bound tasks",
                "Use async/await for I/O-bound operations"
            ],
            "general": [
                "Measure before optimizing",
                "Focus on bottlenecks (80/20 rule)",
                "Consider algorithmic complexity",
                "Use caching strategically",
                "Minimize I/O operations",
                "Batch operations when possible",
                "Use connection pooling",
                "Optimize database queries",
                "Consider memory vs CPU tradeoffs",
                "Use appropriate data structures"
            ]
        }
    
    def _initialize_testing_strategies(self) -> Dict[str, List[str]]:
        """Initialize testing strategies"""
        return {
            "unit_testing": [
                "Test individual functions and methods in isolation",
                "Use descriptive test names",
                "Test edge cases and error conditions",
                "Use assertions effectively",
                "Keep tests independent",
                "Use test fixtures for setup",
                "Mock external dependencies",
                "Aim for high code coverage",
                "Write tests before fixing bugs",
                "Use parameterized tests for multiple scenarios"
            ],
            "integration_testing": [
                "Test component interactions",
                "Test database operations",
                "Test API endpoints",
                "Test file system operations",
                "Test network communications",
                "Use test databases",
                "Test error handling across components",
                "Validate data flow",
                "Test configuration variations",
                "Monitor performance under load"
            ],
            "testing_tools": {
                "python": ["pytest", "unittest", "mock", "coverage", "tox"],
                "javascript": ["jest", "mocha", "chai", "sinon", "cypress"],
                "general": ["CI/CD pipelines", "automated testing", "test documentation"]
            }
        }
    
    def _initialize_security_practices(self) -> Dict[str, List[str]]:
        """Initialize security best practices"""
        return {
            "input_validation": [
                "Never trust user input",
                "Validate and sanitize all inputs",
                "Use allowlists instead of blocklists",
                "Validate data types and formats",
                "Check input length and range",
                "Escape special characters",
                "Use parameterized queries for databases",
                "Validate file uploads",
                "Implement rate limiting",
                "Use CAPTCHA for public forms"
            ],
            "authentication": [
                "Use strong password policies",
                "Implement multi-factor authentication",
                "Use secure password hashing (bcrypt, Argon2)",
                "Implement session management",
                "Use HTTPS everywhere",
                "Implement account lockout policies",
                "Use secure token generation",
                "Implement proper logout",
                "Monitor for suspicious activity",
                "Keep authentication libraries updated"
            ],
            "data_protection": [
                "Encrypt sensitive data at rest",
                "Encrypt data in transit",
                "Use secure key management",
                "Implement data retention policies",
                "Anonymize personal data",
                "Use secure backup procedures",
                "Implement access controls",
                "Audit data access",
                "Comply with privacy regulations",
                "Secure disposal of sensitive data"
            ]
        }
    
    def analyze_code(self, code: str, language: ProgrammingLanguage = ProgrammingLanguage.PYTHON) -> Dict[str, Any]:
        """
        Analyze code and provide comprehensive insights
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Dictionary with analysis results
        """
        try:
            analysis = {
                "language": language.value,
                "code_length": len(code),
                "line_count": len(code.split('\n')),
                "quality_analysis": self.analyze_code_quality(code, language),
                "security_analysis": self.analyze_security(code, language),
                "suggestions": self.get_improvement_suggestions(code, language),
                "complexity_analysis": self.analyze_complexity(code, language)
            }
            
            return analysis
            
        except Exception as e:
            return {
                "error": str(e),
                "language": language.value,
                "code_length": len(code),
                "line_count": len(code.split('\n'))
            }
    
    def analyze_code_quality(self, code: str, language: ProgrammingLanguage) -> Dict[str, Any]:
        """Analyze code quality and provide suggestions"""
        analysis = {
            "quality_score": 0,
            "issues": [],
            "suggestions": [],
            "patterns_found": [],
            "smells_detected": []
        }
        
        try:
            tree = ast.parse(code)
            
            # Analyze code structure
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            # Check for code smells
            for func in functions:
                if len(func.body) > 20:  # Long method
                    analysis["smells_detected"].append({
                        "type": "Long Method",
                        "function": func.name,
                        "lines": len(func.body),
                        "suggestion": "Consider breaking this function into smaller methods"
                    })
                
                # Check for magic numbers
                for node in ast.walk(func):
                    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                        if node.value not in [0, 1, -1]:  # Common exceptions
                            analysis["smells_detected"].append({
                                "type": "Magic Number",
                                "value": node.value,
                                "line": node.lineno,
                                "suggestion": "Consider using a named constant"
                            })
            
            # Calculate quality score
            base_score = 100
            issues_penalty = len(analysis["smells_detected"]) * 10
            analysis["quality_score"] = max(0, base_score - issues_penalty)
            
            # Add suggestions based on analysis
            if len(functions) == 0 and len(classes) == 0:
                analysis["suggestions"].append("Consider organizing code into functions and classes")
            
            if analysis["quality_score"] < 70:
                analysis["suggestions"].append("Code quality needs improvement - address detected issues")
            
        except SyntaxError as e:
            analysis["issues"].append(f"Syntax error: {e}")
            analysis["quality_score"] = 0
        
        return analysis
    
    def suggest_improvements(self, code: str, language: ProgrammingLanguage) -> List[str]:
        """Suggest specific improvements for code"""
        suggestions = []
        
        # Analyze code for improvement opportunities
        if language == ProgrammingLanguage.PYTHON:
            # Check for Python-specific improvements
            if "for i in range(len(" in code:
                suggestions.append("Consider using enumerate() instead of range(len())")
            
            if "if " in code and "else:" in code:
                suggestions.append("Consider using ternary operator for simple conditional assignments")
            
            if "def " in code and "return " not in code:
                suggestions.append("Functions should have explicit return statements")
        
        # General suggestions
        if len(code.split('\n')) > 50:
            suggestions.append("Consider breaking large files into smaller modules")
        
        if code.count('#') < len(code.split('\n')) * 0.1:
            suggestions.append("Consider adding more comments for complex logic")
        
        return suggestions
    
    def get_pattern_suggestion(self, task: str, language: ProgrammingLanguage) -> Optional[CodePattern]:
        """Suggest appropriate code pattern for a task"""
        task_lower = task.lower()
        
        if language == ProgrammingLanguage.PYTHON:
            patterns = self.code_patterns[language]
            
            if "resource" in task_lower or "file" in task_lower:
                return next((p for p in patterns if p.name == "Context Manager"), None)
            elif "create" in task_lower and "object" in task_lower:
                return next((p for p in patterns if p.name == "Factory Pattern"), None)
            elif "timing" in task_lower or "log" in task_lower:
                return next((p for p in patterns if p.name == "Decorator Pattern"), None)
        
        return None
    
    def learn_new_pattern(self, pattern: CodePattern) -> bool:
        """Learn a new code pattern"""
        try:
            if pattern.language not in self.code_patterns:
                self.code_patterns[pattern.language] = []
            
            # Check if pattern already exists
            existing_names = [p.name for p in self.code_patterns[pattern.language]]
            if pattern.name not in existing_names:
                self.code_patterns[pattern.language].append(pattern)
                return True
            
            return False
        except Exception:
            return False
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get summary of ARCHON's programming knowledge"""
        return {
            "languages_known": [lang.value for lang in ProgrammingLanguage],
            "code_patterns_count": sum(len(patterns) for patterns in self.code_patterns.values()),
            "code_smells_count": len(self.code_smells),
            "design_patterns_count": len(self.design_patterns["creational"]) + 
                                  len(self.design_patterns["structural"]) + 
                                  len(self.design_patterns["behavioral"]),
            "best_practices_categories": list(self.best_practices.keys()),
            "optimization_techniques": list(self.optimization_techniques.keys()),
            "testing_strategies": list(self.testing_strategies.keys()),
            "security_practices": list(self.security_practices.keys())
        }
