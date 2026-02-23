import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
import threading
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_model import AIModel, ModelConfig
from computer.file_manager import FileManager
from computer.process_manager import ProcessManager
from computer.system_controller import SystemController
from voice.tts import TextToSpeechEngine
try:
    from voice.stt import SpeechToTextEngine
except ImportError:
    print("⚠️ Using alternative STT engine (no pyaudio)")
    from voice.stt_no_pyaudio import SpeechToTextEngineNoPyAudio as SpeechToTextEngine

class WebInterface:
    """
    Modern web interface for the conversational AI system
    """
    
    def __init__(self):
        self.ai_model = None
        self.file_manager = FileManager()
        self.process_manager = ProcessManager()
        self.system_controller = SystemController()
        self.tts_engine = None
        self.stt_engine = None
        
        # Session state initialization
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        if 'voice_enabled' not in st.session_state:
            st.session_state.voice_enabled = False
        if 'current_directory' not in st.session_state:
            st.session_state.current_directory = os.getcwd()
    
    def initialize_ai_model(self):
        """Initialize the AI model"""
        if 'ai_model' not in st.session_state:
            with st.spinner("Initializing AI Model..."):
                try:
                    config = ModelConfig(
                        voice_enabled=st.session_state.voice_enabled,
                        computer_interaction_enabled=True
                    )
                    self.ai_model = AIModel(config)
                    st.session_state.ai_model = self.ai_model
                    
                    # Initialize voice engines if enabled
                    if st.session_state.voice_enabled:
                        self.tts_engine = TextToSpeechEngine()
                        self.stt_engine = SpeechToTextEngine()
                        st.session_state.tts_engine = self.tts_engine
                        st.session_state.stt_engine = self.stt_engine
                    
                    st.success("AI Model initialized successfully!")
                except Exception as e:
                    st.error(f"Error initializing AI Model: {str(e)}")
                    return False
        else:
            self.ai_model = st.session_state.ai_model
            if st.session_state.voice_enabled:
                self.tts_engine = st.session_state.get('tts_engine')
                self.stt_engine = st.session_state.get('stt_engine')
        
        return True
    
    def render_sidebar(self):
        """Render the sidebar with controls"""
        with st.sidebar:
            st.title("🤖 AI Assistant")
            
            # Model status
            st.subheader("Model Status")
            if self.ai_model:
                st.success("✅ Model Loaded")
                model_info = self.ai_model.get_model_info()
                st.json({
                    "Parameters": f"{model_info['parameters']['total']:,}",
                    "Device": model_info['device'],
                    "Session": model_info['session_id']
                })
            else:
                st.error("❌ Model Not Loaded")
                if st.button("Initialize Model"):
                    self.initialize_ai_model()
            
            st.divider()
            
            # Voice controls
            st.subheader("🎤 Voice Controls")
            voice_enabled = st.checkbox("Enable Voice", value=st.session_state.voice_enabled)
            
            if voice_enabled != st.session_state.voice_enabled:
                st.session_state.voice_enabled = voice_enabled
                if voice_enabled:
                    self.initialize_ai_model()
            
            if st.session_state.voice_enabled and self.tts_engine:
                # TTS Settings
                st.subheader("🔊 Text-to-Speech")
                rate = st.slider("Speech Rate", 50, 400, self.tts_engine.settings.rate)
                volume = st.slider("Volume", 0.0, 1.0, self.tts_engine.settings.volume)
                
                if st.button("Apply Voice Settings"):
                    self.tts_engine.set_rate(rate)
                    self.tts_engine.set_volume(volume)
                    st.success("Voice settings updated!")
                
                # Voice selection
                voices = self.tts_engine.get_available_voices()
                if voices:
                    voice_names = [v['name'] for v in voices]
                    selected_voice = st.selectbox("Select Voice", voice_names)
                    if st.button("Change Voice"):
                        voice_idx = voice_names.index(selected_voice)
                        result = self.tts_engine.set_voice(voice_idx)
                        if result['success']:
                            st.success(f"Voice changed to: {selected_voice}")
            
            st.divider()
            
            # System controls
            st.subheader("⚙️ System Controls")
            
            if st.button("📊 System Info"):
                with st.spinner("Getting system information..."):
                    system_info = self.system_controller.get_system_info()
                    st.session_state.system_info = system_info
            
            if st.button("🔄 Running Processes"):
                with st.spinner("Getting running processes..."):
                    processes = self.process_manager.get_running_processes()
                    st.session_state.processes = processes
            
            if st.button("📁 Current Directory"):
                with st.spinner("Getting directory contents..."):
                    files = self.file_manager.list_directory()
                    st.session_state.current_files = files
    
    def render_chat_interface(self):
        """Render the main chat interface"""
        st.title("💬 Conversational AI Assistant")
        
        # Chat history
        chat_container = st.container()
        
        with chat_container:
            # Display conversation history
            for i, message in enumerate(st.session_state.conversation_history):
                if message['role'] == 'user':
                    st.chat_message("user").write(message['content'])
                else:
                    st.chat_message("assistant").write(message['content'])
                    
                    # Show operation results if any
                    if 'operation_result' in message and message['operation_result']:
                        with st.expander("🔧 Operation Details"):
                            st.json(message['operation_result'])
        
        # Input area
        user_input = st.chat_input("Type your message here...")
        
        if user_input and self.ai_model:
            # Add user message to history
            st.session_state.conversation_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': time.time()
            })
            
            # Get AI response
            with st.spinner("Thinking..."):
                response = self.ai_model.chat(user_input)
            
            # Add assistant response to history
            st.session_state.conversation_history.append({
                'role': 'assistant',
                'content': response['text'],
                'timestamp': time.time(),
                'operation_result': response.get('operation_result'),
                'intent': response.get('intent'),
                'entities': response.get('entities')
            })
            
            # Rerun to display the new messages
            st.rerun()
        
        # Voice input (if enabled)
        if st.session_state.voice_enabled and self.stt_engine:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎤 Start Listening"):
                    with st.spinner("Listening..."):
                        text = self.stt_engine.listen(duration=5)
                        if text:
                            st.session_state.voice_input = text
                            st.success(f"Heard: {text}")
                        else:
                            st.warning("No speech detected")
            
            with col2:
                if st.button("🔊 Test Voice"):
                    if self.tts_engine:
                        self.tts_engine.speak("Hello! This is a test of the voice system.")
                        st.success("Voice test completed")
    
    def render_file_manager(self):
        """Render file manager interface"""
        st.title("📁 File Manager")
        
        # Current directory
        col1, col2 = st.columns([3, 1])
        
        with col1:
            current_dir = st.text_input("Current Directory", value=st.session_state.current_directory)
        
        with col2:
            if st.button("🔄 Refresh"):
                st.session_state.current_directory = current_dir
                files = self.file_manager.list_directory(current_dir)
                st.session_state.current_files = files
                st.rerun()
        
        # File operations
        st.subheader("File Operations")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            new_file_name = st.text_input("New File Name")
            if st.button("📄 Create File") and new_file_name:
                result = self.file_manager.create_file(f"{current_dir}/{new_file_name}")
                if result['success']:
                    st.success(f"File created: {new_file_name}")
                else:
                    st.error(result['message'])
        
        with col2:
            new_folder_name = st.text_input("New Folder Name")
            if st.button("📁 Create Folder") and new_folder_name:
                result = self.file_manager.create_directory(f"{current_dir}/{new_folder_name}")
                if result['success']:
                    st.success(f"Folder created: {new_folder_name}")
                else:
                    st.error(result['message'])
        
        # File list
        if 'current_files' in st.session_state:
            st.subheader("Files and Folders")
            
            files = st.session_state.current_files
            if files:
                # Create DataFrame for display
                df = pd.DataFrame(files)
                
                # Display with interactive table
                selected_file = st.dataframe(
                    df[['name', 'type', 'size', 'modified']],
                    use_container_width=True,
                    selection_mode="single-row"
                )
                
                # File actions
                if selected_file:
                    st.subheader("File Actions")
                    file_info = selected_file.iloc[0] if not selected_file.empty else None
                    
                    if file_info is not None:
                        file_path = f"{current_dir}/{file_info['name']}"
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            if st.button("👁️ View") and file_info['type'] == 'file':
                                result = self.file_manager.read_file(file_path)
                                if result['success']:
                                    st.text_area("File Content", result['content'], height=200)
                                else:
                                    st.error(result['message'])
                        
                        with col2:
                            if st.button("🗑️ Delete"):
                                result = self.file_manager.delete_file(file_path)
                                if result['success']:
                                    st.success(f"Deleted: {file_info['name']}")
                                    st.rerun()
                                else:
                                    st.error(result['message'])
                        
                        with col3:
                            if st.button("📋 Copy"):
                                st.session_state.clipboard_file = file_path
                                st.success(f"Copied to clipboard: {file_info['name']}")
                        
                        with col4:
                            if st.button("✏️ Rename") and file_info['type'] == 'file':
                                new_name = st.text_input("New Name", value=file_info['name'])
                                if st.button("Confirm Rename"):
                                    result = self.file_manager.rename_file(file_path, new_name)
                                    if result['success']:
                                        st.success(f"Renamed to: {new_name}")
                                        st.rerun()
                                    else:
                                        st.error(result['message'])
            else:
                st.info("No files found in current directory")
    
    def render_process_manager(self):
        """Render process manager interface"""
        st.title("⚙️ Process Manager")
        
        # Process controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Processes"):
                with st.spinner("Getting processes..."):
                    processes = self.process_manager.get_running_processes()
                    st.session_state.processes = processes
                    st.rerun()
        
        with col2:
            process_name = st.text_input("Process Name to Start")
            if st.button("▶️ Start Process") and process_name:
                result = self.process_manager.start_process(process_name)
                if result['success']:
                    st.success(f"Started: {process_name} (PID: {result['pid']})")
                else:
                    st.error(result['message'])
        
        with col3:
            if st.button("📊 System Summary"):
                with st.spinner("Getting system summary..."):
                    summary = self.process_manager.get_system_processes_summary()
                    st.session_state.system_summary = summary
        
        # Process list
        if 'processes' in st.session_state:
            st.subheader("Running Processes")
            
            processes = st.session_state.processes
            
            if processes:
                # Create DataFrame
                process_data = []
                for proc in processes:
                    process_data.append({
                        'PID': proc.pid,
                        'Name': proc.name,
                        'Status': proc.status,
                        'CPU %': f"{proc.cpu_percent:.1f}",
                        'Memory %': f"{proc.memory_percent:.1f}",
                        'Created': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(proc.create_time))
                    })
                
                df = pd.DataFrame(process_data)
                
                # Display with filtering
                filter_name = st.text_input("Filter by name")
                if filter_name:
                    df = df[df['Name'].str.contains(filter_name, case=False)]
                
                st.dataframe(df, use_container_width=True)
                
                # Process actions
                st.subheader("Process Actions")
                selected_pid = st.selectbox("Select Process by PID", [p.pid for p in processes])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("⏹️ Stop Process"):
                        result = self.process_manager.stop_process(selected_pid)
                        if result['success']:
                            st.success(f"Stopped process: {selected_pid}")
                        else:
                            st.error(result['message'])
                
                with col2:
                    if st.button("🔄 Restart Process"):
                        result = self.process_manager.restart_process(selected_pid)
                        if result['success']:
                            st.success(f"Restarted process: {selected_pid}")
                        else:
                            st.error(result['message'])
                
                with col3:
                    if st.button("📊 Monitor Process"):
                        with st.spinner("Monitoring process..."):
                            monitoring = self.process_manager.monitor_process(selected_pid, duration=5)
                            if monitoring['success']:
                                data = monitoring['data']
                                
                                # Create charts
                                fig = make_subplots(
                                    rows=2, cols=1,
                                    subplot_titles=('CPU Usage Over Time', 'Memory Usage Over Time')
                                )
                                
                                timestamps = [s['timestamp'] for s in data['samples']]
                                cpu_values = [s.get('cpu_percent', 0) for s in data['samples']]
                                memory_values = [s.get('memory_percent', 0) for s in data['samples']]
                                
                                fig.add_trace(
                                    go.Scatter(x=timestamps, y=cpu_values, name='CPU %'),
                                    row=1, col=1
                                )
                                
                                fig.add_trace(
                                    go.Scatter(x=timestamps, y=memory_values, name='Memory %'),
                                    row=2, col=1
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error(monitoring['message'])
        
        # System summary
        if 'system_summary' in st.session_state:
            st.subheader("System Summary")
            summary = st.session_state.system_summary
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Processes", summary['total_processes'])
                st.metric("Running Processes", summary['running_processes'])
                st.metric("Total CPU Usage", f"{summary['total_cpu_usage']:.1f}%")
            
            with col2:
                st.metric("Total Memory Usage", f"{summary['total_memory_usage']:.1f}%")
                st.metric("Sleeping Processes", summary['sleeping_processes'])
            
            # Top processes
            st.subheader("Top CPU Processes")
            top_cpu_df = pd.DataFrame(summary['top_cpu_processes'])
            st.dataframe(top_cpu_df, use_container_width=True)
            
            st.subheader("Top Memory Processes")
            top_mem_df = pd.DataFrame(summary['top_memory_processes'])
            st.dataframe(top_mem_df, use_container_width=True)
    
    def render_system_monitor(self):
        """Render system monitoring interface"""
        st.title("📊 System Monitor")
        
        # System information
        if 'system_info' in st.session_state:
            info = st.session_state.system_info
            
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("CPU Cores", info['cpu']['count'])
                st.metric("CPU Usage", f"{info['cpu']['usage_percent']:.1f}%")
            
            with col2:
                st.metric("Total Memory", f"{info['memory']['total_gb']:.1f} GB")
                st.metric("Memory Usage", f"{info['memory']['percent']:.1f}%")
            
            with col3:
                st.metric("Available Memory", f"{info['memory']['available_gb']:.1f} GB")
                st.metric("Used Memory", f"{info['memory']['used_gb']:.1f} GB")
            
            with col4:
                st.metric("System", info['system'])
                st.metric("Python Version", info['python_version'])
            
            # Disk usage
            st.subheader("Disk Usage")
            
            disk_data = []
            for device, usage in info['disk'].items():
                disk_data.append({
                    'Device': device,
                    'Mount Point': usage['mountpoint'],
                    'Total (GB)': usage['total_gb'],
                    'Used (GB)': usage['used_gb'],
                    'Free (GB)': usage['free_gb'],
                    'Usage %': usage['percent']
                })
            
            if disk_data:
                df = pd.DataFrame(disk_data)
                st.dataframe(df, use_container_width=True)
                
                # Disk usage chart
                fig = px.pie(
                    df, 
                    values='Used (GB)', 
                    names='Device', 
                    title='Disk Usage Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Network information
            st.subheader("Network Information")
            
            network_info = info['network']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Established Connections", network_info['connections']['established'])
                st.metric("Listening Ports", network_info['connections']['listening'])
            
            with col2:
                st.metric("Time Wait Connections", network_info['connections']['time_wait'])
                st.metric("Bytes Sent", f"{network_info['io_stats']['bytes_sent']:,}")
                st.metric("Bytes Received", f"{network_info['io_stats']['bytes_recv']:,}")
            
            # Network interfaces
            if network_info['interfaces']:
                st.subheader("Network Interfaces")
                
                interface_data = []
                for name, interface in network_info['interfaces'].items():
                    for addr in interface['addresses']:
                        interface_data.append({
                            'Interface': name,
                            'Family': addr['family'],
                            'Address': addr['address'],
                            'Netmask': addr['netmask']
                        })
                
                if interface_data:
                    df = pd.DataFrame(interface_data)
                    st.dataframe(df, use_container_width=True)
        
        # System health check
        if st.button("🏥 Health Check"):
            with st.spinner("Performing health check..."):
                health = self.system_controller.check_system_health()
                
                st.subheader("System Health Status")
                
                # Overall status
                status_color = {
                    'healthy': 'green',
                    'warning': 'orange',
                    'critical': 'red'
                }
                
                st.markdown(f"**Overall Status**: :{status_color[health['overall']]}[{health['overall'].upper()}]")
                
                # Health checks
                for check_name, check_result in health['checks'].items():
                    if check_result['status'] == 'ok':
                        st.success(f"✅ {check_name.title()}: OK")
                    elif check_result['status'] == 'warning':
                        st.warning(f"⚠️ {check_name.title()}: Warning")
                    else:
                        st.error(f"❌ {check_name.title()}: Critical")
                
                # Warnings and errors
                if health['warnings']:
                    st.subheader("Warnings")
                    for warning in health['warnings']:
                        st.warning(f"⚠️ {warning}")
                
                if health['errors']:
                    st.subheader("Errors")
                    for error in health['errors']:
                        st.error(f"❌ {error}")
    
    def render_settings(self):
        """Render settings page"""
        st.title("⚙️ Settings")
        
        # Model settings
        st.subheader("🤖 Model Settings")
        
        if self.ai_model:
            model_info = self.ai_model.get_model_info()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Model Status", "Loaded" if model_info['is_initialized'] else "Not Loaded")
                st.metric("Device", model_info['device'])
                st.metric("Session ID", model_info['session_id'][:8] + "...")
            
            with col2:
                st.metric("Total Parameters", f"{model_info['parameters']['total']:,}")
                st.metric("Conversational Net", f"{model_info['parameters']['conversational_net']:,}")
                st.metric("Computer Module", f"{model_info['parameters']['computer_module']:,}")
        
        # Voice settings
        st.subheader("🎤 Voice Settings")
        
        if st.session_state.voice_enabled and self.tts_engine:
            current_settings = self.tts_engine.get_current_settings()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Current Voice", current_settings.get('current_voice', {}).get('name', 'Default'))
                st.metric("Speech Rate", current_settings['rate'])
                st.metric("Volume", f"{current_settings['volume']:.2f}")
            
            with col2:
                st.metric("Is Speaking", "Yes" if current_settings['is_speaking'] else "No")
                st.metric("Queue Size", current_settings['queue_size'])
        
        # System settings
        st.subheader("⚙️ System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Restart AI Model"):
                st.session_state.ai_model = None
                self.initialize_ai_model()
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear Conversation History"):
                st.session_state.conversation_history = []
                st.success("Conversation history cleared")
        
        # Export/Import settings
        st.subheader("💾 Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 Export Conversation"):
                if st.session_state.conversation_history:
                    export_data = {
                        'conversation_history': st.session_state.conversation_history,
                        'export_time': time.time()
                    }
                    st.download_button(
                        "Download JSON",
                        data=json.dumps(export_data, indent=2),
                        file_name="conversation_history.json",
                        mime="application/json"
                    )
                else:
                    st.warning("No conversation history to export")
        
        with col2:
            uploaded_file = st.file_uploader("📥 Import Conversation", type=['json'])
            if uploaded_file:
                try:
                    import_data = json.load(uploaded_file)
                    st.session_state.conversation_history = import_data.get('conversation_history', [])
                    st.success("Conversation history imported successfully")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error importing conversation: {str(e)}")
    
    def run(self):
        """Main application runner"""
        # Set page configuration
        st.set_page_config(
            page_title="Conversational AI Assistant",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .stChatMessage {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .stChatMessage[data-testid="chat-message-container-user"] {
            background-color: #e3f2fd;
        }
        .stChatMessage[data-testid="chat-message-container-assistant"] {
            background-color: #f3e5f5;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Render sidebar
        self.render_sidebar()
        
        # Main navigation
        page = st.selectbox(
            "Select Page",
            ["💬 Chat", "📁 File Manager", "⚙️ Process Manager", "📊 System Monitor", "⚙️ Settings"],
            key="main_navigation"
        )
        
        # Initialize AI model if needed
        if page != "⚙️ Settings":
            self.initialize_ai_model()
        
        # Render selected page
        if page == "💬 Chat":
            self.render_chat_interface()
        elif page == "📁 File Manager":
            self.render_file_manager()
        elif page == "⚙️ Process Manager":
            self.render_process_manager()
        elif page == "📊 System Monitor":
            self.render_system_monitor()
        elif page == "⚙️ Settings":
            self.render_settings()

def main():
    """Main function to run the web interface"""
    app = WebInterface()
    app.run()

if __name__ == "__main__":
    main()
