# Custom AI Model - Conversational Computer Assistant

A sophisticated AI model designed for natural conversation, computer interaction, and voice capabilities.

## Features

- **Conversational AI**: Advanced neural networking for fluent dialogue
- **Computer Interaction**: File system, process management, and system operations
- **Voice Capabilities**: Text-to-Speech (TTS) and Speech-to-Text (STT)
- **Pre-trained Model**: Optimized for computer usage scenarios
- **Neural Network Architecture**: Professional implementation with optimization

## Installation

```bash
pip install -r requirements.txt
```

## Development servers with auto-reload

To run the FastAPI backend (port 8000) and Streamlit UI (port 8507) with automatic
restart on file changes, use the bundled helper script:

```bash
python scripts/dev_servers.py
```

You can tweak ports or add extra watch folders:

```bash
python scripts/dev_servers.py --api-port 8010 --ui-port 8600 --watch src/ui --watch configs
```

The script relies on the `watchfiles` dependency (already listed in
`requirements.txt`) and will restart either service when source files change or if
a process crashes.

## Project Structure

```
├── src/
│   ├── core/
│   │   ├── ai_model.py          # Main AI model implementation
│   │   ├── neural_network.py    # Neural network architecture
│   │   └── conversation.py      # Conversation management
│   ├── voice/
│   │   ├── tts.py              # Text-to-Speech engine
│   │   ├── stt.py              # Speech-to-Text engine
│   │   └── audio_processor.py  # Audio processing utilities
│   ├── computer/
│   │   ├── file_manager.py     # File system operations
│   │   ├── process_manager.py  # Process management
│   │   └── system_controller.py # System operations
│   ├── training/
│   │   ├── data_pipeline.py    # Training data pipeline
│   │   ├── model_trainer.py    # Model training logic
│   │   └── preprocessor.py     # Data preprocessing
│   └── ui/
│       ├── web_interface.py    # Web-based UI
│       ├── cli_interface.py    # Command-line interface
│       └── voice_interface.py  # Voice interaction interface
├── models/                      # Trained model storage
├── data/                       # Training and test data
├── config/                     # Configuration files
└── tests/                      # Unit tests
```

## Quick Start

```python
from src.core.ai_model import AIModel

# Initialize the AI model
ai = AIModel()

# Start conversation
response = ai.chat("Hello, how can you help me?")
print(response)

# Enable voice interaction
ai.enable_voice()
```

## Architecture

The system uses a multi-layered neural network architecture optimized for:
- Natural language understanding
- Context-aware responses
- Computer operation comprehension
- Voice processing

## Training

The model is pre-trained on:
- Conversational datasets
- Computer operation manuals
- Technical documentation
- Voice interaction patterns

## License

MIT License
