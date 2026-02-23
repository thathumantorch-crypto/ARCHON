#!/usr/bin/env python3
"""
ARCHON Launcher - Simple launcher without Unicode characters
"""

import sys
import os
import subprocess

def show_banner():
    print("=" * 80)
    print("ARCHON - Autonomous Recursive Cognitive Heuristic Operations Network")
    print("=" * 80)
    print("Self-Aware AI with Safe Self-Modification & Programming Expertise")
    print("")
    print("Core Capabilities:")
    print("  - Conversational AI with Context Awareness")
    print("  - Advanced Programming Assistance")
    print("  - Safe Self-Modification & Learning")
    print("  - Voice Interaction (TTS/STT)")
    print("  - Computer Interaction & Control")
    print("  - Ethical Constraints & Safety Systems")
    print("")
    print("ARCHON is designed to:")
    print("  - Learn continuously from interactions")
    print("  - Improve its own code safely")
    print("  - Provide expert programming assistance")
    print("  - Maintain strict ethical guidelines")
    print("  - Adapt to new situations")
    print("=" * 80)

def launch_web():
    """Launch ARCHON enhanced web interface"""
    print("\nStarting ARCHON Enhanced Web Interface...")
    print("   Open your browser and navigate to: http://localhost:8507")
    print("   Press Ctrl+C to stop the server")

    try:
        sys.path.insert(0, 'src')
        import streamlit.web.cli as stcli

        sys.argv = [
            "streamlit",
            "run",
            "src/ui/enhanced_web_interface.py",
            "--server.port",
            "8507",
        ]

        stcli.main()

    except ImportError:
        print("ERROR: Streamlit not installed. Install with: pip install streamlit")
        return False
    except Exception as e:
        print(f"ERROR: Error starting ARCHON web interface: {e}")
        return False

def launch_dev_servers():
    """Launch FastAPI + Streamlit dev servers with auto-reload"""
    print("\nStarting ARCHON dev servers with auto-reload...")
    print("   FastAPI -> http://localhost:8000")
    print("   Streamlit -> http://localhost:8507")
    print("   Press Ctrl+C to stop both servers.")

    script_path = os.path.join('scripts', 'dev_servers.py')
    if not os.path.exists(script_path):
        print("ERROR: scripts/dev_servers.py not found. Did you pull the latest repo?")
        return False

    try:
        subprocess.call([sys.executable, script_path])
        return True
    except KeyboardInterrupt:
        print("\nDev servers stopped.")
        return True
    except Exception as exc:
        print(f"ERROR: Unable to launch dev servers: {exc}")
        return False

def launch_cli():
    """Launch ARCHON command-line interface"""
    print("\nStarting ARCHON Command-Line Interface...")
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
        
        print("\nARCHON initialized successfully!")
        print(f"   Session ID: {archon.session_id}")
        
        # Main CLI loop
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! ARCHON will remember our conversation.")
                    break
                
                if not user_input:
                    continue
                
                # Process with ARCHON
                print("ARCHON is thinking...", end="", flush=True)
                response = archon.process_message(user_input)
                print("\r" + " " * 50 + "\r", end="")  # Clear thinking message
                
                # Display response
                print(f"ARCHON: {response['archon_response']}")
                
                # Show additional info
                if response['learning_occurred']:
                    print("   Learning occurred during this interaction")
                
                if response['self_modification_occurred']:
                    print("   Self-modification analysis performed")
                
                if response['programming_assistance']:
                    print("   Programming assistance provided")
                
                # Show confidence
                print(f"   Confidence: {response['confidence']:.1%}")
                
            except KeyboardInterrupt:
                print("\nGoodbye! ARCHON will remember our conversation.")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error initializing ARCHON CLI: {e}")
        return False

def test_archon():
    """Test ARCHON systems"""
    print("\nTesting ARCHON Core Systems...")
    
    try:
        # Add src to path
        sys.path.insert(0, 'src')
        
        # Import ARCHON components
        from core.archon_core import ArchonCore
        from core.archon_ai import ArchonAI
        from core.programming_knowledge import ArchonProgrammingKnowledge
        
        print("OK: ARCHON Core Components imported successfully")
        
        # Test ARCHON Core
        archon_core = ArchonCore()
        print("OK: ARCHON Core initialized")
        
        # Test Programming Knowledge
        prog_knowledge = ArchonProgrammingKnowledge()
        knowledge_summary = prog_knowledge.get_knowledge_summary()
        print(f"OK: Programming Knowledge: {knowledge_summary['languages_known']}")
        
        # Test Full ARCHON AI
        archon_ai = ArchonAI()
        print("OK: Full ARCHON AI System initialized")
        
        # Test basic conversation
        test_messages = [
            "Hello ARCHON, introduce yourself",
            "What programming languages do you know?",
            "Can you analyze Python code?",
            "How do you learn and improve?"
        ]
        
        print("\nTesting Conversational Capabilities:")
        for msg in test_messages:
            print(f"   Testing: {msg}")
            response = archon_ai.process_message(msg)
            print(f"   Response: {response['archon_response'][:50]}...")
            print(f"   Confidence: {response['confidence']:.1%}")
        
        # Get status
        status = archon_ai.get_archon_status()
        print("\nARCHON Status Summary:")
        print(f"   Identity: {status['archon_core']['identity']}")
        print(f"   Capabilities: {len(status['capabilities'])} active")
        print(f"   Safety Constraints: {len(status['safety_constraints'])} active")
        print(f"   Learning Events: {status['archon_core']['performance_metrics']['learning_events']}")
        
        print("\nARCHON Test Completed Successfully!")
        print("   All core systems are operational")
        print("   Safety constraints are active")
        print("   Learning capabilities are enabled")
        
        return True
        
    except Exception as e:
        print(f"ARCHON Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_menu():
    """Show menu"""
    print("\n" + "=" * 60)
    print("ARCHON LAUNCHER MENU")
    print("=" * 60)
    print("1. Web Interface (Recommended)")
    print("2. Dev Servers (FastAPI + Streamlit auto-reload)")
    print("3. Command-Line Interface")
    print("4. Test ARCHON Systems")
    print("5. Exit")
    print("=" * 60)

def main():
    """Main launcher function"""
    show_banner()
    
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()
        
        if command in ['web', '1']:
            return launch_web()
        elif command in ['dev', '2']:
            return launch_dev_servers()
        elif command in ['cli', '3']:
            return launch_cli()
        elif command in ['test', '4']:
            return test_archon()
        else:
            print(f"Unknown command: {command}")
            print("Use: python run_archon.py [web|dev|cli|test]")
            return False
    else:
        # Interactive menu mode
        while True:
            show_menu()
            
            try:
                choice = input("Select an option (1-4): ").strip()
                
                if choice == '1':
                    launch_web()
                elif choice == '2':
                    launch_dev_servers()
                elif choice == '3':
                    launch_cli()
                elif choice == '4':
                    test_archon()
                elif choice == '5':
                    print("Goodbye! ARCHON will be ready when you return.")
                    break
                else:
                    print("Invalid option. Please try again.")
                
                if choice != '5':
                    print("\nPress Enter to continue...")
                    input()
                
            except KeyboardInterrupt:
                print("\nGoodbye! ARCHON will be ready when you return.")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
