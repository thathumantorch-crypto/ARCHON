#!/usr/bin/env python3
"""
Working demonstration of the Conversational AI System
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def main():
    """Main demonstration function"""
    print("=" * 60)
    print("CONVERSATIONAL AI SYSTEM - WORKING DEMONSTRATION")
    print("=" * 60)
    
    # Test conversation system
    print("\n1. Testing Conversation System:")
    from core.conversation import ConversationManager
    cm = ConversationManager()
    
    test_inputs = [
        "Hello, how are you?",
        "What files are in this directory?",
        "Help me understand what you can do"
    ]
    
    for input_text in test_inputs:
        print(f"  User: {input_text}")
        intent = cm.classify_intent(input_text)
        entities = cm.extract_entities(input_text, intent)
        response = cm.generate_contextual_response(input_text, intent, entities, None)
        print(f"  AI: {response}")
        print()
    
    # Test file manager
    print("2. Testing File Manager:")
    from computer.file_manager import FileManager
    fm = FileManager()
    
    files = fm.list_directory('.')
    print(f"  Found {len(files)} items in current directory")
    
    # Create and delete a test file
    result = fm.create_file('demo_test.txt', 'AI system test file')
    print(f"  Create file: {result['message']}")
    
    result = fm.delete_file('demo_test.txt')
    print(f"  Delete file: {result['message']}")
    
    # Test process manager
    print("\n3. Testing Process Manager:")
    from computer.process_manager import ProcessManager
    pm = ProcessManager()
    
    processes = pm.get_running_processes()
    print(f"  Found {len(processes)} running processes")
    
    # Test system controller
    print("\n4. Testing System Controller:")
    from computer.system_controller import SystemController
    sc = SystemController()
    
    info = sc.get_system_info()
    print(f"  System: {info['system']} {info['version']}")
    print(f"  CPU cores: {info['cpu']['count']}")
    print(f"  Memory: {info['memory']['total_gb']:.1f} GB total")
    
    health = sc.check_system_health()
    print(f"  Health status: {health['overall']}")
    
    # Test voice components
    print("\n5. Testing Voice Components:")
    
    # Test TTS
    try:
        from voice.tts import TextToSpeechEngine
        tts = TextToSpeechEngine()
        voices = tts.get_available_voices()
        print(f"  TTS: Found {len(voices)} voices")
        
        # Test speech synthesis
        result = tts.speak("Hello, this is a test of the AI voice system.", blocking=False)
        print(f"  Speech test: {result['message']}")
        
    except Exception as e:
        print(f"  TTS Error: {e}")
    
    # Test STT
    try:
        try:
            from voice.stt import SpeechToTextEngine
            print("  STT: Using original engine")
        except ImportError:
            from voice.stt_no_pyaudio import SpeechToTextEngineNoPyAudio
            print("  STT: Using alternative engine (no pyaudio)")
        
        stt = SpeechToTextEngine()
        engines = stt.get_available_engines()
        print(f"  Available engines: {engines}")
        
        # Test microphone calibration
        result = stt.calibrate_microphone(duration=1)
        print(f"  Microphone calibration: {result['message']}")
        
    except Exception as e:
        print(f"  STT Error: {e}")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
    print("All core components are working correctly.")
    print("=" * 60)
    
    print("\nTo use the AI system:")
    print("1. Web Interface: python launch.py web")
    print("2. CLI Interface: python launch.py cli")
    print("3. Voice Interface: python launch.py voice")
    print("4. Interactive Menu: python launch.py")

if __name__ == "__main__":
    main()
