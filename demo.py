#!/usr/bin/env python3
"""
Simple demonstration of the Conversational AI System
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def demo_conversation():
    """Demonstrate the conversation system"""
    print("=" * 60)
    print("CONVERSATIONAL AI SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    from core.conversation import ConversationManager
    from computer.file_manager import FileManager
    from computer.process_manager import ProcessManager
    from computer.system_controller import SystemController
    
    # Initialize components
    cm = ConversationManager()
    fm = FileManager()
    pm = ProcessManager()
    sc = SystemController()
    
    print("\n🤖 AI Assistant is ready!")
    print("Type 'quit' to exit, 'help' for commands")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\n📖 Available commands:")
                print("  'list files' - List files in current directory")
                print("  'list processes' - Show running processes")
                print("  'system info' - Show system information")
                print("  'system health' - Check system health")
                print("  'create file <name>' - Create a new file")
                print("  'help' - Show this help message")
                print("  'quit' - Exit the demo")
                continue
            
            # Classify intent and generate response
            intent = cm.classify_intent(user_input)
            entities = cm.extract_entities(user_input, intent)
            
            # Handle specific commands
            if 'list files' in user_input.lower():
                files = fm.list_directory('.')
                response = f"I found {len(files)} items in the current directory:"
                for file_info in files[:10]:  # Show first 10
                    response += f"\n  📄 {file_info['name']} ({file_info['type']})"
                if len(files) > 10:
                    response += f"\n  ... and {len(files) - 10} more items"
            
            elif 'list processes' in user_input.lower():
                processes = pm.get_running_processes()
                response = f"I found {len(processes)} running processes:"
                for proc in processes[:10]:  # Show first 10
                    response += f"\n  🔧 {proc.name} (PID: {proc.pid}, CPU: {proc.cpu_percent:.1f}%)"
                if len(processes) > 10:
                    response += f"\n  ... and {len(processes) - 10} more processes"
            
            elif 'system info' in user_input.lower():
                info = sc.get_system_info()
                response = f"System Information:\n"
                response += f"  💻 OS: {info['system']} {info['version']}\n"
                response += f"  🧠 CPU: {info['cpu']['count']} cores\n"
                response += f"  💾 Memory: {info['memory']['total_gb']:.1f} GB total, {info['memory']['available_gb']:.1f} GB available"
            
            elif 'system health' in user_input.lower():
                health = sc.check_system_health()
                response = f"System Health: {health['overall'].upper()}\n"
                if health['warnings']:
                    response += f"⚠️ Warnings: {len(health['warnings'])}\n"
                if health['errors']:
                    response += f"❌ Errors: {len(health['errors'])}"
                else:
                    response += "✅ No critical issues detected"
            
            elif 'create file' in user_input.lower():
                # Extract filename from entities or input
                filename = entities.get('file_names', ['demo.txt'])[0]
                if not filename:
                    # Simple extraction
                    words = user_input.split()
                    for i, word in enumerate(words):
                        if word.lower() == 'file' and i + 1 < len(words):
                            filename = words[i + 1]
                            break
                
                if filename:
                    result = fm.create_file(filename, "This file was created by the AI assistant.")
                    if result['success']:
                        response = f"✅ Successfully created file: {filename}"
                    else:
                        response = f"❌ Error creating file: {result['message']}"
                else:
                    response = "Please specify a filename after 'create file'"
            
            else:
                # Use conversation manager for general responses
                response = cm.generate_contextual_response(user_input, intent, entities, None)
            
            print(f"🤖 AI: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def demo_voice():
    """Demonstrate voice components"""
    print("\n" + "=" * 60)
    print("VOICE COMPONENTS DEMONSTRATION")
    print("=" * 60)
    
    try:
        # Test TTS
        from voice.tts import TextToSpeechEngine
        
        tts = TextToSpeechEngine()
        voices = tts.get_available_voices()
        
        print(f"🔊 Text-to-Speech: Found {len(voices)} voices")
        for i, voice in enumerate(voices):
            print(f"  {i+1}. {voice['name']} ({voice['gender']})")
        
        # Test speech
        print("\n🗣️ Testing speech synthesis...")
        result = tts.speak("Hello! This is the AI assistant speaking to you.", blocking=False)
        print(f"Result: {result['message']}")
        
    except Exception as e:
        print(f"❌ TTS Error: {e}")
    
    try:
        # Test STT
        try:
            from voice.stt import SpeechToTextEngine
            print("\n🎤 Speech-to-Text: Using original engine")
        except ImportError:
            from voice.stt_no_pyaudio import SpeechToTextEngineNoPyAudio
            print("\n🎤 Speech-to-Text: Using alternative engine (no pyaudio)")
        
        stt = SpeechToTextEngine()
        engines = stt.get_available_engines()
        print(f"Available engines: {engines}")
        
        # Test microphone
        print("\n🎤 Testing microphone...")
        result = stt.calibrate_microphone(duration=2)
        print(f"Calibration: {result['message']}")
        
        # Optional: Test listening (uncomment to try)
        # print("🎤 Listening for 3 seconds... Say something!")
        # text = stt.listen(duration=3)
        # if text:
        #     print(f"✅ Recognized: {text}")
        # else:
        #     print("❌ No speech detected")
        
    except Exception as e:
        print(f"❌ STT Error: {e}")

def main():
    """Main demonstration function"""
    print("🚀 Starting Conversational AI System Demo")
    print("This demo showcases the core capabilities of the AI system")
    
    # Run conversation demo
    demo_conversation()
    
    # Run voice demo
    demo_voice()
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed successfully!")
    print("The AI system is ready for use!")
    print("=" * 60)

if __name__ == "__main__":
    main()
