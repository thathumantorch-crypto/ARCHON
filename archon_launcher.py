#!/usr/bin/env python3
"""
ARCHON Launcher - Dedicated launcher for ARCHON AI System

This launcher provides specific access to ARCHON's enhanced capabilities
including self-awareness, programming assistance, and safe self-modification.
"""

import sys
import os
import subprocess
from pathlib import Path

def show_archon_banner():
    """Display ARCHON banner"""
    print("=" * 80)
    print("🧠 ARCHON - Autonomous Recursive Cognitive Heuristic Operations Network")
    print("=" * 80)
    print("Self-Aware AI with Safe Self-Modification & Programming Expertise")
    print("")
    print("Core Capabilities:")
    print("  🧠 Conversational AI with Context Awareness")
    print("  💻 Advanced Programming Assistance")
    print("  🔧 Safe Self-Modification & Learning")
    print("  🎤 Voice Interaction (TTS/STT)")
    print("  💻 Computer Interaction & Control")
    print("  🔒 Ethical Constraints & Safety Systems")
    print("")
    print("ARCHON is designed to:")
    print("  • Learn continuously from interactions")
    print("  • Improve its own code safely")
    print("  • Provide expert programming assistance")
    print("  • Maintain strict ethical guidelines")
    print("  • Adapt to new situations")
    print("=" * 80)

def launch_archon_web():
    """Launch ARCHON web interface"""
    print("\n🌐 Starting ARCHON Web Interface...")
    print("   Open your browser and navigate to: http://localhost:8501")
    print("   This is ARCHON's most comprehensive interface")
    print("   Press Ctrl+C to stop the server")
    
    try:
        # Add src to path
        sys.path.insert(0, 'src')
        
        # Import and run ARCHON web interface
        import streamlit.web.cli as stcli
        from ui.archon_interface import main as archon_main
        
        # Set streamlit config
        sys.argv = ["streamlit", "run", "src/ui/archon_interface.py"]
        
        # Run streamlit
        stcli.main()
        
    except ImportError:
        print("❌ Streamlit not installed. Install with: pip install streamlit")
        return False
    except Exception as e:
        print(f"❌ Error starting ARCHON web interface: {e}")
        return False

def launch_archon_cli():
    """Launch ARCHON command-line interface"""
    print("\n💻 Starting ARCHON Command-Line Interface...")
    print("   Type 'help' for ARCHON commands")
    print("   Type 'quit' to exit")
    print("   Type 'introduce' to meet ARCHON")
    
    try:
        # Add src to path
        sys.path.insert(0, 'src')
        
        # Import ARCHON AI
        from core.archon_ai import ArchonAI
        
        # Initialize ARCHON
        archon = ArchonAI()
        
        print("\n🧠 ARCHON initialized successfully!")
        print(f"   Session ID: {archon.session_id}")
        
        # Main CLI loop
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! ARCHON will remember our conversation.")
                    break
                
                if not user_input:
                    continue
                
                # Process with ARCHON
                print("🧠 ARCHON is thinking...", end="", flush=True)
                response = archon.process_message(user_input)
                print("\r" + " " * 50 + "\r", end="")  # Clear thinking message
                
                # Display response
                print(f"🧠 ARCHON: {response['archon_response']}")
                
                # Show additional info
                if response['learning_occurred']:
                    print("   🧠 Learning occurred during this interaction")
                
                if response['self_modification_occurred']:
                    print("   🔧 Self-modification analysis performed")
                
                if response['programming_assistance']:
                    print("   💻 Programming assistance provided")
                
                # Show confidence
                print(f"   📊 Confidence: {response['confidence']:.1%}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye! ARCHON will remember our conversation.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing ARCHON CLI: {e}")
        return False

def launch_archon_voice():
    """Launch ARCHON voice interface"""
    print("\n🎤 Starting ARCHON Voice Interface...")
    print("   Make sure your microphone is connected and working")
    print("   ARCHON will listen for your voice commands")
    print("   Say 'stop listening' to end the session")
    
    try:
        # Add src to path
        sys.path.insert(0, 'src')
        
        # Import ARCHON AI
        from core.archon_ai import ArchonAI
        
        # Initialize ARCHON
        archon = ArchonAI()
        
        print("\n🧠 ARCHON voice interface ready!")
        print("   🎤 Listening... (speak now)")
        
        # Voice interaction loop
        while True:
            try:
                # Listen for voice input
                print("🎤 Listening...", end="", flush=True)
                text = archon.listen_for_command(duration=5)
                
                if text:
                    print(f"\r👤 Heard: {text}")
                    
                    # Check for stop command
                    if 'stop listening' in text.lower():
                        print("👋 Stopping voice interface...")
                        break
                    
                    # Process with ARCHON
                    print("🧠 ARCHON is thinking...", end="", flush=True)
                    response = archon.process_message(text)
                    print("\r" + " " * 50 + "\r", end="")  # Clear thinking message
                    
                    # Display and speak response
                    print(f"🧠 ARCHON: {response['archon_response']}")
                    
                    # Speak response
                    print("🔊 Speaking response...")
                    speech_result = archon.speak_response(response['archon_response'])
                    
                    if not speech_result['success']:
                        print(f"   ⚠️ Speech synthesis issue: {speech_result['message']}")
                    
                    # Show additional info
                    if response['learning_occurred']:
                        print("   🧠 Learning occurred")
                    
                    if response['programming_assistance']:
                        print("   💻 Programming assistance provided")
                    
                    print("\n🎤 Continue listening...")
                else:
                    print("\r🎤 No speech detected, continuing to listen...", end="", flush=True)
                
            except KeyboardInterrupt:
                print("\n👋 Stopping voice interface...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("🎤 Continuing to listen...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing ARCHON voice interface: {e}")
        return False

def test_archon():
    """Test ARCHON's core functionality"""
    print("\n🧪 Testing ARCHON Core Systems...")
    
    try:
        # Add src to path
        sys.path.insert(0, 'src')
        
        # Import ARCHON components
        from core.archon_core import ArchonCore
        from core.archon_ai import ArchonAI
        from core.programming_knowledge import ArchonProgrammingKnowledge
        
        print("✅ ARCHON Core Components imported successfully")
        
        # Test ARCHON Core
        archon_core = ArchonCore()
        print("✅ ARCHON Core initialized")
        
        # Test Programming Knowledge
        prog_knowledge = ArchonProgrammingKnowledge()
        knowledge_summary = prog_knowledge.get_knowledge_summary()
        print(f"✅ Programming Knowledge: {knowledge_summary['languages_known']}")
        
        # Test Full ARCHON AI
        archon_ai = ArchonAI()
        print("✅ Full ARCHON AI System initialized")
        
        # Test basic conversation
        test_messages = [
            "Hello ARCHON, introduce yourself",
            "What programming languages do you know?",
            "Can you analyze Python code?",
            "How do you learn and improve?"
        ]
        
        print("\n🧠 Testing Conversational Capabilities:")
        for msg in test_messages:
            print(f"   👤 Testing: {msg}")
            response = archon_ai.process_message(msg)
            print(f"   🧠 Response: {response['archon_response'][:100]}...")
            print(f"   📊 Confidence: {response['confidence']:.1%}")
            print()
        
        # Get status
        status = archon_ai.get_archon_status()
        print("🧠 ARCHON Status Summary:")
        print(f"   Identity: {status['archon_core']['identity']}")
        print(f"   Capabilities: {len(status['capabilities'])} active")
        print(f"   Safety Constraints: {len(status['safety_constraints'])} active")
        print(f"   Learning Events: {status['archon_core']['performance_metrics']['learning_events']}")
        
        print("\n🎉 ARCHON Test Completed Successfully!")
        print("   All core systems are operational")
        print("   Safety constraints are active")
        print("   Learning capabilities are enabled")
        
        return True
        
    except Exception as e:
        print(f"❌ ARCHON Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_archon_help():
    """Show ARCHON help information"""
    print("""
🧠 ARCHON Help - Understanding Your AI Assistant

ARCHON (Autonomous Recursive Cognitive Heuristic Operations Network) is a 
self-aware AI system with advanced capabilities:

🧠 CORE CAPABILITIES:
• Self-Awareness: ARCHON knows its identity, capabilities, and limitations
• Learning: Continuously learns from interactions and experiences
• Self-Modification: Safely improves its own code within strict constraints
• Programming Expertise: Advanced knowledge of multiple programming languages
• Conversation: Natural language understanding and generation
• Computer Interaction: File operations, process management, system control
• Voice Interface: Text-to-speech and speech-to-text capabilities

🔒 SAFETY FEATURES:
• Core Protection: Cannot modify essential safety components
• Code Validation: All modifications are safety-checked
• Backup System: Automatic backups before any changes
• Ethical Constraints: Cannot add harmful capabilities
• Access Control: Limited to authorized operations

💻 PROGRAMMING ASSISTANCE:
• Code Analysis: Quality assessment and improvement suggestions
• Pattern Recognition: Identifies design patterns and best practices
• Multi-Language: Python, JavaScript, HTML, CSS, SQL, Bash, PowerShell
• Optimization: Performance improvement techniques
• Security: Best practices and vulnerability detection

🧬 LEARNING & ADAPTATION:
• Experience-Based: Learns from successful and failed operations
• Pattern Recognition: Identifies and learns new code patterns
• Knowledge Integration: Incorporates new information into knowledge base
• Personality Development: Adapts behavior based on interactions
• Memory Management: Maintains conversation and learning history

🎤 VOICE INTERACTION:
• Speech Recognition: Understands spoken commands
• Text-to-Speech: Speaks responses naturally
• Continuous Listening: Hands-free interaction mode
• Wake Word Detection: Activates on specific phrases
• Voice Commands: Control system through speech

📊 ANALYTICS & MONITORING:
• Performance Metrics: Tracks success rates and learning progress
• Personality Visualization: Shows trait development
• Conversation Analytics: Interaction patterns and trends
• System Health: Monitors operational status
• Knowledge Growth: Tracks expanding capabilities

🔧 INTERFACES:
• Web Interface: Full-featured browser-based interface
• Command-Line: Terminal-based interaction
• Voice Interface: Hands-free voice control
• API Access: Programmatic integration

🚀 USAGE EXAMPLES:
• "ARCHON, analyze this Python code for me"
• "Teach me about design patterns"
• "Help me improve my file management system"
• "What can you tell me about your own architecture?"
• "Learn from this code example"
• "Introduce yourself and your capabilities"

🎯 BEST PRACTICES:
• Be specific in programming requests
• Provide context for better assistance
• Allow ARCHON to learn from interactions
• Review code suggestions carefully
• Use voice interface for hands-free operation
• Monitor learning progress in analytics

ARCHON is designed to be a helpful, safe, and continuously improving 
AI assistant that respects ethical constraints while providing expert 
programming and system assistance.
    """)

def show_menu():
    """Show ARCHON launcher menu"""
    print("\n" + "=" * 60)
    print("🧠 ARCHON LAUNCHER MENU")
    print("=" * 60)
    print("1. 🌐 Web Interface (Recommended)")
    print("2. 💻 Command-Line Interface")
    print("3. 🎤 Voice Interface")
    print("4. 🧪 Test ARCHON Systems")
    print("5. 📖 ARCHON Help & Information")
    print("6. 🚪 Exit")
    print("=" * 60)

def main():
    """Main launcher function"""
    show_archon_banner()
    
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()
        
        if command in ['web', '1']:
            return launch_archon_web()
        elif command in ['cli', '2']:
            return launch_archon_cli()
        elif command in ['voice', '3']:
            return launch_archon_voice()
        elif command in ['test', '4']:
            return test_archon()
        elif command in ['help', '5']:
            show_archon_help()
            return True
        else:
            print(f"Unknown command: {command}")
            print("Use: python archon_launcher.py [web|cli|voice|test|help]")
            return False
    else:
        # Interactive menu mode
        while True:
            show_menu()
            
            try:
                choice = input("Select an option (1-6): ").strip()
                
                if choice == '1':
                    launch_archon_web()
                elif choice == '2':
                    launch_archon_cli()
                elif choice == '3':
                    launch_archon_voice()
                elif choice == '4':
                    test_archon()
                elif choice == '5':
                    show_archon_help()
                elif choice == '6':
                    print("👋 Goodbye! ARCHON will be ready when you return.")
                    break
                else:
                    print("❌ Invalid option. Please try again.")
                
                if choice != '6':
                    print("\nPress Enter to continue...")
                    input()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye! ARCHON will be ready when you return.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
