#!/usr/bin/env python3
"""
Simple launcher for the Conversational AI System
"""

import sys
import os
import subprocess
from pathlib import Path

def launch_web_interface():
    """Launch the web interface"""
    print("Starting Web Interface...")
    print("Open your browser and navigate to: http://localhost:8507")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Add src to path
        sys.path.insert(0, 'src')
        
        # Import and run web interface
        import streamlit.web.cli as stcli
        
        # Set streamlit config
        sys.argv = ["streamlit", "run", "src/ui/enhanced_web_interface.py", "--server.port", "8507"]
        
        # Run streamlit
        stcli.main()
        
    except ImportError:
        print("ERROR: Streamlit not installed. Install with: pip install streamlit")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def launch_cli_interface():
    """Launch the CLI interface"""
    print("Starting Command-Line Interface...")
    
    try:
        # Add src to path
        sys.path.insert(0, 'src')
        
        # Import and run CLI interface
        from ui.cli_interface import main as cli_main
        cli_main()
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def launch_voice_interface():
    """Launch the voice interface"""
    print("Starting Voice Interface...")
    print("Make sure your microphone is connected and working")
    
    try:
        # Add src to path
        sys.path.insert(0, 'src')
        
        # Import and run voice interface
        from ui.voice_interface import main as voice_main
        voice_main()
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def show_menu():
    """Show the main menu"""
    print("=" * 60)
    print("Conversational AI System Launcher")
    print("=" * 60)
    print("1. Web Interface")
    print("2. Command-Line Interface")
    print("3. Voice Interface")
    print("4. Exit")
    print("=" * 60)

def main():
    """Main launcher function"""
    if len(sys.argv) > 1:
        # Command line mode
        interface = sys.argv[1].lower()
        
        if interface in ['web', '1']:
            return launch_web_interface()
        elif interface in ['cli', '2']:
            return launch_cli_interface()
        elif interface in ['voice', '3']:
            return launch_voice_interface()
        else:
            print(f"Unknown interface: {interface}")
            return False
    else:
        # Interactive menu mode
        while True:
            show_menu()
            
            try:
                choice = input("Select an option (1-4): ").strip()
                
                if choice == '1':
                    launch_web_interface()
                elif choice == '2':
                    launch_cli_interface()
                elif choice == '3':
                    launch_voice_interface()
                elif choice == '4':
                    print("Goodbye!")
                    break
                else:
                    print("Invalid option. Please try again.")
                
                print("\nPress Enter to continue...")
                input()
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
