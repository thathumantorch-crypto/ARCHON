import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
import json
import os
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import random
import re
from pathlib import Path
import pickle
from transformers import AutoTokenizer
from sklearn.model_selection import train_test_split

class DataType(Enum):
    """Data types for training"""
    CONVERSATION = "conversation"
    COMPUTER_OPERATIONS = "computer_operations"
    VOICE_COMMANDS = "voice_commands"
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    CODE_SNIPPETS = "code_snippets"
    SYSTEM_LOGS = "system_logs"

@dataclass
class TrainingExample:
    """Single training example"""
    input_text: str
    target_text: str
    intent: str
    entities: Dict[str, Any]
    context: Dict[str, Any]
    data_type: DataType
    difficulty: float = 0.5  # 0.0 to 1.0

class ConversationalDataset(Dataset):
    """
    Dataset class for conversational AI training
    """
    
    def __init__(self, examples: List[TrainingExample], tokenizer, max_length: int = 512):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Preprocess examples
        self.processed_examples = self._preprocess_examples()
    
    def _preprocess_examples(self) -> List[Dict[str, Any]]:
        """Preprocess training examples"""
        processed = []
        
        for example in self.examples:
            try:
                # Tokenize input and target
                input_encoding = self.tokenizer(
                    example.input_text,
                    max_length=self.max_length,
                    padding='max_length',
                    truncation=True,
                    return_tensors='pt'
                )
                
                target_encoding = self.tokenizer(
                    example.target_text,
                    max_length=self.max_length,
                    padding='max_length',
                    truncation=True,
                    return_tensors='pt'
                )
                
                processed_example = {
                    'input_ids': input_encoding['input_ids'].squeeze(),
                    'attention_mask': input_encoding['attention_mask'].squeeze(),
                    'labels': target_encoding['input_ids'].squeeze(),
                    'intent': self._encode_intent(example.intent),
                    'entities': self._encode_entities(example.entities),
                    'context': self._encode_context(example.context),
                    'data_type': example.data_type.value,
                    'difficulty': example.difficulty
                }
                
                processed.append(processed_example)
            
            except Exception as e:
                print(f"Error processing example: {e}")
                continue
        
        return processed
    
    def _encode_intent(self, intent: str) -> torch.Tensor:
        """Encode intent as tensor"""
        intent_mapping = {
            'general_chat': 0,
            'file_operation': 1,
            'process_management': 2,
            'system_control': 3,
            'voice_command': 4,
            'help_request': 5,
            'unknown': 6
        }
        
        intent_id = intent_mapping.get(intent, 6)
        return torch.tensor(intent_id, dtype=torch.long)
    
    def _encode_entities(self, entities: Dict[str, Any]) -> torch.Tensor:
        """Encode entities as tensor"""
        # Simplified entity encoding
        entity_features = []
        
        # File operation features
        entity_features.append(1.0 if 'file_paths' in entities else 0.0)
        entity_features.append(1.0 if 'file_names' in entities else 0.0)
        entity_features.append(1.0 if 'operation' in entities else 0.0)
        
        # Process operation features
        entity_features.append(1.0 if 'process_names' in entities else 0.0)
        
        # System operation features
        entity_features.append(1.0 if 'setting' in entities else 0.0)
        
        # Voice command features
        entity_features.append(1.0 if 'voice_command' in entities else 0.0)
        entity_features.append(1.0 if 'voice_setting' in entities else 0.0)
        
        # Common features
        entity_features.append(1.0 if 'numbers' in entities else 0.0)
        entity_features.append(1.0 if 'time_expressions' in entities else 0.0)
        
        # Pad to fixed size
        while len(entity_features) < 10:
            entity_features.append(0.0)
        
        return torch.tensor(entity_features[:10], dtype=torch.float)
    
    def _encode_context(self, context: Dict[str, Any]) -> torch.Tensor:
        """Encode context as tensor"""
        context_features = []
        
        # Computer state features
        computer_state = context.get('computer_state', {})
        context_features.append(float(computer_state.get('running_processes', 0)))
        context_features.append(float(computer_state.get('directory_contents', 0)))
        
        # Session features
        context_features.append(1.0 if context.get('voice_active', False) else 0.0)
        context_features.append(len(context.get('previous_turns', [])))
        
        # Time features
        timestamp = context.get('timestamp', '')
        if timestamp:
            # Extract hour of day
            try:
                hour = int(timestamp.split('T')[1].split(':')[0])
                context_features.append(float(hour / 24.0))  # Normalize to 0-1
            except:
                context_features.append(0.0)
        else:
            context_features.append(0.0)
        
        # Pad to fixed size
        while len(context_features) < 10:
            context_features.append(0.0)
        
        return torch.tensor(context_features[:10], dtype=torch.float)
    
    def __len__(self) -> int:
        return len(self.processed_examples)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        return self.processed_examples[idx]

class DataPipeline:
    """
    Advanced data pipeline for training conversational AI
    """
    
    def __init__(self, data_dir: str = "data", tokenizer_name: str = "bert-base-uncased"):
        self.data_dir = Path(data_dir)
        self.tokenizer_name = tokenizer_name
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        
        # Create data directories
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / "raw").mkdir(exist_ok=True)
        (self.data_dir / "processed").mkdir(exist_ok=True)
        (self.data_dir / "models").mkdir(exist_ok=True)
        
        # Data sources
        self.data_sources = {
            DataType.CONVERSATION: self._load_conversation_data,
            DataType.COMPUTER_OPERATIONS: self._load_computer_operations_data,
            DataType.VOICE_COMMANDS: self._load_voice_commands_data,
            DataType.TECHNICAL_DOCUMENTATION: self._load_technical_documentation,
            DataType.CODE_SNIPPETS: self._load_code_snippets,
            DataType.SYSTEM_LOGS: self._load_system_logs
        }
    
    def generate_synthetic_data(self, num_examples: int = 1000) -> List[TrainingExample]:
        """Generate synthetic training data"""
        examples = []
        
        # Conversation templates
        conversation_templates = [
            ("Hello, how are you?", "Hello! I'm doing well, thank you for asking. How can I help you today?"),
            ("What can you do?", "I can help you with file operations, process management, system control, and voice commands."),
            ("Help me with files", "I'd be happy to help you with file operations. What would you like to do?"),
            ("List my files", "I'll list the files in your current directory."),
            ("Open a program", "I can help you start a program. Which one would you like to open?"),
            ("Check system status", "I'll check your system status and performance for you."),
            ("Enable voice", "Voice control is now enabled. You can use voice commands to interact with me."),
            ("What's running?", "I'll list all running processes for you."),
            ("Shutdown computer", "I can help you shutdown the system. Are you sure you want to proceed?")
        ]
        
        # Computer operation templates
        computer_templates = [
            ("Create file {filename}", "I'll create the file {filename} for you."),
            ("Delete {filename}", "I'll delete the file {filename} for you."),
            ("Copy {source} to {destination}", "I'll copy {source} to {destination}."),
            ("Start {process}", "I'll start the {process} process for you."),
            ("Stop {process}", "I'll stop the {process} process for you."),
            ("List files", "I'll list all files in the current directory."),
            ("Check memory", "I'll check the system memory usage for you."),
            ("Restart system", "I'll restart the system for you.")
        ]
        
        # Voice command templates
        voice_templates = [
            ("Speak louder", "I'll increase my speaking volume."),
            ("Speak softer", "I'll decrease my speaking volume."),
            ("Stop speaking", "I'll stop speaking now."),
            ("Repeat that", "I'll repeat what I just said."),
            ("Change voice", "I'll change my voice settings for you.")
        ]
        
        # Generate examples
        for i in range(num_examples):
            # Choose template type
            template_type = random.choice(['conversation', 'computer', 'voice'])
            
            if template_type == 'conversation':
                input_text, target_text = random.choice(conversation_templates)
                intent = 'general_chat'
                entities = {}
                data_type = DataType.CONVERSATION
                
            elif template_type == 'computer':
                template = random.choice(computer_templates)
                # Fill in placeholders
                input_text = template.format(
                    filename=random.choice(['document.txt', 'data.csv', 'config.json']),
                    source=random.choice(['file1.txt', 'data.csv']),
                    destination=random.choice(['backup/', 'new_location/']),
                    process=random.choice(['notepad.exe', 'chrome.exe', 'python.exe'])
                )
                target_text = "I'll help you with that operation."
                intent = 'file_operation' if 'file' in input_text else 'process_management'
                entities = self._extract_entities_from_text(input_text)
                data_type = DataType.COMPUTER_OPERATIONS
                
            else:  # voice
                input_text, target_text = random.choice(voice_templates)
                intent = 'voice_command'
                entities = self._extract_entities_from_text(input_text)
                data_type = DataType.VOICE_COMMANDS
            
            # Create context
            context = {
                'computer_state': {
                    'running_processes': random.randint(10, 100),
                    'directory_contents': random.randint(5, 50)
                },
                'voice_active': random.choice([True, False]),
                'previous_turns': [],
                'timestamp': '2024-01-01T12:00:00'
            }
            
            # Create training example
            example = TrainingExample(
                input_text=input_text,
                target_text=target_text,
                intent=intent,
                entities=entities,
                context=context,
                data_type=data_type,
                difficulty=random.uniform(0.3, 0.8)
            )
            
            examples.append(example)
        
        return examples
    
    def _extract_entities_from_text(self, text: str) -> Dict[str, Any]:
        """Extract entities from text"""
        entities = {}
        
        # File paths
        file_pattern = r'["\']?([a-zA-Z]:\\[^"\']+)["\']?'
        paths = re.findall(file_pattern, text)
        if paths:
            entities['file_paths'] = paths
        
        # File names
        file_name_pattern = r'["\']?([^"\'\\]+\.[a-zA-Z0-9]+)["\']?'
        files = re.findall(file_name_pattern, text)
        if files:
            entities['file_names'] = files
        
        # Process names
        process_pattern = r'["\']?([a-zA-Z0-9_\-\.]+\.exe)["\']?'
        processes = re.findall(process_pattern, text, re.IGNORECASE)
        if processes:
            entities['process_names'] = processes
        
        # Numbers
        numbers = re.findall(r'\b\d+\b', text)
        if numbers:
            entities['numbers'] = [int(n) for n in numbers]
        
        return entities
    
    def _load_conversation_data(self) -> List[TrainingExample]:
        """Load conversation data from files"""
        examples = []
        
        # Try to load from existing files
        conv_file = self.data_dir / "raw" / "conversations.json"
        
        if conv_file.exists():
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item in data:
                    example = TrainingExample(
                        input_text=item.get('input', ''),
                        target_text=item.get('target', ''),
                        intent=item.get('intent', 'general_chat'),
                        entities=item.get('entities', {}),
                        context=item.get('context', {}),
                        data_type=DataType.CONVERSATION,
                        difficulty=item.get('difficulty', 0.5)
                    )
                    examples.append(example)
            
            except Exception as e:
                print(f"Error loading conversation data: {e}")
        
        return examples
    
    def _load_computer_operations_data(self) -> List[TrainingExample]:
        """Load computer operations data"""
        examples = []
        
        # Generate synthetic computer operation data
        operations = [
            ('create file', 'file_operation'),
            ('delete file', 'file_operation'),
            ('copy file', 'file_operation'),
            ('move file', 'file_operation'),
            ('list files', 'file_operation'),
            ('start process', 'process_management'),
            ('stop process', 'process_management'),
            ('restart process', 'process_management'),
            ('check system', 'system_control'),
            ('shutdown system', 'system_control')
        ]
        
        for operation, intent in operations:
            for i in range(50):  # Generate 50 examples per operation
                input_text = f"Please {operation} for me"
                target_text = f"I'll help you {operation}."
                
                example = TrainingExample(
                    input_text=input_text,
                    target_text=target_text,
                    intent=intent,
                    entities={'operation': operation},
                    context={'computer_state': {}},
                    data_type=DataType.COMPUTER_OPERATIONS,
                    difficulty=0.4
                )
                examples.append(example)
        
        return examples
    
    def _load_voice_commands_data(self) -> List[TrainingExample]:
        """Load voice commands data"""
        examples = []
        
        voice_commands = [
            ('speak louder', 'increase_volume'),
            ('speak softer', 'decrease_volume'),
            ('stop speaking', 'stop_speech'),
            ('repeat that', 'repeat'),
            ('enable voice', 'enable_voice'),
            ('disable voice', 'disable_voice')
        ]
        
        for command, action in voice_commands:
            for i in range(30):  # Generate 30 examples per command
                input_text = f"Can you {command}?"
                target_text = f"I'll {action} for you."
                
                example = TrainingExample(
                    input_text=input_text,
                    target_text=target_text,
                    intent='voice_command',
                    entities={'voice_command': action},
                    context={'voice_active': True},
                    data_type=DataType.VOICE_COMMANDS,
                    difficulty=0.3
                )
                examples.append(example)
        
        return examples
    
    def _load_technical_documentation(self) -> List[TrainingExample]:
        """Load technical documentation data"""
        examples = []
        
        # Generate synthetic technical Q&A
        tech_topics = [
            ('What is CPU?', 'CPU stands for Central Processing Unit. It\'s the primary component of a computer that performs most of the processing.'),
            ('What is RAM?', 'RAM stands for Random Access Memory. It\'s a type of computer memory that can be read and changed in any order.'),
            ('What is an operating system?', 'An operating system is software that manages computer hardware and software resources.'),
            ('What is a file system?', 'A file system is a method and data structure that the operating system uses to control how data is stored and retrieved.')
        ]
        
        for question, answer in tech_topics:
            for i in range(20):  # Generate 20 examples per topic
                example = TrainingExample(
                    input_text=question,
                    target_text=answer,
                    intent='help_request',
                    entities={'topic': question.split()[2].lower()},
                    context={},
                    data_type=DataType.TECHNICAL_DOCUMENTATION,
                    difficulty=0.6
                )
                examples.append(example)
        
        return examples
    
    def _load_code_snippets(self) -> List[TrainingExample]:
        """Load code snippets data"""
        examples = []
        
        code_examples = [
            ('How to create a file in Python?', 'You can create a file in Python using the open() function with "w" mode.'),
            ('How to list processes?', 'You can list processes using the psutil library in Python.'),
            ('How to use subprocess?', 'The subprocess module allows you to spawn new processes.')
        ]
        
        for question, answer in code_examples:
            for i in range(15):  # Generate 15 examples per snippet
                example = TrainingExample(
                    input_text=question,
                    target_text=answer,
                    intent='help_request',
                    entities={'language': 'python'},
                    context={},
                    data_type=DataType.CODE_SNIPPETS,
                    difficulty=0.7
                )
                examples.append(example)
        
        return examples
    
    def _load_system_logs(self) -> List[TrainingExample]:
        """Load system logs data"""
        examples = []
        
        # Generate synthetic system log analysis
        log_patterns = [
            ('Error in system log', 'I found an error in the system log. Let me help you investigate.'),
            ('High CPU usage detected', 'I detected high CPU usage. Would you like me to check which processes are causing it?'),
            ('Low memory warning', 'Your system is running low on memory. Consider closing some applications.'),
            ('Disk space full', 'Your disk is almost full. You should clean up some files.')
        ]
        
        for pattern, response in log_patterns:
            for i in range(10):  # Generate 10 examples per pattern
                example = TrainingExample(
                    input_text=f"Check {pattern.lower()}",
                    target_text=response,
                    intent='system_control',
                    entities={'log_type': pattern.split()[0].lower()},
                    context={'computer_state': {}},
                    data_type=DataType.SYSTEM_LOGS,
                    difficulty=0.8
                )
                examples.append(example)
        
        return examples
    
    def load_all_data(self, synthetic_ratio: float = 0.7) -> List[TrainingExample]:
        """Load all training data"""
        all_examples = []
        
        # Load real data
        for data_type, loader in self.data_sources.items():
            try:
                examples = loader()
                all_examples.extend(examples)
                print(f"Loaded {len(examples)} examples for {data_type.value}")
            except Exception as e:
                print(f"Error loading {data_type.value}: {e}")
        
        # Generate synthetic data
        synthetic_count = int(len(all_examples) * synthetic_ratio / (1 - synthetic_ratio))
        synthetic_examples = self.generate_synthetic_data(synthetic_count)
        all_examples.extend(synthetic_examples)
        
        print(f"Generated {len(synthetic_examples)} synthetic examples")
        print(f"Total examples: {len(all_examples)}")
        
        return all_examples
    
    def create_data_loaders(self, examples: List[TrainingExample], 
                           batch_size: int = 16, 
                           test_size: float = 0.2,
                           val_size: float = 0.1) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """Create train, validation, and test data loaders"""
        
        # Split data
        train_examples, temp_examples = train_test_split(
            examples, test_size=(test_size + val_size), random_state=42
        )
        
        val_examples, test_examples = train_test_split(
            temp_examples, test_size=(test_size / (test_size + val_size)), random_state=42
        )
        
        # Create datasets
        train_dataset = ConversationalDataset(train_examples, self.tokenizer)
        val_dataset = ConversationalDataset(val_examples, self.tokenizer)
        test_dataset = ConversationalDataset(test_examples, self.tokenizer)
        
        # Create data loaders
        train_loader = DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True, num_workers=2
        )
        
        val_loader = DataLoader(
            val_dataset, batch_size=batch_size, shuffle=False, num_workers=2
        )
        
        test_loader = DataLoader(
            test_dataset, batch_size=batch_size, shuffle=False, num_workers=2
        )
        
        print(f"Data splits - Train: {len(train_examples)}, Val: {len(val_examples)}, Test: {len(test_examples)}")
        
        return train_loader, val_loader, test_loader
    
    def save_processed_data(self, examples: List[TrainingExample], filename: str):
        """Save processed training data"""
        processed_data = []
        
        for example in examples:
            processed_example = {
                'input_text': example.input_text,
                'target_text': example.target_text,
                'intent': example.intent,
                'entities': example.entities,
                'context': example.context,
                'data_type': example.data_type.value,
                'difficulty': example.difficulty
            }
            processed_data.append(processed_example)
        
        save_path = self.data_dir / "processed" / filename
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(processed_data)} examples to {save_path}")
    
    def load_processed_data(self, filename: str) -> List[TrainingExample]:
        """Load processed training data"""
        load_path = self.data_dir / "processed" / filename
        
        if not load_path.exists():
            print(f"File not found: {load_path}")
            return []
        
        examples = []
        
        with open(load_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data:
            example = TrainingExample(
                input_text=item['input_text'],
                target_text=item['target_text'],
                intent=item['intent'],
                entities=item['entities'],
                context=item['context'],
                data_type=DataType(item['data_type']),
                difficulty=item['difficulty']
            )
            examples.append(example)
        
        print(f"Loaded {len(examples)} examples from {load_path}")
        return examples
    
    def analyze_data_distribution(self, examples: List[TrainingExample]) -> Dict[str, Any]:
        """Analyze the distribution of training data"""
        analysis = {
            'total_examples': len(examples),
            'data_types': {},
            'intents': {},
            'difficulty_distribution': {'easy': 0, 'medium': 0, 'hard': 0},
            'average_input_length': 0,
            'average_target_length': 0
        }
        
        input_lengths = []
        target_lengths = []
        
        for example in examples:
            # Count data types
            data_type = example.data_type.value
            analysis['data_types'][data_type] = analysis['data_types'].get(data_type, 0) + 1
            
            # Count intents
            intent = example.intent
            analysis['intents'][intent] = analysis['intents'].get(intent, 0) + 1
            
            # Count difficulty
            if example.difficulty < 0.33:
                analysis['difficulty_distribution']['easy'] += 1
            elif example.difficulty < 0.67:
                analysis['difficulty_distribution']['medium'] += 1
            else:
                analysis['difficulty_distribution']['hard'] += 1
            
            # Track lengths
            input_lengths.append(len(example.input_text.split()))
            target_lengths.append(len(example.target_text.split()))
        
        # Calculate averages
        if input_lengths:
            analysis['average_input_length'] = sum(input_lengths) / len(input_lengths)
        
        if target_lengths:
            analysis['average_target_length'] = sum(target_lengths) / len(target_lengths)
        
        return analysis
