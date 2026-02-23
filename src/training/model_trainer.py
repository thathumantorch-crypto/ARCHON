import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import time
import matplotlib.pyplot as plt
from tqdm import tqdm
import wandb
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from ..core.neural_network import ConversationalNeuralNetwork, ComputerInteractionModule, VoiceProcessingModule
from .data_pipeline import ConversationalDataset

@dataclass
class TrainingConfig:
    """Configuration for model training"""
    learning_rate: float = 1e-4
    batch_size: int = 16
    num_epochs: int = 50
    warmup_steps: int = 1000
    max_grad_norm: float = 1.0
    weight_decay: float = 0.01
    adam_epsilon: float = 1e-8
    save_steps: int = 500
    eval_steps: int = 100
    logging_steps: int = 10
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    mixed_precision: bool = True
    gradient_accumulation_steps: int = 1
    early_stopping_patience: int = 5
    use_wandb: bool = False

class ModelTrainer:
    """
    Advanced model trainer with support for multiple loss functions,
    optimization strategies, and monitoring
    """
    
    def __init__(self, config: TrainingConfig = None):
        self.config = config or TrainingConfig()
        self.device = torch.device(self.config.device)
        
        # Initialize models
        self.conversational_net = None
        self.computer_module = None
        self.voice_module = None
        
        # Optimizers and schedulers
        self.optimizer = None
        self.scheduler = None
        
        # Training state
        self.global_step = 0
        self.current_epoch = 0
        self.best_loss = float('inf')
        self.early_stopping_counter = 0
        
        # Metrics tracking
        self.training_history = {
            'train_loss': [],
            'train_accuracy': [],
            'val_loss': [],
            'val_accuracy': [],
            'learning_rates': []
        }
        
        # Initialize wandb if enabled
        if self.config.use_wandb:
            wandb.init(project="conversational-ai", config=self.config.__dict__)
    
    def setup_models(self, vocab_size: int = 50000, hidden_size: int = 768,
                    num_layers: int = 12, num_heads: int = 12,
                    max_seq_len: int = 512):
        """Setup the neural network models"""
        
        self.conversational_net = ConversationalNeuralNetwork(
            vocab_size=vocab_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            num_heads=num_heads,
            max_seq_len=max_seq_len
        ).to(self.device)
        
        self.computer_module = ComputerInteractionModule(
            hidden_size=hidden_size
        ).to(self.device)
        
        self.voice_module = VoiceProcessingModule(
            hidden_size=hidden_size
        ).to(self.device)
        
        # Setup optimizer
        self.setup_optimizer()
        
        # Setup scheduler
        self.setup_scheduler()
        
        print(f"Models setup on {self.device}")
        print(f"Total parameters: {self.count_parameters():,}")
    
    def setup_optimizer(self):
        """Setup optimizer for training"""
        all_params = []
        
        if self.conversational_net:
            all_params.extend(self.conversational_net.parameters())
        if self.computer_module:
            all_params.extend(self.computer_module.parameters())
        if self.voice_module:
            all_params.extend(self.voice_module.parameters())
        
        self.optimizer = optim.AdamW(
            all_params,
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            eps=self.config.adam_epsilon
        )
    
    def setup_scheduler(self):
        """Setup learning rate scheduler"""
        total_steps = self.config.num_epochs * 1000  # Estimate
        
        self.scheduler = optim.lr_scheduler.OneCycleLR(
            self.optimizer,
            max_lr=self.config.learning_rate,
            total_steps=total_steps,
            pct_start=0.1,
            anneal_strategy='cos'
        )
    
    def count_parameters(self) -> int:
        """Count total trainable parameters"""
        total = 0
        
        for model in [self.conversational_net, self.computer_module, self.voice_module]:
            if model:
                total += sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        return total
    
    def compute_loss(self, batch: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """Compute multi-task loss"""
        
        # Forward pass through conversational network
        outputs = self.conversational_net(
            batch['input_ids'],
            batch['attention_mask']
        )
        
        # Language modeling loss
        lm_logits = outputs['logits'].view(-1, outputs['logits'].size(-1))
        labels = batch['labels'].view(-1)
        lm_loss = nn.CrossEntropyLoss(ignore_index=0)(lm_logits, labels)
        
        # Computer interaction loss
        computer_outputs = self.computer_module(outputs['hidden_states'])
        computer_loss = 0
        
        if 'file_operations' in computer_outputs:
            # Simple binary classification for file operations
            file_targets = torch.zeros(computer_outputs['file_operations'].size(0), 
                                     computer_outputs['file_operations'].size(1))
            computer_loss += nn.MSELoss()(computer_outputs['file_operations'], file_targets)
        
        # Voice processing loss
        voice_outputs = self.voice_module(outputs['hidden_states'])
        voice_loss = 0
        
        if 'voice_commands' in voice_outputs:
            # Simple classification for voice commands
            voice_targets = torch.zeros(voice_outputs['voice_commands'].size(0),
                                      voice_outputs['voice_commands'].size(1), dtype=torch.long)
            voice_loss += nn.CrossEntropyLoss()(voice_outputs['voice_commands'], voice_targets)
        
        # Intent classification loss
        intent_loss = nn.CrossEntropyLoss()(outputs['action_logits'].view(-1, 100), 
                                          batch['intent'].unsqueeze(1).expand(-1, 100).argmax(dim=1))
        
        # Combined loss with weights
        total_loss = (
            1.0 * lm_loss +
            0.3 * computer_loss +
            0.2 * voice_loss +
            0.1 * intent_loss
        )
        
        return {
            'total_loss': total_loss,
            'lm_loss': lm_loss,
            'computer_loss': computer_loss,
            'voice_loss': voice_loss,
            'intent_loss': intent_loss
        }
    
    def train_epoch(self, train_loader: DataLoader) -> Dict[str, float]:
        """Train for one epoch"""
        self.conversational_net.train()
        self.computer_module.train()
        self.voice_module.train()
        
        total_loss = 0
        total_lm_loss = 0
        total_computer_loss = 0
        total_voice_loss = 0
        total_intent_loss = 0
        
        num_batches = len(train_loader)
        
        progress_bar = tqdm(train_loader, desc=f"Epoch {self.current_epoch}")
        
        for batch_idx, batch in enumerate(progress_bar):
            # Move batch to device
            batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                    for k, v in batch.items()}
            
            # Compute loss
            losses = self.compute_loss(batch)
            
            # Backward pass
            losses['total_loss'].backward()
            
            # Gradient clipping
            if self.config.max_grad_norm > 0:
                torch.nn.utils.clip_grad_norm_(
                    list(self.conversational_net.parameters()) +
                    list(self.computer_module.parameters()) +
                    list(self.voice_module.parameters()),
                    self.config.max_grad_norm
                )
            
            # Optimizer step
            self.optimizer.step()
            self.scheduler.step()
            self.optimizer.zero_grad()
            
            # Update metrics
            total_loss += losses['total_loss'].item()
            total_lm_loss += losses['lm_loss'].item()
            total_computer_loss += losses['computer_loss'].item()
            total_voice_loss += losses['voice_loss'].item()
            total_intent_loss += losses['intent_loss'].item()
            
            self.global_step += 1
            
            # Update progress bar
            progress_bar.set_postfix({
                'loss': f"{losses['total_loss'].item():.4f}",
                'lr': f"{self.scheduler.get_last_lr()[0]:.6f}"
            })
            
            # Logging
            if self.global_step % self.config.logging_steps == 0:
                self.log_metrics({
                    'train/total_loss': losses['total_loss'].item(),
                    'train/lm_loss': losses['lm_loss'].item(),
                    'train/computer_loss': losses['computer_loss'].item(),
                    'train/voice_loss': losses['voice_loss'].item(),
                    'train/intent_loss': losses['intent_loss'].item(),
                    'train/learning_rate': self.scheduler.get_last_lr()[0],
                    'train/global_step': self.global_step
                })
        
        # Calculate averages
        avg_loss = total_loss / num_batches
        avg_lm_loss = total_lm_loss / num_batches
        avg_computer_loss = total_computer_loss / num_batches
        avg_voice_loss = total_voice_loss / num_batches
        avg_intent_loss = total_intent_loss / num_batches
        
        return {
            'total_loss': avg_loss,
            'lm_loss': avg_lm_loss,
            'computer_loss': avg_computer_loss,
            'voice_loss': avg_voice_loss,
            'intent_loss': avg_intent_loss
        }
    
    def evaluate(self, val_loader: DataLoader) -> Dict[str, float]:
        """Evaluate the model"""
        self.conversational_net.eval()
        self.computer_module.eval()
        self.voice_module.eval()
        
        total_loss = 0
        total_lm_loss = 0
        total_computer_loss = 0
        total_voice_loss = 0
        total_intent_loss = 0
        
        all_predictions = []
        all_labels = []
        
        num_batches = len(val_loader)
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Evaluating"):
                # Move batch to device
                batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                        for k, v in batch.items()}
                
                # Compute loss
                losses = self.compute_loss(batch)
                
                # Update metrics
                total_loss += losses['total_loss'].item()
                total_lm_loss += losses['lm_loss'].item()
                total_computer_loss += losses['computer_loss'].item()
                total_voice_loss += losses['voice_loss'].item()
                total_intent_loss += losses['intent_loss'].item()
                
                # Collect predictions for accuracy calculation
                predictions = torch.argmax(losses['logits'], dim=-1)
                labels = batch['labels']
                
                # Flatten and filter out padding tokens
                mask = labels != 0
                pred_flat = predictions[mask].cpu().numpy()
                labels_flat = labels[mask].cpu().numpy()
                
                all_predictions.extend(pred_flat)
                all_labels.extend(labels_flat)
        
        # Calculate averages
        avg_loss = total_loss / num_batches
        avg_lm_loss = total_lm_loss / num_batches
        avg_computer_loss = total_computer_loss / num_batches
        avg_voice_loss = total_voice_loss / num_batches
        avg_intent_loss = total_intent_loss / num_batches
        
        # Calculate accuracy
        accuracy = accuracy_score(all_labels, all_predictions) if all_labels else 0
        
        return {
            'total_loss': avg_loss,
            'lm_loss': avg_lm_loss,
            'computer_loss': avg_computer_loss,
            'voice_loss': avg_voice_loss,
            'intent_loss': avg_intent_loss,
            'accuracy': accuracy
        }
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader,
              save_dir: str = "models") -> Dict[str, Any]:
        """Main training loop"""
        
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)
        
        print(f"Starting training for {self.config.num_epochs} epochs")
        print(f"Device: {self.device}")
        print(f"Batch size: {self.config.batch_size}")
        print(f"Learning rate: {self.config.learning_rate}")
        
        training_start_time = time.time()
        
        for epoch in range(self.config.num_epochs):
            self.current_epoch = epoch
            
            # Train epoch
            train_metrics = self.train_epoch(train_loader)
            
            # Evaluate
            val_metrics = self.evaluate(val_loader)
            
            # Update history
            self.training_history['train_loss'].append(train_metrics['total_loss'])
            self.training_history['train_accuracy'].append(val_metrics['accuracy'])
            self.training_history['val_loss'].append(val_metrics['total_loss'])
            self.training_history['val_accuracy'].append(val_metrics['accuracy'])
            self.training_history['learning_rates'].append(self.scheduler.get_last_lr()[0])
            
            # Print epoch results
            print(f"\nEpoch {epoch + 1}/{self.config.num_epochs}")
            print(f"Train Loss: {train_metrics['total_loss']:.4f}")
            print(f"Val Loss: {val_metrics['total_loss']:.4f}")
            print(f"Val Accuracy: {val_metrics['accuracy']:.4f}")
            print(f"Learning Rate: {self.scheduler.get_last_lr()[0]:.6f}")
            
            # Log metrics
            self.log_metrics({
                'epoch': epoch + 1,
                'train/total_loss': train_metrics['total_loss'],
                'train/lm_loss': train_metrics['lm_loss'],
                'val/total_loss': val_metrics['total_loss'],
                'val/accuracy': val_metrics['accuracy'],
                'learning_rate': self.scheduler.get_last_lr()[0]
            })
            
            # Save checkpoint
            if (epoch + 1) % self.config.save_steps == 0:
                self.save_checkpoint(save_path / f"checkpoint_epoch_{epoch + 1}")
            
            # Save best model
            if val_metrics['total_loss'] < self.best_loss:
                self.best_loss = val_metrics['total_loss']
                self.save_checkpoint(save_path / "best_model")
                self.early_stopping_counter = 0
            else:
                self.early_stopping_counter += 1
            
            # Early stopping
            if self.early_stopping_counter >= self.config.early_stopping_patience:
                print(f"Early stopping triggered after {epoch + 1} epochs")
                break
        
        training_time = time.time() - training_start_time
        
        # Save final model
        self.save_checkpoint(save_path / "final_model")
        
        # Save training history
        self.save_training_history(save_path / "training_history.json")
        
        # Plot training curves
        self.plot_training_curves(save_path / "training_curves.png")
        
        print(f"\nTraining completed in {training_time:.2f} seconds")
        print(f"Best validation loss: {self.best_loss:.4f}")
        
        return {
            'training_time': training_time,
            'best_loss': self.best_loss,
            'total_epochs': epoch + 1,
            'final_metrics': val_metrics
        }
    
    def save_checkpoint(self, path: Path):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': self.current_epoch,
            'global_step': self.global_step,
            'best_loss': self.best_loss,
            'conversational_net_state_dict': self.conversational_net.state_dict(),
            'computer_module_state_dict': self.computer_module.state_dict(),
            'voice_module_state_dict': self.voice_module.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'config': self.config.__dict__,
            'training_history': self.training_history
        }
        
        torch.save(checkpoint, path)
        print(f"Checkpoint saved to {path}")
    
    def load_checkpoint(self, path: Path):
        """Load model checkpoint"""
        checkpoint = torch.load(path, map_location=self.device)
        
        self.conversational_net.load_state_dict(checkpoint['conversational_net_state_dict'])
        self.computer_module.load_state_dict(checkpoint['computer_module_state_dict'])
        self.voice_module.load_state_dict(checkpoint['voice_module_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        self.current_epoch = checkpoint['epoch']
        self.global_step = checkpoint['global_step']
        self.best_loss = checkpoint['best_loss']
        self.training_history = checkpoint['training_history']
        
        print(f"Checkpoint loaded from {path}")
    
    def save_training_history(self, path: Path):
        """Save training history to JSON"""
        with open(path, 'w') as f:
            json.dump(self.training_history, f, indent=2)
    
    def plot_training_curves(self, path: Path):
        """Plot training curves"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Loss curves
        axes[0, 0].plot(self.training_history['train_loss'], label='Train Loss')
        axes[0, 0].plot(self.training_history['val_loss'], label='Val Loss')
        axes[0, 0].set_title('Training and Validation Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Accuracy curves
        axes[0, 1].plot(self.training_history['train_accuracy'], label='Train Accuracy')
        axes[0, 1].plot(self.training_history['val_accuracy'], label='Val Accuracy')
        axes[0, 1].set_title('Training and Validation Accuracy')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Accuracy')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Learning rate curve
        axes[1, 0].plot(self.training_history['learning_rates'])
        axes[1, 0].set_title('Learning Rate Schedule')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Learning Rate')
        axes[1, 0].grid(True)
        
        # Loss difference
        loss_diff = np.array(self.training_history['val_loss']) - np.array(self.training_history['train_loss'])
        axes[1, 1].plot(loss_diff)
        axes[1, 1].set_title('Validation - Training Loss Difference')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Loss Difference')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Training curves saved to {path}")
    
    def log_metrics(self, metrics: Dict[str, float]):
        """Log training metrics"""
        if self.config.use_wandb:
            wandb.log(metrics)
    
    def generate_text(self, prompt: str, max_length: int = 100, 
                     temperature: float = 1.0, do_sample: bool = True) -> str:
        """Generate text using the trained model"""
        if not self.conversational_net:
            return "Model not loaded"
        
        self.conversational_net.eval()
        
        with torch.no_grad():
            # Tokenize prompt
            # This is simplified - in practice, you'd use the actual tokenizer
            input_ids = torch.tensor([[1, 2, 3]], device=self.device)  # Placeholder
            
            # Generate response
            generated_ids = self.conversational_net.generate_response(
                input_ids, max_length=max_length, temperature=temperature, do_sample=do_sample
            )
            
            # Convert back to text (placeholder)
            generated_text = "Generated response placeholder"
            
            return generated_text
    
    def cleanup(self):
        """Clean up resources"""
        if self.config.use_wandb:
            wandb.finish()
        
        # Clear CUDA cache if using GPU
        if self.device.type == 'cuda':
            torch.cuda.empty_cache()
        
        print("Model trainer cleaned up")
