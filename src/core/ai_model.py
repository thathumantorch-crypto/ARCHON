import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict

from .neural_network import ConversationalNeuralNetwork, ComputerInteractionModule, VoiceProcessingModule
from .conversation import ConversationManager, ConversationContext, ConversationIntent
from ..voice.tts import TextToSpeechEngine
try:
    from ..voice.stt import SpeechToTextEngine
except ImportError:
    print("⚠️ Using alternative STT engine (no pyaudio)")
    from ..voice.stt_no_pyaudio import SpeechToTextEngineNoPyAudio as SpeechToTextEngine
from ..computer.file_manager import FileManager
from ..computer.process_manager import ProcessManager
from ..computer.system_controller import SystemController

@dataclass
class ModelConfig:
    """Configuration for the AI model"""
    vocab_size: int = 50000
    hidden_size: int = 768
    num_layers: int = 12
    num_heads: int = 12
    max_seq_len: int = 512
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    model_path: str = "models/conversational_ai.pt"
    voice_enabled: bool = False
    computer_interaction_enabled: bool = True

class AIModel:
    """
    Main AI Model class that integrates all components for conversational AI
    with computer interaction and voice capabilities
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()
        self.device = torch.device(self.config.device)
        
        # Initialize core components
        self._initialize_neural_networks()
        self._initialize_conversation_manager()
        self._initialize_computer_interfaces()
        self._initialize_voice_interfaces()
        
        # Model state
        self.is_initialized = False
        self.current_context = None
        self.session_id = self._generate_session_id()
        
        # Load pre-trained model if available
        self._load_model_if_exists()
    
    def _initialize_neural_networks(self):
        """Initialize neural network components"""
        self.conversational_net = ConversationalNeuralNetwork(
            vocab_size=self.config.vocab_size,
            hidden_size=self.config.hidden_size,
            num_layers=self.config.num_layers,
            num_heads=self.config.num_heads,
            max_seq_len=self.config.max_seq_len
        ).to(self.device)
        
        self.computer_module = ComputerInteractionModule(
            hidden_size=self.config.hidden_size
        ).to(self.device)
        
        self.voice_module = VoiceProcessingModule(
            hidden_size=self.config.hidden_size
        ).to(self.device)
        
        # Optimizer
        self.optimizer = torch.optim.AdamW(
            list(self.conversational_net.parameters()) +
            list(self.computer_module.parameters()) +
            list(self.voice_module.parameters()),
            lr=1e-4,
            weight_decay=0.01
        )
    
    def _initialize_conversation_manager(self):
        """Initialize conversation management system"""
        self.conversation_manager = ConversationManager(
            max_context_length=10
        )
    
    def _initialize_computer_interfaces(self):
        """Initialize computer interaction interfaces"""
        if self.config.computer_interaction_enabled:
            self.file_manager = FileManager()
            self.process_manager = ProcessManager()
            self.system_controller = SystemController()
        else:
            self.file_manager = None
            self.process_manager = None
            self.system_controller = None
    
    def _initialize_voice_interfaces(self):
        """Initialize voice interfaces"""
        if self.config.voice_enabled:
            self.tts_engine = TextToSpeechEngine()
            self.stt_engine = SpeechToTextEngine()
        else:
            self.tts_engine = None
            self.stt_engine = None
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
    
    def _load_model_if_exists(self):
        """Load pre-trained model if available"""
        if os.path.exists(self.config.model_path):
            try:
                checkpoint = torch.load(self.config.model_path, map_location=self.device)
                self.conversational_net.load_state_dict(checkpoint['conversational_net'])
                self.computer_module.load_state_dict(checkpoint['computer_module'])
                self.voice_module.load_state_dict(checkpoint['voice_module'])
                self.optimizer.load_state_dict(checkpoint['optimizer'])
                self.is_initialized = True
                print(f"Model loaded from {self.config.model_path}")
            except Exception as e:
                print(f"Error loading model: {e}")
                self.is_initialized = False
        else:
            print("No pre-trained model found. Using untrained model.")
            self.is_initialized = False
    
    def save_model(self, path: Optional[str] = None):
        """Save the current model state"""
        save_path = path or self.config.model_path
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        checkpoint = {
            'conversational_net': self.conversational_net.state_dict(),
            'computer_module': self.computer_module.state_dict(),
            'voice_module': self.voice_module.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'config': asdict(self.config),
            'timestamp': datetime.now().isoformat()
        }
        
        torch.save(checkpoint, save_path)
        print(f"Model saved to {save_path}")
    
    def initialize_context(self, user_id: str = "default") -> ConversationContext:
        """Initialize conversation context"""
        self.current_context = ConversationContext(
            user_id=user_id,
            session_id=self.session_id,
            timestamp=datetime.now(),
            previous_turns=[],
            computer_state=self._get_computer_state(),
            voice_active=self.config.voice_enabled,
            current_directory=os.getcwd()
        )
        return self.current_context
    
    def _get_computer_state(self) -> Dict[str, Any]:
        """Get current computer state"""
        state = {}
        
        if self.file_manager:
            try:
                state['current_directory'] = os.getcwd()
                state['directory_contents'] = len(os.listdir('.'))
            except:
                state['current_directory'] = "unknown"
                state['directory_contents'] = 0
        
        if self.process_manager:
            try:
                state['running_processes'] = len(self.process_manager.get_running_processes())
            except:
                state['running_processes'] = 0
        
        if self.system_controller:
            try:
                state['system_info'] = self.system_controller.get_system_info()
            except:
                state['system_info'] = {}
        
        return state
    
    def chat(self, user_input: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Main chat interface for user interaction
        
        Args:
            user_input: User's text input
            user_id: User identifier
            
        Returns:
            Dictionary containing response and metadata
        """
        # Initialize context if needed
        if self.current_context is None or self.current_context.user_id != user_id:
            self.initialize_context(user_id)
        
        # Classify intent and extract entities
        intent = self.conversation_manager.classify_intent(user_input)
        entities = self.conversation_manager.extract_entities(user_input, intent)
        
        # Generate contextual response
        response_text = self.conversation_manager.generate_contextual_response(
            user_input, intent, entities, self.current_context
        )
        
        # Execute computer operations if needed
        operation_result = None
        if intent in [ConversationIntent.FILE_OPERATION, ConversationIntent.PROCESS_MANAGEMENT, 
                     ConversationIntent.SYSTEM_CONTROL]:
            operation_result = self._execute_computer_operation(intent, entities)
        
        # Update conversation context
        self._update_conversation_context(user_input, response_text, intent, entities)
        
        # Prepare response
        response = {
            'text': response_text,
            'intent': intent.value,
            'entities': entities,
            'operation_result': operation_result,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id
        }
        
        # Voice output if enabled
        if self.config.voice_enabled and self.tts_engine:
            self._speak_response(response_text)
        
        return response
    
    def _execute_computer_operation(self, intent: ConversationIntent, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute computer operations based on intent and entities"""
        result = {'success': False, 'message': '', 'data': {}}
        
        try:
            if intent == ConversationIntent.FILE_OPERATION and self.file_manager:
                operation = entities.get('operation', '')
                if operation == 'list':
                    files = self.file_manager.list_directory()
                    result['success'] = True
                    result['data']['files'] = files
                    result['message'] = f"Found {len(files)} items in current directory"
                elif operation == 'create':
                    file_names = entities.get('file_names', [])
                    if file_names:
                        created = []
                        for file_name in file_names:
                            try:
                                self.file_manager.create_file(file_name)
                                created.append(file_name)
                            except:
                                pass
                        result['success'] = True
                        result['data']['created_files'] = created
                        result['message'] = f"Created {len(created)} files"
            
            elif intent == ConversationIntent.PROCESS_MANAGEMENT and self.process_manager:
                operation = entities.get('operation', '')
                if operation == 'list':
                    processes = self.process_manager.get_running_processes()
                    result['success'] = True
                    result['data']['processes'] = processes[:10]  # Limit to first 10
                    result['message'] = f"Found {len(processes)} running processes"
            
            elif intent == ConversationIntent.SYSTEM_CONTROL and self.system_controller:
                operation = entities.get('operation', '')
                if operation == 'check':
                    system_info = self.system_controller.get_system_info()
                    result['success'] = True
                    result['data']['system_info'] = system_info
                    result['message'] = "System information retrieved"
        
        except Exception as e:
            result['message'] = f"Error executing operation: {str(e)}"
        
        return result
    
    def _update_conversation_context(self, user_input: str, response: str, 
                                   intent: ConversationIntent, entities: Dict[str, Any]):
        """Update conversation context with new turn"""
        if self.current_context:
            turn = {
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'assistant_response': response,
                'intent': intent.value,
                'entities': entities
            }
            
            self.current_context.previous_turns.append(turn)
            
            # Limit context length
            if len(self.current_context.previous_turns) > 10:
                self.current_context.previous_turns = self.current_context.previous_turns[-10:]
            
            # Update computer state
            self.current_context.computer_state = self._get_computer_state()
    
    def _speak_response(self, text: str):
        """Convert response text to speech"""
        if self.tts_engine:
            try:
                self.tts_engine.speak(text)
            except Exception as e:
                print(f"Error speaking response: {e}")
    
    def enable_voice(self):
        """Enable voice interaction"""
        if not self.config.voice_enabled:
            self.config.voice_enabled = True
            self._initialize_voice_interfaces()
            if self.current_context:
                self.current_context.voice_active = True
            return "Voice interaction enabled"
        return "Voice interaction already enabled"
    
    def disable_voice(self):
        """Disable voice interaction"""
        if self.config.voice_enabled:
            self.config.voice_enabled = False
            self.tts_engine = None
            self.stt_engine = None
            if self.current_context:
                self.current_context.voice_active = False
            return "Voice interaction disabled"
        return "Voice interaction already disabled"
    
    def listen_to_voice(self, duration: int = 5) -> Optional[str]:
        """Listen to voice input and convert to text"""
        if self.stt_engine:
            try:
                return self.stt_engine.listen(duration)
            except Exception as e:
                print(f"Error listening to voice: {e}")
                return None
        return None
    
    def train_step(self, batch_data: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """Perform one training step"""
        self.conversational_net.train()
        self.computer_module.train()
        self.voice_module.train()
        
        # Forward pass
        outputs = self.conversational_net(
            batch_data['input_ids'],
            batch_data.get('attention_mask'),
            batch_data.get('computer_context')
        )
        
        # Calculate losses
        lm_loss = F.cross_entropy(
            outputs['logits'].view(-1, self.config.vocab_size),
            batch_data['labels'].view(-1)
        )
        
        action_loss = F.cross_entropy(
            outputs['action_logits'].view(-1, 100),
            batch_data['action_labels'].view(-1)
        )
        
        voice_loss = F.cross_entropy(
            outputs['voice_logits'].view(-1, 50),
            batch_data['voice_labels'].view(-1)
        )
        
        # Combined loss
        total_loss = lm_loss + 0.3 * action_loss + 0.2 * voice_loss
        
        # Backward pass
        self.optimizer.zero_grad()
        total_loss.backward()
        self.optimizer.step()
        
        return {
            'total_loss': total_loss.item(),
            'lm_loss': lm_loss.item(),
            'action_loss': action_loss.item(),
            'voice_loss': voice_loss.item()
        }
    
    def evaluate(self, test_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Evaluate model on test data"""
        self.conversational_net.eval()
        self.computer_module.eval()
        self.voice_module.eval()
        
        total_loss = 0
        correct_predictions = 0
        total_predictions = 0
        
        with torch.no_grad():
            for batch in test_data:
                # Convert batch to tensors
                input_ids = torch.tensor(batch['input_ids'], device=self.device)
                labels = torch.tensor(batch['labels'], device=self.device)
                
                outputs = self.conversational_net(input_ids)
                
                # Calculate loss
                loss = F.cross_entropy(
                    outputs['logits'].view(-1, self.config.vocab_size),
                    labels.view(-1)
                )
                total_loss += loss.item()
                
                # Calculate accuracy (simplified)
                predictions = torch.argmax(outputs['logits'], dim=-1)
                correct_predictions += (predictions == labels).sum().item()
                total_predictions += labels.numel()
        
        avg_loss = total_loss / len(test_data)
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and statistics"""
        return {
            'model_config': asdict(self.config),
            'is_initialized': self.is_initialized,
            'session_id': self.session_id,
            'device': str(self.device),
            'parameters': {
                'conversational_net': sum(p.numel() for p in self.conversational_net.parameters()),
                'computer_module': sum(p.numel() for p in self.computer_module.parameters()),
                'voice_module': sum(p.numel() for p in self.voice_module.parameters()),
                'total': sum(p.numel() for p in self.conversational_net.parameters()) +
                        sum(p.numel() for p in self.computer_module.parameters()) +
                        sum(p.numel() for p in self.voice_module.parameters())
            }
        }
