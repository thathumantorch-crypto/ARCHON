import cmd
import sys
import os
import json
import time
from typing import Dict, List, Any, Optional
import argparse
from pathlib import Path
import threading
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_model import AIModel, ModelConfig
from computer.file_manager import FileManager
from computer.process_manager import ProcessManager
from computer.system_controller import SystemController
from voice.tts import TextToSpeechEngine
from voice.stt import SpeechToTextEngine

class CLIInterface(cmd.Cmd):
    """
    Command-line interface for the conversational AI system
    """
    
    intro = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                Conversational AI Assistant CLI                ║
    ║                                                              ║
    ║  Type 'help' for available commands or 'chat' to start       ║
    ║  Type 'exit' to quit the application                        ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    
    prompt = "🤖 AI> "
    
    def __init__(self):
        super().__init__()
        self.ai_model = None
        self.file_manager = FileManager()
        self.process_manager = ProcessManager()
        self.system_controller = SystemController()
        self.tts_engine = None
        self.stt_engine = None
        self.voice_enabled = False
        self.current_directory = os.getcwd()
        self.conversation_history = []
        
        # Initialize AI model
        self.initialize_ai_model()
    
    def initialize_ai_model(self):
        """Initialize the AI model"""
        try:
            print("🔄 Initializing AI Model...")
            config = ModelConfig(
                voice_enabled=self.voice_enabled,
                computer_interaction_enabled=True
            )
            self.ai_model = AIModel(config)
            
            # Initialize voice engines if enabled
            if self.voice_enabled:
                self.tts_engine = TextToSpeechEngine()
                self.stt_engine = SpeechToTextEngine()
            
            print("✅ AI Model initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Error initializing AI Model: {str(e)}")
            return False
    
    def do_chat(self, arg):
        """Start interactive chat mode"""
        print("\n🗣️  Entering chat mode. Type 'quit' to exit chat.")
        print("─" * 60)
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Exiting chat mode...")
                    break
                
                if not user_input:
                    continue
                
                # Get AI response
                print("🤖 AI: ", end="", flush=True)
                response = self.ai_model.chat(user_input)
                print(response['text'])
                
                # Show operation results if any
                if response.get('operation_result') and response['operation_result'].get('success'):
                    print(f"🔧 Operation completed: {response['operation_result'].get('message', '')}")
                
                # Add to conversation history
                self.conversation_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'user': user_input,
                    'assistant': response['text'],
                    'intent': response.get('intent'),
                    'entities': response.get('entities')
                })
                
            except KeyboardInterrupt:
                print("\n👋 Chat interrupted. Type 'quit' to exit.")
            except Exception as e:
                print(f"❌ Error in chat: {str(e)}")
    
    def do_voice(self, arg):
        """Toggle voice interaction"""
        if not arg:
            # Show current status
            status = "enabled" if self.voice_enabled else "disabled"
            print(f"🎤 Voice is currently {status}")
            return
        
        if arg.lower() in ['on', 'enable', 'start']:
            if not self.voice_enabled:
                self.voice_enabled = True
                if self.initialize_ai_model():
                    print("✅ Voice interaction enabled")
                else:
                    print("❌ Failed to enable voice interaction")
            else:
                print("✅ Voice is already enabled")
        
        elif arg.lower() in ['off', 'disable', 'stop']:
            if self.voice_enabled:
                self.voice_enabled = False
                self.tts_engine = None
                self.stt_engine = None
                print("✅ Voice interaction disabled")
            else:
                print("✅ Voice is already disabled")
        
        else:
            print("Usage: voice [on|off|enable|disable|start|stop]")
    
    def do_listen(self, arg):
        """Listen to voice input"""
        if not self.voice_enabled or not self.stt_engine:
            print("❌ Voice is not enabled. Use 'voice on' to enable.")
            return
        
        try:
            duration = int(arg) if arg.isdigit() else 5
            print(f"🎤 Listening for {duration} seconds...")
            
            text = self.stt_engine.listen(duration)
            
            if text:
                print(f"👤 Heard: {text}")
                
                # Get AI response
                print("🤖 AI: ", end="", flush=True)
                response = self.ai_model.chat(text)
                print(response['text'])
                
                # Speak response if TTS is available
                if self.tts_engine:
                    self.tts_engine.speak(response['text'])
            else:
                print("❌ No speech detected")
        
        except ValueError:
            print("❌ Invalid duration. Usage: listen [seconds]")
        except Exception as e:
            print(f"❌ Error listening: {str(e)}")
    
    def do_speak(self, arg):
        """Speak text using TTS"""
        if not self.voice_enabled or not self.tts_engine:
            print("❌ Voice is not enabled. Use 'voice on' to enable.")
            return
        
        if not arg:
            print("❌ Please provide text to speak")
            return
        
        try:
            print(f"🔊 Speaking: {arg}")
            self.tts_engine.speak(arg)
        except Exception as e:
            print(f"❌ Error speaking: {str(e)}")
    
    def do_ls(self, arg):
        """List directory contents"""
        path = arg if arg else self.current_directory
        
        try:
            files = self.file_manager.list_directory(path)
            
            if not files:
                print(f"📁 Directory is empty: {path}")
                return
            
            print(f"📁 Contents of {path}:")
            print("─" * 60)
            
            for file_info in files:
                icon = "📁" if file_info['type'] == 'directory' else "📄"
                size_str = self.format_size(file_info['size']) if file_info['type'] == 'file' else ""
                modified = file_info['modified'][:19].replace('T', ' ')
                
                print(f"{icon} {file_info['name']:<30} {size_str:>10} {modified}")
        
        except Exception as e:
            print(f"❌ Error listing directory: {str(e)}")
    
    def do_cd(self, arg):
        """Change directory"""
        if not arg:
            print(f"📁 Current directory: {self.current_directory}")
            return
        
        try:
            new_path = os.path.abspath(arg)
            if os.path.isdir(new_path):
                self.current_directory = new_path
                os.chdir(new_path)
                print(f"📁 Changed to: {self.current_directory}")
            else:
                print(f"❌ Directory not found: {arg}")
        except Exception as e:
            print(f"❌ Error changing directory: {str(e)}")
    
    def do_pwd(self, arg):
        """Print working directory"""
        print(f"📁 {self.current_directory}")
    
    def do_mkdir(self, arg):
        """Create directory"""
        if not arg:
            print("❌ Please provide directory name")
            return
        
        try:
            result = self.file_manager.create_directory(arg)
            if result['success']:
                print(f"✅ Directory created: {arg}")
            else:
                print(f"❌ {result['message']}")
        except Exception as e:
            print(f"❌ Error creating directory: {str(e)}")
    
    def do_touch(self, arg):
        """Create empty file"""
        if not arg:
            print("❌ Please provide file name")
            return
        
        try:
            result = self.file_manager.create_file(arg)
            if result['success']:
                print(f"✅ File created: {arg}")
            else:
                print(f"❌ {result['message']}")
        except Exception as e:
            print(f"❌ Error creating file: {str(e)}")
    
    def do_cat(self, arg):
        """Display file contents"""
        if not arg:
            print("❌ Please provide file name")
            return
        
        try:
            result = self.file_manager.read_file(arg)
            if result['success']:
                print(f"📄 Contents of {arg}:")
                print("─" * 60)
                print(result['content'])
                print("─" * 60)
            else:
                print(f"❌ {result['message']}")
        except Exception as e:
            print(f"❌ Error reading file: {str(e)}")
    
    def do_rm(self, arg):
        """Remove file or directory"""
        if not arg:
            print("❌ Please provide file or directory name")
            return
        
        try:
            # Check if it's a file or directory
            if os.path.isfile(arg):
                result = self.file_manager.delete_file(arg)
            elif os.path.isdir(arg):
                result = self.file_manager.delete_directory(arg, recursive=True)
            else:
                print(f"❌ File or directory not found: {arg}")
                return
            
            if result['success']:
                print(f"✅ Removed: {arg}")
            else:
                print(f"❌ {result['message']}")
        except Exception as e:
            print(f"❌ Error removing: {str(e)}")
    
    def do_ps(self, arg):
        """List running processes"""
        try:
            processes = self.process_manager.get_running_processes()
            
            if not processes:
                print("📋 No running processes found")
                return
            
            print(f"📋 Running Processes ({len(processes)} total):")
            print("─" * 80)
            print(f"{'PID':<8} {'Name':<25} {'CPU%':<8} {'MEM%':<8} {'Status':<12}")
            print("─" * 80)
            
            for proc in processes[:20]:  # Show first 20
                print(f"{proc.pid:<8} {proc.name[:24]:<25} {proc.cpu_percent:<8.1f} "
                      f"{proc.memory_percent:<8.1f} {proc.status:<12}")
            
            if len(processes) > 20:
                print(f"... and {len(processes) - 20} more processes")
        
        except Exception as e:
            print(f"❌ Error listing processes: {str(e)}")
    
    def do_kill(self, arg):
        """Kill process by PID"""
        if not arg:
            print("❌ Please provide process PID")
            return
        
        try:
            pid = int(arg)
            result = self.process_manager.stop_process(pid, force=True)
            
            if result['success']:
                print(f"✅ Process killed: PID {pid}")
            else:
                print(f"❌ {result['message']}")
        
        except ValueError:
            print("❌ Invalid PID. Please provide a number.")
        except Exception as e:
            print(f"❌ Error killing process: {str(e)}")
    
    def do_start(self, arg):
        """Start a process"""
        if not arg:
            print("❌ Please provide command to start")
            return
        
        try:
            result = self.process_manager.start_process(arg)
            
            if result['success']:
                print(f"✅ Process started: {arg} (PID: {result['pid']})")
            else:
                print(f"❌ {result['message']}")
        
        except Exception as e:
            print(f"❌ Error starting process: {str(e)}")
    
    def do_sysinfo(self, arg):
        """Display system information"""
        try:
            info = self.system_controller.get_system_info()
            
            print("💻 System Information:")
            print("─" * 60)
            print(f"System: {info['system']} {info['version']}")
            print(f"Machine: {info['machine']}")
            print(f"Processor: {info['processor']}")
            print(f"Python: {info['python_version']}")
            print(f"Boot Time: {info['boot_time'][:19].replace('T', ' ')}")
            
            print("\n🖥️  CPU Information:")
            print(f"Cores: {info['cpu']['count']} (Physical: {info['cpu']['physical_count']})")
            print(f"Usage: {info['cpu']['usage_percent']:.1f}%")
            
            if info['cpu']['frequency']:
                freq = info['cpu']['frequency']
                print(f"Frequency: {freq['current']:.2f} MHz (Max: {freq['max']:.2f} MHz)")
            
            print("\n💾 Memory Information:")
            mem = info['memory']
            print(f"Total: {mem['total_gb']:.1f} GB")
            print(f"Available: {mem['available_gb']:.1f} GB")
            print(f"Used: {mem['used_gb']:.1f} GB ({mem['percent']:.1f}%)")
            
            print("\n💿 Disk Information:")
            for device, usage in info['disk'].items():
                print(f"{device}: {usage['used_gb']:.1f}/{usage['total_gb']:.1f} GB "
                      f"({usage['percent']:.1f}%)")
        
        except Exception as e:
            print(f"❌ Error getting system info: {str(e)}")
    
    def do_health(self, arg):
        """Check system health"""
        try:
            health = self.system_controller.check_system_health()
            
            print("🏥 System Health Check:")
            print("─" * 60)
            
            # Overall status
            status_icons = {
                'healthy': '✅',
                'warning': '⚠️',
                'critical': '❌'
            }
            
            icon = status_icons.get(health['overall'], '❓')
            print(f"Overall Status: {icon} {health['overall'].upper()}")
            
            # Individual checks
            for check_name, check_result in health['checks'].items():
                if check_result['status'] == 'ok':
                    print(f"✅ {check_name.title()}: OK")
                elif check_result['status'] == 'warning':
                    print(f"⚠️ {check_name.title()}: Warning")
                else:
                    print(f"❌ {check_name.title()}: Critical")
            
            # Warnings and errors
            if health['warnings']:
                print("\n⚠️ Warnings:")
                for warning in health['warnings']:
                    print(f"  • {warning}")
            
            if health['errors']:
                print("\n❌ Errors:")
                for error in health['errors']:
                    print(f"  • {error}")
        
        except Exception as e:
            print(f"❌ Error checking system health: {str(e)}")
    
    def do_history(self, arg):
        """Show conversation history"""
        if not self.conversation_history:
            print("📝 No conversation history yet")
            return
        
        print(f"📝 Conversation History ({len(self.conversation_history)} messages):")
        print("─" * 80)
        
        for i, entry in enumerate(self.conversation_history[-10:], 1):  # Show last 10
            timestamp = entry['timestamp'][:19].replace('T', ' ')
            print(f"[{timestamp}] #{i}")
            print(f"👤 You: {entry['user']}")
            print(f"🤖 AI: {entry['assistant']}")
            if entry.get('intent'):
                print(f"🏷️  Intent: {entry['intent']}")
            print()
    
    def do_clear(self, arg):
        """Clear conversation history"""
        self.conversation_history.clear()
        print("📝 Conversation history cleared")
    
    def do_export(self, arg):
        """Export conversation history to file"""
        if not self.conversation_history:
            print("📝 No conversation history to export")
            return
        
        filename = arg if arg else f"conversation_{int(time.time())}.json"
        
        try:
            export_data = {
                'export_time': datetime.now().isoformat(),
                'conversation_history': self.conversation_history
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"📤 Conversation exported to: {filename}")
        
        except Exception as e:
            print(f"❌ Error exporting conversation: {str(e)}")
    
    def do_import(self, arg):
        """Import conversation history from file"""
        if not arg:
            print("❌ Please provide filename to import")
            return
        
        try:
            with open(arg, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            self.conversation_history.extend(import_data.get('conversation_history', []))
            print(f"📥 Conversation imported from: {arg}")
            print(f"📝 Added {len(import_data.get('conversation_history', []))} messages")
        
        except FileNotFoundError:
            print(f"❌ File not found: {arg}")
        except Exception as e:
            print(f"❌ Error importing conversation: {str(e)}")
    
    def do_status(self, arg):
        """Show current system status"""
        print("📊 Current Status:")
        print("─" * 40)
        print(f"🤖 AI Model: {'✅ Loaded' if self.ai_model else '❌ Not Loaded'}")
        print(f"🎤 Voice: {'✅ Enabled' if self.voice_enabled else '❌ Disabled'}")
        print(f"📁 Current Directory: {self.current_directory}")
        print(f"📝 Conversation History: {len(self.conversation_history)} messages")
        
        if self.ai_model:
            model_info = self.ai_model.get_model_info()
            print(f"🧠 Model Parameters: {model_info['parameters']['total']:,}")
            print(f"💻 Device: {model_info['device']}")
    
    def do_help(self, arg):
        """Show help information"""
        if arg:
            # Show help for specific command
            super().do_help(arg)
        else:
            # Show categorized help
            print("\n🤖 Conversational AI Assistant - Help")
            print("=" * 60)
            
            print("\n💬 Chat Commands:")
            print("  chat          - Start interactive chat mode")
            print("  voice [on/off] - Toggle voice interaction")
            print("  listen [sec]  - Listen to voice input")
            print("  speak <text>  - Speak text using TTS")
            print("  history       - Show conversation history")
            print("  clear         - Clear conversation history")
            
            print("\n📁 File Commands:")
            print("  ls [path]     - List directory contents")
            print("  cd <path>     - Change directory")
            print("  pwd           - Print working directory")
            print("  mkdir <name>  - Create directory")
            print("  touch <file>  - Create empty file")
            print("  cat <file>    - Display file contents")
            print("  rm <file/dir> - Remove file or directory")
            
            print("\n⚙️ Process Commands:")
            print("  ps            - List running processes")
            print("  kill <PID>    - Kill process by PID")
            print("  start <cmd>   - Start a process")
            
            print("\n💻 System Commands:")
            print("  sysinfo       - Display system information")
            print("  health        - Check system health")
            print("  status        - Show current status")
            
            print("\n💾 Data Commands:")
            print("  export <file> - Export conversation history")
            print("  import <file> - Import conversation history")
            
            print("\n🔧 Other Commands:")
            print("  help [cmd]    - Show help for command")
            print("  exit/quit     - Exit the application")
            print("\n" + "=" * 60)
    
    def do_exit(self, arg):
        """Exit the application"""
        print("👋 Goodbye!")
        return True
    
    def do_quit(self, arg):
        """Exit the application"""
        return self.do_exit(arg)
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    def default(self, line):
        """Handle unknown commands"""
        if line.strip():
            print(f"❌ Unknown command: {line}")
            print("💡 Type 'help' for available commands")

def main():
    """Main function to run the CLI interface"""
    parser = argparse.ArgumentParser(description="Conversational AI Assistant CLI")
    parser.add_argument("--voice", action="store_true", help="Enable voice interaction")
    parser.add_argument("--chat", action="store_true", help="Start directly in chat mode")
    
    args = parser.parse_args()
    
    # Create and run CLI interface
    cli = CLIInterface()
    
    if args.voice:
        cli.voice_enabled = True
        cli.initialize_ai_model()
    
    if args.chat:
        cli.do_chat("")
    else:
        try:
            cli.cmdloop()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
