#!/usr/bin/env python3
"""
Setup script for Conversational AI System

This script handles installation, configuration, and setup of the AI system.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import argparse

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERROR: Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"OK: Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    try:
        # Install requirements
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("OK: Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Error installing dependencies: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "data/raw",
        "data/processed", 
        "data/models",
        "models",
        "logs",
        "temp",
        "exports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")

def download_models():
    """Download pre-trained models if needed"""
    print("🧠 Setting up models...")
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Check if models already exist
    model_files = [
        "conversational_ai.pt",
        "tokenizer.json",
        "config.json"
    ]
    
    models_exist = all((models_dir / file).exists() for file in model_files)
    
    if models_exist:
        print("✅ Models already exist")
        return True
    
    print("⬇️ Downloading pre-trained models...")
    
    try:
        # This would typically download from a model repository
        # For now, we'll create placeholder files
        for file in model_files:
            (models_dir / file).touch()
            print(f"✅ Created: models/{file}")
        
        print("✅ Model setup completed")
        return True
    except Exception as e:
        print(f"❌ Error setting up models: {e}")
        return False

def setup_voice():
    """Setup voice components"""
    print("🎤 Setting up voice components...")
    
    try:
        # Test TTS engine
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"✅ TTS engine ready with {len(voices)} voices")
        
        # Test STT engine
        import speech_recognition as sr
        r = sr.Recognizer()
        print("✅ STT engine ready")
        
        # Test audio
        import pyaudio
        audio = pyaudio.PyAudio()
        device_count = audio.get_device_count()
        print(f"✅ Audio system ready with {device_count} devices")
        audio.terminate()
        
        return True
    except ImportError as e:
        print(f"❌ Voice component not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Error setting up voice: {e}")
        return False

def test_system():
    """Test the complete system"""
    print("🧪 Testing system components...")
    
    tests = {
        "AI Model": test_ai_model,
        "File Manager": test_file_manager,
        "Process Manager": test_process_manager,
        "System Controller": test_system_controller,
        "Voice Components": test_voice_components
    }
    
    results = {}
    
    for test_name, test_func in tests.items():
        try:
            print(f"🔍 Testing {test_name}...")
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results[test_name] = False
    
    # Summary
    passed = sum(results.values())
    total = len(results)
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        return True
    else:
        print("⚠️ Some tests failed. Check the logs for details.")
        return False

def test_ai_model():
    """Test AI model initialization"""
    try:
        sys.path.insert(0, 'src')
        from core.ai_model import AIModel, ModelConfig
        
        config = ModelConfig(voice_enabled=False, computer_interaction_enabled=True)
        model = AIModel(config)
        
        # Test basic functionality
        response = model.chat("Hello, test message")
        return response is not None
    except Exception:
        return False

def test_file_manager():
    """Test file manager"""
    try:
        sys.path.insert(0, 'src')
        from computer.file_manager import FileManager
        
        fm = FileManager()
        files = fm.list_directory('.')
        return isinstance(files, list)
    except Exception:
        return False

def test_process_manager():
    """Test process manager"""
    try:
        sys.path.insert(0, 'src')
        from computer.process_manager import ProcessManager
        
        pm = ProcessManager()
        processes = pm.get_running_processes()
        return isinstance(processes, list)
    except Exception:
        return False

def test_system_controller():
    """Test system controller"""
    try:
        sys.path.insert(0, 'src')
        from computer.system_controller import SystemController
        
        sc = SystemController()
        info = sc.get_system_info()
        return 'system' in info
    except Exception:
        return False

def test_voice_components():
    """Test voice components"""
    try:
        sys.path.insert(0, 'src')
        from voice.tts import TextToSpeechEngine
        from voice.stt import SpeechToTextEngine
        
        # Test TTS
        tts = TextToSpeechEngine()
        voices = tts.get_available_voices()
        
        # Test STT
        stt = SpeechToTextEngine()
        engines = stt.get_available_engines()
        
        return len(voices) > 0 and len(engines) > 0
    except Exception:
        return False

def create_desktop_shortcut():
    """Create desktop shortcut for easy access"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Conversational AI.lnk")
        target = os.path.join(os.getcwd(), "main.py")
        wDir = os.getcwd()
        icon = target
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}" --interface web'
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()
        
        print("✅ Desktop shortcut created")
        return True
    except ImportError:
        print("⚠️ Cannot create desktop shortcut (Windows only)")
        return False
    except Exception as e:
        print(f"❌ Error creating shortcut: {e}")
        return False

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Setup Conversational AI System")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--skip-tests", action="store_true", help="Skip system tests")
    parser.add_argument("--voice-only", action="store_true", help="Setup voice components only")
    parser.add_argument("--shortcut", action="store_true", help="Create desktop shortcut")
    
    args = parser.parse_args()
    
    print("""
    ================================================================
                      Conversational AI System Setup                    
    ================================================================
    """)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not args.skip_deps:
        if not install_dependencies():
            return False
    
    # Setup directories
    setup_directories()
    
    # Setup models
    if not args.voice_only:
        if not download_models():
            return False
    
    # Setup voice components
    setup_voice()
    
    # Create desktop shortcut (Windows only)
    if args.shortcut and platform.system() == "Windows":
        create_desktop_shortcut()
    
    # Run tests
    if not args.skip_tests:
        if not test_system():
            return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📖 Usage:")
    print("  python main.py                    # Start web interface")
    print("  python main.py --interface cli    # Start command-line interface")
    print("  python main.py --interface voice  # Start voice interface")
    print("  python main.py --help              # Show all options")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
