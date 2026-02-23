#!/usr/bin/env python3
"""
Main entry point for the Conversational AI System

This script provides multiple interfaces to interact with the AI:
- Web interface (Streamlit)
- Command-line interface
- Voice interface
- Direct API access

Usage:
    python main.py [--interface TYPE] [--options]

Interfaces:
    - web: Web-based interface (default)
    - cli: Command-line interface
    - voice: Voice-only interface
    - api: REST API server
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "ai_system.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_web_interface(args):
    """Run the web interface"""
    try:
        import streamlit.web.cli as stcli
        
        print("Starting Enhanced Web Interface...")
        print("Open your browser and navigate to: http://localhost:8507")
        print("The interface will start automatically...")
        
        # Set streamlit config
        sys.argv = ["streamlit", "run", "src/ui/enhanced_web_interface.py", "--server.port", "8507"]
        
        # Run streamlit
        stcli.main()
        
    except ImportError:
        print("ERROR: Streamlit not installed. Install with: pip install streamlit")
        return False
    except Exception as e:
        print(f"ERROR: Error starting web interface: {str(e)}")
        return False

def run_cli_interface(args):
    """Run the command-line interface"""
    try:
        from src.ui.cli_interface import main as cli_main
        
        print("💻 Starting Command-Line Interface...")
        
        # Set up CLI arguments
        cli_args = []
        if args.voice:
            cli_args.extend(["--voice"])
        if args.chat:
            cli_args.extend(["--chat"])
        
        # Override sys.argv for CLI
        sys.argv = ["cli_interface.py"] + cli_args
        
        cli_main()
        
    except Exception as e:
        print(f"❌ Error starting CLI interface: {str(e)}")
        return False

def run_voice_interface(args):
    """Run the voice-only interface"""
    try:
        from src.ui.voice_interface import main as voice_main
        
        print("🎤 Starting Voice Interface...")
        print("💡 Make sure your microphone is connected and working")
        
        voice_main()
        
    except Exception as e:
        print(f"❌ Error starting voice interface: {str(e)}")
        return False

def run_api_server(args):
    """Run the REST API server"""
    try:
        import uvicorn
        from src.ui.api_server import app, main as api_main
        
        print("🔌 Starting API Server...")
        print(f"📡 API will be available at: http://localhost:{args.port}")
        print("📖 API documentation: http://localhost:{args.port}/docs")
        
        # Configure uvicorn
        uvicorn_config = {
            "app": app,
            "host": args.host,
            "port": args.port,
            "reload": args.reload,
            "log_level": args.api_log_level.lower()
        }
        
        uvicorn.run(**uvicorn_config)
        
    except ImportError:
        print("❌ FastAPI/Uvicorn not installed. Install with: pip install fastapi uvicorn")
        return False
    except Exception as e:
        print(f"❌ Error starting API server: {str(e)}")
        return False

def run_training(args):
    """Run model training"""
    try:
        from src.training.training_script import main as training_main
        
        print("🧠 Starting Model Training...")
        
        # Set up training arguments
        training_args = {
            'epochs': args.epochs,
            'batch_size': args.batch_size,
            'learning_rate': args.learning_rate,
            'data_dir': args.data_dir,
            'model_dir': args.model_dir,
            'resume': args.resume
        }
        
        training_main(training_args)
        
    except Exception as e:
        print(f"❌ Error during training: {str(e)}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'torch',
        'transformers',
        'streamlit',
        'pyttsx3',
        'speechrecognition',
        'psutil',
        'numpy',
        'pandas'
    ]
    package_aliases = {
        'speechrecognition': ['speech_recognition'],
    }
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            aliases = package_aliases.get(package, [])
            for alias in aliases:
                try:
                    __import__(alias)
                    break
                except ImportError:
                    continue
            else:
                missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        return False
    else:
        print("✅ All dependencies are installed!")
        return True

def show_system_info():
    """Display system information"""
    import platform
    import torch
    
    print("💻 System Information:")
    print("=" * 50)
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"Architecture: {platform.machine()}")
    
    if torch.cuda.is_available():
        print(f"CUDA: {torch.version.cuda}")
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print("CUDA: Not available")
    
    print("=" * 50)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Conversational AI System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                           # Start web interface (default)
    python main.py --interface cli           # Start command-line interface
    python main.py --interface voice         # Start voice interface
    python main.py --interface api           # Start API server
    python main.py --train                   # Start model training
    python main.py --check-deps              # Check dependencies
    python main.py --system-info             # Show system information
        """
    )
    
    # Interface selection
    parser.add_argument(
        "--interface", "-i",
        choices=["web", "cli", "voice", "api"],
        default="web",
        help="Interface type to run (default: web)"
    )
    
    # Web interface options
    parser.add_argument("--web-port", type=int, default=8501, help="Web interface port")
    
    # CLI interface options
    parser.add_argument("--voice", action="store_true", help="Enable voice in CLI")
    parser.add_argument("--chat", action="store_true", help="Start directly in chat mode")
    
    # Voice interface options
    parser.add_argument("--voice-mode", choices=["command", "conversation", "assistant"], 
                       default="conversation", help="Voice interaction mode")
    
    # API server options
    parser.add_argument("--host", default="127.0.0.1", help="API server host")
    parser.add_argument("--port", type=int, default=8000, help="API server port")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for API")
    parser.add_argument("--api-log-level", default="info", choices=["debug", "info", "warning", "error"], help="API log level")
    
    # Training options
    parser.add_argument("--train", action="store_true", help="Run model training")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Training batch size")
    parser.add_argument("--learning-rate", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--data-dir", default="data", help="Training data directory")
    parser.add_argument("--model-dir", default="models", help="Model save directory")
    parser.add_argument("--resume", action="store_true", help="Resume training from checkpoint")
    
    # Utility options
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies")
    parser.add_argument("--system-info", action="store_true", help="Show system information")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Show banner
    print("""
    ================================================================
                Conversational AI System
    ================================================================
    * Advanced AI with voice, computer interaction, and more
    ================================================================
    """)
    
    # Handle utility commands
    if args.check_deps:
        return check_dependencies()
    
    if args.system_info:
        show_system_info()
        return True
    
    # Check dependencies first
    if not check_dependencies():
        return False
    
    # Show system info
    show_system_info()
    
    # Run appropriate interface
    try:
        if args.train:
            return run_training(args)
        elif args.interface == "web":
            return run_web_interface(args)
        elif args.interface == "cli":
            return run_cli_interface(args)
        elif args.interface == "voice":
            return run_voice_interface(args)
        elif args.interface == "api":
            return run_api_server(args)
        else:
            print(f"❌ Unknown interface: {args.interface}")
            return False
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return True
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
