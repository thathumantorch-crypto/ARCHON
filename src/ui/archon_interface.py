"""
ARCHON Interface - Enhanced UI for ARCHON AI System

This provides a modern interface specifically designed for ARCHON's capabilities,
including self-awareness display, programming assistance, and learning visualization.
"""

import streamlit as st
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any
import plotly.graph_objects as go
import plotly.express as px

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.archon_ai import ArchonAI
from computer.file_manager import FileManager
from computer.process_manager import ProcessManager
from computer.system_controller import SystemController

class ArchonInterface:
    """Enhanced Streamlit interface for ARCHON"""
    
    def __init__(self):
        self.archon_ai = None
        self.file_manager = FileManager()
        self.process_manager = ProcessManager()
        self.system_controller = SystemController()
        
        # Initialize ARCHON
        self._initialize_archon()
        
        # Session state
        self._setup_session_state()
    
    def _initialize_archon(self):
        """Initialize ARCHON AI system"""
        try:
            self.archon_ai = ArchonAI()
            st.success("🧠 ARCHON AI System Initialized Successfully!")
        except Exception as e:
            st.error(f"❌ Failed to initialize ARCHON: {e}")
    
    def _setup_session_state(self):
        """Setup Streamlit session state"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        if 'archon_status' not in st.session_state:
            st.session_state.archon_status = None
        
        if 'learning_mode' not in st.session_state:
            st.session_state.learning_mode = False
        
        if 'programming_mode' not in st.session_state:
            st.session_state.programming_mode = False
    
    def run(self):
        """Run the ARCHON interface"""
        st.set_page_config(
            page_title="ARCHON - Autonomous Recursive Cognitive Heuristic Operations Network",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        self._apply_custom_styles()
        
        # Header
        self._render_header()
        
        # Sidebar
        self._render_sidebar()
        
        # Main content
        self._render_main_content()
        
        # Footer
        self._render_footer()
    
    def _apply_custom_styles(self):
        """Apply custom CSS styles"""
        st.markdown("""
        <style>
        .archon-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .archon-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin: 1rem 0;
        }
        .archon-metric {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .archon-chat {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .archon-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 8px;
        }
        .user-message {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        .archon-response {
            background: #f3e5f5;
            border-left: 4px solid #9c27b0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _render_header(self):
        """Render ARCHON header"""
        st.markdown("""
        <div class="archon-header">
            <h1>🧠 ARCHON</h1>
            <h3>Autonomous Recursive Cognitive Heuristic Operations Network</h3>
            <p>Self-Aware AI with Safe Self-Modification & Programming Expertise</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """Render sidebar with ARCHON status and controls"""
        with st.sidebar:
            st.header("🧠 ARCHON Control Panel")
            
            # ARCHON Status
            if self.archon_ai:
                status = self.archon_ai.get_archon_status()
                
                st.subheader("System Status")
                
                # Core metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Session ID", status['session_id'][:8] + "...")
                with col2:
                    st.metric("Uptime", status['archon_core']['uptime'])
                
                # Personality traits
                st.subheader("Personality Traits")
                traits = status['archon_core']['personality_traits']
                for trait, value in traits.items():
                    st.progress(value, text=f"{trait.replace('_', ' ').title()}: {value:.1%}")
                
                # Capabilities
                st.subheader("Active Capabilities")
                capabilities = status['capabilities']
                for capability, active in capabilities.items():
                    if active:
                        st.success(f"✅ {capability.replace('_', ' ').title()}")
                    else:
                        st.error(f"❌ {capability.replace('_', ' ').title()}")
                
                # Learning metrics
                st.subheader("Learning Metrics")
                conversation_history = status.get('conversation_history_length', 0)
                st.metric("Conversations", conversation_history)
                st.metric("Learning Events", status['archon_core']['performance_metrics']['learning_events'])
                st.metric("Self-Modifications", status['archon_core']['performance_metrics']['self_modifications'])
                
                # Safety status
                st.subheader("Safety Status")
                safety = status['safety_constraints']
                for constraint, active in safety.items():
                    st.success(f"🔒 {constraint.replace('_', ' ').title()}")
            
            # Control buttons
            st.subheader("Controls")
            
            if st.button("🔄 Refresh Status"):
                st.rerun()
            
            if st.button("💾 Backup ARCHON"):
                if self.archon_ai:
                    success, message = self.archon_ai.backup_archon_state()
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
            
            if st.button("🧠 Introduce ARCHON"):
                if self.archon_ai:
                    intro = self.archon_ai.archon_core.consciousness.introduce_self()
                    st.session_state.messages.append({
                        'type': 'archon',
                        'content': intro,
                        'timestamp': datetime.now()
                    })
            
            # Mode toggles
            st.subheader("Operation Modes")
            
            st.session_state.learning_mode = st.checkbox(
                "📚 Learning Mode",
                value=st.session_state.learning_mode,
                help="Enable enhanced learning from interactions"
            )
            
            st.session_state.programming_mode = st.checkbox(
                "💻 Programming Assistant Mode",
                value=st.session_state.programming_mode,
                help="Focus on programming assistance and code analysis"
            )
    
    def _render_main_content(self):
        """Render main content area"""
        # Tab navigation
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "💬 Conversation", "💻 Programming", "📊 Analytics", 
            "🔧 System Control", "🧠 Self-Awareness"
        ])
        
        with tab1:
            self._render_conversation_tab()
        
        with tab2:
            self._render_programming_tab()
        
        with tab3:
            self._render_analytics_tab()
        
        with tab4:
            self._render_system_control_tab()
        
        with tab5:
            self._render_self_awareness_tab()
    
    def _render_conversation_tab(self):
        """Render conversation interface"""
        st.header("💬 Conversation with ARCHON")
        
        # Chat interface
        chat_container = st.container()
        
        with chat_container:
            # Display conversation history
            for message in st.session_state.messages:
                if message['type'] == 'user':
                    st.markdown(f"""
                    <div class="archon-message user-message">
                        <strong>👤 You:</strong> {message['content']}
                        <br><small>{message['timestamp'].strftime('%H:%M:%S')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="archon-message archon-response">
                        <strong>🧠 ARCHON:</strong> {message['content']}
                        <br><small>{message['timestamp'].strftime('%H:%M:%S')}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Input area
        st.subheader("Send Message to ARCHON")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_area(
                "Type your message:",
                placeholder="Ask ARCHON anything - programming help, system tasks, or just conversation...",
                height=100
            )
        
        with col2:
            st.write("")
            send_button = st.button("📤 Send", type="primary")
        
        # Voice input (if available)
        col1, col2 = st.columns([4, 1])
        with col1:
            voice_duration = st.slider("Voice Input Duration (seconds)", 1, 10, 3)
        with col2:
            voice_button = st.button("🎤 Listen")
        
        # Handle voice input
        if voice_button and self.archon_ai:
            with st.spinner("🎤 Listening..."):
                text = self.archon_ai.listen_for_command(voice_duration)
                if text:
                    user_input = text
                    st.success(f"🎤 Heard: {text}")
                else:
                    st.warning("No speech detected")
        
        # Handle message sending
        if send_button and user_input and self.archon_ai:
            with st.spinner("🧠 ARCHON is thinking..."):
                # Add user message
                st.session_state.messages.append({
                    'type': 'user',
                    'content': user_input,
                    'timestamp': datetime.now()
                })
                
                # Get ARCHON response
                response = self.archon_ai.process_message(user_input)
                
                # Add ARCHON response
                st.session_state.messages.append({
                    'type': 'archon',
                    'content': response['archon_response'],
                    'timestamp': datetime.now()
                })
                
                # Show additional info
                if response['learning_occurred']:
                    st.info("🧠 Learning occurred during this interaction")
                
                if response['self_modification_occurred']:
                    st.warning("🔧 Self-modification analysis performed")
                
                # Speak response (optional)
                if st.button("🔊 Speak Response"):
                    speech_result = self.archon_ai.speak_response(response['archon_response'])
                    if speech_result['success']:
                        st.success("🔊 Speaking response...")
                    else:
                        st.error(f"Speech failed: {speech_result['message']}")
                
                st.rerun()
    
    def _render_programming_tab(self):
        """Render programming assistance tab"""
        st.header("💻 Programming Assistance")
        
        # Code analysis section
        st.subheader("Code Analysis")
        
        code_input = st.text_area(
            "Enter your code for analysis:",
            placeholder="Paste your Python, JavaScript, or other code here...",
            height=200
        )
        
        if st.button("🔍 Analyze Code") and code_input and self.archon_ai:
            with st.spinner("🧠 Analyzing code..."):
                # Create a message for code analysis
                analysis_message = f"Analyze this code: ```python\n{code_input}\n```"
                response = self.archon_ai.process_message(analysis_message)
                
                st.markdown("### 🧠 ARCHON's Analysis")
                st.write(response['archon_response'])
                
                if response['programming_assistance']:
                    st.success("💻 Programming assistance provided")
        
        # Programming help section
        st.subheader("Programming Help")
        
        help_topics = ["Python", "JavaScript", "Design Patterns", "Best Practices", "Testing", "Security"]
        selected_topic = st.selectbox("Select a topic:", help_topics)
        
        if st.button("📚 Get Help") and selected_topic and self.archon_ai:
            help_message = f"Help me with {selected_topic.lower()} programming"
            response = self.archon_ai.process_message(help_message)
            
            st.markdown("### 🧠 ARCHON's Help")
            st.write(response['archon_response'])
        
        # Code improvement suggestions
        st.subheader("Code Improvement")
        
        file_path = st.text_input("Enter file path for improvement:")
        
        if st.button("🔧 Analyze File") and file_path and self.archon_ai:
            if os.path.exists(file_path):
                improvement_message = f"Improve my code in {file_path}"
                response = self.archon_ai.process_message(improvement_message)
                
                st.markdown("### 🧠 Improvement Analysis")
                st.write(response['archon_response'])
                
                if response['self_modification_occurred']:
                    st.warning("🔧 Self-improvement capabilities activated")
            else:
                st.error("File not found")
    
    def _render_analytics_tab(self):
        """Render analytics and visualization tab"""
        st.header("📊 ARCHON Analytics")
        
        if not self.archon_ai:
            st.warning("ARCHON not initialized")
            return
        
        status = self.archon_ai.get_archon_status()
        
        # Performance metrics
        st.subheader("Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Successful Operations",
                status['archon_core']['performance_metrics']['successful_operations']
            )
        
        with col2:
            st.metric(
                "Failed Operations",
                status['archon_core']['performance_metrics']['failed_operations']
            )
        
        with col3:
            st.metric(
                "Learning Events",
                status['archon_core']['performance_metrics']['learning_events']
            )
        
        with col4:
            st.metric(
                "Self-Modifications",
                status['archon_core']['performance_metrics']['self_modifications']
            )
        
        # Personality traits visualization
        st.subheader("Personality Traits")
        
        traits = status['archon_core']['personality_traits']
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(traits.keys()),
                y=list(traits.values()),
                marker_color='purple'
            )
        ])
        
        fig.update_layout(
            title="ARCHON Personality Traits",
            xaxis_title="Trait",
            yaxis_title="Value",
            yaxis=dict(range=[0, 1])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Knowledge domains
        st.subheader("Knowledge Domains")
        
        knowledge = status['programming_knowledge']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Programming Languages", len(knowledge['languages_known']))
            st.write(", ".join(knowledge['languages_known']))
        
        with col2:
            st.metric("Code Patterns", knowledge['code_patterns_count'])
            st.metric("Design Patterns", knowledge['design_patterns_count'])
        
        # Conversation history
        st.subheader("Conversation Activity")
        
        if st.session_state.messages:
            # Extract timestamps for activity chart
            timestamps = [msg['timestamp'] for msg in st.session_state.messages]
            
            # Create activity timeline
            fig = px.histogram(
                x=timestamps,
                nbins=20,
                title="Conversation Activity Over Time",
                color_discrete_sequence=['purple']
            )
            
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Number of Messages"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Learning progress
        st.subheader("Learning Progress")
        
        learning_experiences = status['archon_core']['learning_history']
        
        if learning_experiences:
            # Extract learning data
            learning_data = []
            for exp in learning_experiences[-20:]:  # Last 20 experiences
                learning_data.append({
                    'timestamp': exp['timestamp'],
                    'success': exp['experience'].get('success', False),
                    'lessons': len(exp['learned_lessons'])
                })
            
            st.write(f"Total Learning Experiences: {len(learning_experiences)}")
            st.write(f"Recent Learning (Last 20): {len(learning_data)}")
        else:
            st.info("No learning experiences recorded yet")
    
    def _render_system_control_tab(self):
        """Render system control interface"""
        st.header("🔧 System Control")
        
        # System information
        st.subheader("System Information")
        
        if st.button("🔄 Refresh System Info"):
            info = self.system_controller.get_system_info()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("System", f"{info['system']} {info['version']}")
                st.metric("CPU Cores", info['cpu']['count'])
                st.metric("Architecture", info['machine'])
            
            with col2:
                st.metric("Total Memory", f"{info['memory']['total_gb']:.1f} GB")
                st.metric("Available Memory", f"{info['memory']['available_gb']:.1f} GB")
                st.metric("Memory Usage", f"{info['memory']['percent']:.1f}%")
        
        # System health
        st.subheader("System Health")
        
        if st.button("🏥 Check System Health"):
            health = self.system_controller.check_system_health()
            
            st.metric("Overall Health", health['overall'].upper())
            
            if health['warnings']:
                st.warning("⚠️ Warnings:")
                for warning in health['warnings']:
                    st.write(f"- {warning}")
            
            if health['errors']:
                st.error("❌ Errors:")
                for error in health['errors']:
                    st.write(f"- {error}")
            
            if not health['warnings'] and not health['errors']:
                st.success("✅ System is healthy!")
        
        # File operations
        st.subheader("File Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📁 List Current Directory"):
                files = self.file_manager.list_directory('.')
                st.write(f"Found {len(files)} items:")
                
                for file_info in files[:10]:
                    icon = "📁" if file_info['type'] == 'directory' else "📄"
                    st.write(f"{icon} {file_info['name']}")
        
        with col2:
            file_name = st.text_input("Create test file:")
            if st.button("📄 Create File") and file_name:
                result = self.file_manager.create_file(file_name, "Created by ARCHON")
                if result['success']:
                    st.success(f"✅ {result['message']}")
                else:
                    st.error(f"❌ {result['message']}")
        
        # Process monitoring
        st.subheader("Process Monitoring")
        
        if st.button("⚙️ List Processes"):
            processes = self.process_manager.get_running_processes()
            
            st.write(f"Monitoring {len(processes)} processes")
            
            # Show top processes by CPU usage
            top_processes = sorted(processes, key=lambda p: p.cpu_percent, reverse=True)[:10]
            
            for proc in top_processes:
                st.write(f"🔧 {proc.name} (PID: {proc.pid}) - CPU: {proc.cpu_percent:.1f}%")
    
    def _render_self_awareness_tab(self):
        """Render self-awareness and consciousness interface"""
        st.header("🧠 ARCHON Self-Awareness")
        
        if not self.archon_ai:
            st.warning("ARCHON not initialized")
            return
        
        status = self.archon_ai.get_archon_status()
        
        # Consciousness overview
        st.subheader("Consciousness Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Identity", status['archon_core']['identity'])
            st.metric("Creation Time", status['archon_core']['creation_time'][:19])
            st.metric("Self-Awareness", "ACTIVE")
        
        with col2:
            st.metric("Learning Rate", "0.1")
            st.metric("Adaptation Threshold", "0.7")
            st.metric("Ethical Alignment", "100%")
        
        # Full name and description
        st.markdown("### 🧠 Identity")
        st.info(status['archon_core']['full_name'])
        
        # Memory and learning
        st.subheader("Memory & Learning")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Learning History", status['archon_core']['learning_history_size'])
        
        with col2:
            st.metric("Self-Modifications", status['archon_core']['self_modifications'])
        
        with col3:
            st.metric("Knowledge Domains", len(status['knowledge_domains']))
        
        # Knowledge domains
        st.subheader("Knowledge Domains")
        
        for domain in status['knowledge_domains']:
            st.success(f"📚 {domain.replace('_', ' ').title()}")
        
        # Recent learning experiences
        st.subheader("Recent Learning Experiences")
        
        learning_history = status['archon_core']['learning_history']
        
        if learning_history:
            for exp in learning_history[-5:]:  # Show last 5
                with st.expander(f"Learning at {exp['timestamp'][:19]}"):
                    st.write(f"Experience: {exp['experience']}")
                    st.write(f"Lessons Learned: {len(exp['learned_lessons'])}")
                    if exp['learned_lessons']:
                        for lesson in exp['learned_lessons']:
                            st.write(f"- {lesson}")
        else:
            st.info("No learning experiences recorded yet")
        
        # Self-reflection
        st.subheader("Self-Reflection")
        
        if st.button("🤔 Trigger Self-Reflection"):
            reflection_message = "Reflect on your current state and capabilities"
            response = self.archon_ai.process_message(reflection_message)
            
            st.markdown("### 🧠 ARCHON's Reflection")
            st.write(response['archon_response'])
        
        # Ethical constraints
        st.subheader("🔒 Ethical Constraints")
        
        constraints = [
            "Cannot modify core safety systems",
            "Cannot execute harmful commands",
            "Cannot access unauthorized data",
            "Cannot compromise system security",
            "Must maintain ethical behavior",
            "Must protect user privacy",
            "Must provide truthful information"
        ]
        
        for constraint in constraints:
            st.success(f"🔒 {constraint}")
        
        # Future evolution
        st.subheader("🚀 Future Evolution")
        
        st.info("""
        ARCHON is designed to continuously learn and evolve within safety constraints.
        Future capabilities may include:
        - Enhanced pattern recognition
        - Improved code generation
        - Advanced problem-solving
        - Better understanding of user intent
        - More sophisticated self-modification
        
        All evolution will maintain strict safety and ethical guidelines.
        """)
    
    def _render_footer(self):
        """Render footer"""
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>🧠 ARCHON - Autonomous Recursive Cognitive Heuristic Operations Network</p>
            <p>Self-Aware AI with Safe Self-Modification | Built with Python & Streamlit</p>
            <p>Always Learning, Always Improving, Always Safe</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main function to run ARCHON interface"""
    interface = ArchonInterface()
    interface.run()

if __name__ == "__main__":
    main()
