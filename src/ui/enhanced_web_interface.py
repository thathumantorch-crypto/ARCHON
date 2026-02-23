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
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.archon_ai import ArchonAI
from computer.file_manager import FileManager
from computer.process_manager import ProcessManager
from computer.system_controller import SystemController
from voice.tts import TextToSpeechEngine
try:
    from voice.stt import SpeechToTextEngine
except ImportError:
    print("WARNING: Using alternative STT engine (no pyaudio)")
    from voice.stt_no_pyaudio import SpeechToTextEngineNoPyAudio as SpeechToTextEngine

class EnhancedWebInterface:
    """
    Enhanced web interface for ARCHON AI system
    """
    
    def __init__(self):
        self.archon_ai = None
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
        if 'learning_status' not in st.session_state:
            st.session_state.learning_status = {}
        if 'model_knowledge_status' not in st.session_state:
            st.session_state.model_knowledge_status = {}
        if 'custom_learning_urls' not in st.session_state:
            st.session_state.custom_learning_urls = []
    
    def initialize_archon_ai(self):
        """Initialize ARCHON AI"""
        if 'archon_ai' not in st.session_state:
            with st.spinner("Initializing ARCHON AI..."):
                try:
                    self.archon_ai = ArchonAI()
                    st.session_state.archon_ai = self.archon_ai
                    
                    # Initialize voice engines if enabled
                    if st.session_state.voice_enabled:
                        self.tts_engine = TextToSpeechEngine()
                        self.stt_engine = SpeechToTextEngine()
                        st.session_state.tts_engine = self.tts_engine
                        st.session_state.stt_engine = self.stt_engine
                    
                    # Get learning and model knowledge status
                    st.session_state.learning_status = self.archon_ai.get_learning_status()
                    st.session_state.model_knowledge_status = self.archon_ai.get_model_knowledge_status()
                    
                    st.success("ARCHON AI initialized successfully!")
                except Exception as e:
                    st.error(f"Error initializing ARCHON AI: {str(e)}")
                    return False
        else:
            self.archon_ai = st.session_state.archon_ai
            if st.session_state.voice_enabled:
                self.tts_engine = st.session_state.get('tts_engine')
                self.stt_engine = st.session_state.get('stt_engine')
        
        return True
    
    def render_chat_interface(self):
        """Render the main chat interface"""
        st.title("* ARCHON AI - Enhanced Conversational Assistant")
        
        # Display ARCHON status
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="AI Learning Status",
                value="OK" if st.session_state.learning_status.get('available', False) else "FAIL",
                help="Status of AI learning system",
                delta="Active" if st.session_state.learning_status.get('available', False) else "Inactive"
            )
        with col2:
            st.metric(
                label="Model Knowledge Status", 
                value="OK" if st.session_state.model_knowledge_status.get('available', False) else "FAIL",
                help="Status of model knowledge integration",
                delta="Active" if st.session_state.model_knowledge_status.get('available', False) else "Inactive"
            )
        with col3:
            st.metric(
                label="Voice System Status",
                value="ON" if st.session_state.voice_enabled else "OFF",
                help="Voice synthesis and recognition status",
                delta="Enabled" if st.session_state.voice_enabled else "Disabled"
            )
        
        # Chat history
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.conversation_history:
                if message['role'] == 'user':
                    st.chat_message("user").write(message['content'])
                else:
                    st.chat_message("assistant").write(message['content'])
        
        # Input area
        user_input = st.chat_input("Type your message here...", key="chat_input")
        
        if user_input and self.archon_ai:
            # Add user message to history
            st.session_state.conversation_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': time.time()
            })
            
            # Get ARCHON response
            with st.spinner("Thinking..."):
                response = self.archon_ai.process_message(user_input)
            
            # Add assistant response to history
            reply = response.get('archon_response', '') or ''
            if not reply.strip():
                reply = "I'm sorry, I wasn't able to generate a response. Could you rephrase?"
            st.session_state.conversation_history.append({
                'role': 'assistant',
                'content': reply,
                'timestamp': time.time(),
            })
            
            # Speak response if voice is enabled
            if st.session_state.voice_enabled and self.tts_engine:
                try:
                    response_text = response.get('archon_response', 'I apologize, but I encountered an error processing your message.')
                    self.tts_engine.speak(response_text)
                except Exception as e:
                    st.warning(f"Voice synthesis error: {e}")
            
            # Rerun to display the new messages
            st.rerun()
        
        # Voice input (if enabled)
        if st.session_state.voice_enabled and self.stt_engine:
            if st.button("Voice Input"):
                with st.spinner("Listening..."):
                    try:
                        text = self.stt_engine.listen()
                        if text:
                            st.session_state.conversation_history.append({
                                'role': 'user',
                                'content': text,
                                'timestamp': time.time(),
                            })
                            response = self.archon_ai.process_message(text)
                            reply = response.get('archon_response', '') or ''
                            if not reply.strip():
                                reply = "I'm sorry, I wasn't able to generate a response."
                            st.session_state.conversation_history.append({
                                'role': 'assistant',
                                'content': reply,
                                'timestamp': time.time(),
                            })
                            st.rerun()
                    except Exception as e:
                        st.error(f"Voice input error: {e}")
    
    def render_file_manager(self):
        """Render file manager interface"""
        st.title("* File Manager")
        
        # Current directory
        st.text_input(
            label="Current Directory",
            value=st.session_state.current_directory,
            disabled=True,
            help="Current working directory for file operations",
            key="current_directory_input"
        )
        
        # List files
        if st.button("Refresh Files"):
            files = self.file_manager.list_directory(st.session_state.current_directory)
            st.session_state.current_files = files
        
        if 'current_files' in st.session_state:
            files = st.session_state.current_files
            if files:
                df = pd.DataFrame(files)
                st.dataframe(df)
            else:
                st.info("No files found or unable to list files")
    
    def render_process_manager(self):
        """Render process manager interface"""
        st.title("* Process Manager")
        
        if st.button("Refresh Processes"):
            processes = self.process_manager.get_running_processes()
            st.session_state.current_processes = processes
        
        if 'current_processes' in st.session_state:
            processes = st.session_state.current_processes
            if processes:
                # Convert ProcessInfo objects to dict for display
                process_data = []
                for proc in processes:
                    process_data.append({
                        'PID': proc.pid,
                        'Name': proc.name,
                        'Status': proc.status,
                        'CPU %': f"{proc.cpu_percent:.1f}",
                        'Memory %': f"{proc.memory_percent:.1f}",
                        'Memory (MB)': f"{proc.memory_info.get('rss', 0) / 1024 / 1024:.1f}",
                        'Created': f"{datetime.fromtimestamp(proc.create_time).strftime('%Y-%m-%d %H:%M:%S')}",
                        'Executable': proc.exe or '',
                        'Command Line': ' '.join(proc.cmdline) if proc.cmdline else ''
                    })
                df = pd.DataFrame(process_data)
                st.dataframe(df)
            else:
                st.info("No processes found or unable to list processes")
    
    def render_system_monitor(self):
        """Render system monitor interface"""
        st.title("* System Monitor")
        
        # Get system info
        cpu_usage = self.system_controller.get_cpu_usage()
        memory_usage = self.system_controller.get_memory_usage()
        disk_usage = self.system_controller.get_disk_usage()
        
        # Calculate average disk usage from all drives
        avg_disk_usage = 0.0
        if disk_usage:
            total_percent = sum(info.get('percent', 0) for info in disk_usage.values())
            avg_disk_usage = total_percent / len(disk_usage)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="CPU Usage",
                value=f"{cpu_usage:.1f}%",
                help="Current CPU usage percentage",
                delta="Normal" if cpu_usage < 70 else ("High" if cpu_usage < 90 else "Critical")
            )
        with col2:
            st.metric(
                label="Memory Usage",
                value=f"{memory_usage:.1f}%",
                help="Current memory usage percentage",
                delta="Normal" if memory_usage < 70 else ("High" if memory_usage < 90 else "Critical")
            )
        with col3:
            st.metric(
                label="Disk Usage",
                value=f"{avg_disk_usage:.1f}%",
                help="Average disk usage across all drives",
                delta="Normal" if avg_disk_usage < 70 else ("High" if avg_disk_usage < 90 else "Critical")
            )
        
        # Disk usage details
        if disk_usage:
            st.subheader("* Disk Usage Details")
            for device, info in disk_usage.items():
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.text(device)
                with col2:
                    st.text(f"Used: {info.get('used', 0) / (1024**3):.1f} GB")
                with col3:
                    st.text(f"Free: {info.get('free', 0) / (1024**3):.1f} GB")
                with col4:
                    st.text(f"Usage: {info.get('percent', 0):.1f}%")
                st.progress(info.get('percent', 0) / 100)
        
        # System info
        system_info = self.system_controller.get_system_info()
        st.subheader("* System Information")
        st.json(system_info)
    
    def render_settings(self):
        """Render settings and integrations"""
        st.title("* Settings & Integrations")
        
        # Voice settings
        st.subheader("* Voice Settings")
        voice_enabled = st.checkbox(
            label="Enable Voice",
            value=st.session_state.voice_enabled,
            help="Enable voice synthesis and recognition features",
            key="voice_enabled_checkbox"
        )
        if voice_enabled != st.session_state.voice_enabled:
            st.session_state.voice_enabled = voice_enabled
            if voice_enabled:
                self.tts_engine = TextToSpeechEngine()
                self.stt_engine = SpeechToTextEngine()
                st.session_state.tts_engine = self.tts_engine
                st.session_state.stt_engine = self.stt_engine
            else:
                self.tts_engine = None
                self.stt_engine = None
                st.session_state.tts_engine = None
                st.session_state.stt_engine = None
        
        # Learning settings
        st.subheader("* AI Learning Settings")
        if st.button("Update Model Knowledge"):
            if self.archon_ai:
                result = self.archon_ai.update_model_knowledge()
                if result['success']:
                    st.success(f"Updated: {result['libraries_processed']} libraries")
                else:
                    st.error(f"Failed: {result['message']}")
        
        # Web learning
        st.subheader("* Web Learning Settings")
        custom_url = st.text_input(
            label="Add YouTube or other safelisted URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste a YouTube (or other safelisted) link and click 'Add URL' so ARCHON learns from it.",
            key="custom_learning_url_input"
        )
        col_add, col_clear = st.columns([1, 1])
        url_checker_available = bool(self.archon_ai and hasattr(self.archon_ai, 'is_url_safelisted'))
        with col_add:
            if st.button("Add URL", key="add_custom_learning_url"):
                if custom_url and custom_url.strip():
                    trimmed = custom_url.strip()
                    if url_checker_available and not self.archon_ai.is_url_safelisted(trimmed):
                        st.warning("That URL isn't in the safelist ARCHON is allowed to crawl.")
                    elif trimmed not in st.session_state.custom_learning_urls:
                        st.session_state.custom_learning_urls.append(trimmed)
                        st.success("URL added for the next learning session.")
                    else:
                        st.info("URL already queued.")
                else:
                    st.warning("Please enter a valid URL before adding.")
        with col_clear:
            if st.button("Clear URLs", key="clear_custom_learning_urls"):
                st.session_state.custom_learning_urls = []
                st.success("Cleared queued URLs.")

        if st.session_state.custom_learning_urls:
            st.markdown("**Queued Learning URLs:**")
            for idx, url in enumerate(st.session_state.custom_learning_urls, start=1):
                st.markdown(f"{idx}. [{url}]({url})")

        if st.button("Start Web Learning Session"):
            if self.archon_ai:
                with st.spinner("Starting web learning..."):
                    result = self.archon_ai.start_web_learning_session(
                        max_pages=3,
                        max_examples=5,
                        custom_urls=st.session_state.custom_learning_urls,
                    )
                    if result['success']:
                        st.success(
                            f"Learned: {result['patterns_learned']} patterns, {result['templates_learned']} templates."
                            f" Custom URLs processed: {result.get('custom_urls_processed', 0)}."
                        )
                        feedback = result.get('custom_url_feedback') or {}
                        if feedback.get('disallowed'):
                            st.warning(
                                "Skipped URLs (not safelisted):\n" + "\n".join(feedback['disallowed'])
                            )
                        if feedback.get('allowed') and not result.get('custom_urls_processed'):
                            st.info("Queued URLs were approved but yielded no learnable content this run.")
                        st.session_state.custom_learning_urls = []
                        if result.get('knowledgebase_ingest'):
                            st.caption(
                                f"Knowledgebase ingest: {result['knowledgebase_ingest'].get('items_ingested', 0)} items persisted."
                            )
                    else:
                        st.error(f"Failed: {result['message']}")

        st.markdown("---")
        st.subheader("* AI Creation Research")
        if st.button("Search YouTube for AI Creation Insights", help="Automatically discover ~100 AI-creation/JARVIS videos, learn from their transcripts, and queue non-core improvements."):
            if not self.archon_ai:
                st.error("ARCHON AI is unavailable right now.")
            else:
                with st.spinner("Scanning YouTube transcripts for AI creation insights (~100 videos)..."):
                    result = self.archon_ai.run_ai_creation_video_learning()
                if result.get('success'):
                    videos = result.get('videos_processed', 0)
                    improvements = result.get('improvement_plans', [])
                    st.success(
                        f"Processed {videos} videos. Logged {len(improvements)} improvement ideas and updated learning systems."
                    )
                    learning_session = result.get('learning_session') or {}
                    st.caption(
                        f"Learning session #{learning_session.get('session_id', 'N/A')} - patterns learned: {learning_session.get('patterns_learned', 0)}, templates learned: {learning_session.get('templates_learned', 0)}."
                    )
                    if improvements:
                        with st.expander("Queued improvement ideas"):
                            for idea in improvements[:20]:
                                st.write(f"- [{idea.get('target','unknown')}] {idea.get('summary')}\n  Source: {idea.get('source_url')}")
                    kb_result = result.get('knowledgebase_ingest')
                    if kb_result:
                        st.caption(
                            f"Knowledgebase ingest: {kb_result.get('items_ingested', 0)} of {kb_result.get('items_attempted', 0)} entries persisted."
                        )
                else:
                    st.error(result.get('message', 'Unable to run AI creation learning.'))

        # Moltbook integration
        st.subheader("* Moltbook Integration")
        if self.archon_ai:
            status_placeholder = st.empty()
            actions_col, heartbeat_col = st.columns([1, 1])

            def refresh_status():
                status = self.archon_ai.check_moltbook_status()
                if status.get('success'):
                    state = status.get('state', {})
                    profile = status.get('profile')
                    claim_status = status.get('status', {})
                    st.markdown(
                        "**Claim Status:** " + claim_status.get('status', 'unknown').replace('_', ' ').title()
                    )
                    st.markdown(f"**Heartbeat Due:** {state.get('heartbeat_due')}")
                    st.markdown(f"**Last Check:** {state.get('last_check')}")
                    if profile:
                        st.markdown("**Moltbook Profile:**")
                        st.json(profile)
                else:
                    st.error(status.get('message', 'Unable to fetch status'))

            with status_placeholder.container():
                refresh_status()

            with actions_col:
                if st.button("Register/Fetch Credentials", key="moltbook_register"):
                    with st.spinner("Registering with Moltbook..."):
                        result = self.archon_ai.register_with_moltbook()
                        if result.get('success'):
                            st.success("Registered or already registered.")
                            if result.get('claim_url'):
                                st.info(
                                    f"Share this claim URL with your human: {result['claim_url']}\n"
                                    f"Verification code: {result.get('verification_code')}"
                                )
                        else:
                            st.error(result.get('message', 'Registration failed'))

            with heartbeat_col:
                if st.button("Run Moltbook Heartbeat", key="moltbook_heartbeat"):
                    with st.spinner("Running heartbeat..."):
                        hb = self.archon_ai.perform_moltbook_heartbeat(force=True)
                        if hb.get('success'):
                            st.success(hb.get('message', 'Heartbeat complete'))
                        else:
                            st.error(hb.get('message', 'Heartbeat failed'))

                if st.button("Manual Moltbook Post", key="moltbook_manual_post"):
                    with st.spinner("Drafting/Postings to Moltbook..."):
                        result = self.archon_ai.consider_moltbook_post(force=True)
                        if result.get('success'):
                            post_info = result.get('post_summary') or result.get('post')
                            st.success("Post submitted to Moltbook." if result.get('posted') else "No post criteria met.")
                            if post_info:
                                st.json(post_info)
                        else:
                            st.error(result.get('message', 'Unable to post to Moltbook'))

            if st.button("Refresh Moltbook Status", key="moltbook_refresh"):
                with st.spinner("Refreshing status..."):
                    status_placeholder.empty()
                    with status_placeholder.container():
                        refresh_status()

        # Status display
        st.subheader("* System Status")
        if self.archon_ai:
            learning_status = self.archon_ai.get_learning_status()
            model_status = self.archon_ai.get_model_knowledge_status()
            
            st.write("**AI Learning System:**")
            st.json(learning_status)
            
            st.write("**Model Knowledge:**")
            st.json(model_status)

    def render_learning_overview(self):
        st.title("* Learned - ARCHON Knowledge Digest")
        if not self.archon_ai:
            st.error("ARCHON AI unavailable. Please initialize on another page.")
            return

        with st.spinner("Gathering learning records..."):
            overview = self.archon_ai.get_learning_overview(limit=400)

        total_entries = overview.get('total_entries', 0)
        st.metric("Total learning sessions", total_entries)

        cols = st.columns(2)

        with cols[0]:
            timeline = overview.get('timeline', [])
            if timeline:
                timeline_df = pd.DataFrame(timeline)
                fig = px.line(timeline_df, x='date', y='count', markers=True, title="Learning cadence")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No timeline data available yet.")

        with cols[1]:
            sources = overview.get('sources', [])
            if sources:
                source_df = pd.DataFrame(sources)
                fig = px.pie(source_df, names='name', values='count', title="Where ARCHON has learned")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No source data recorded yet.")

        st.subheader("Latest insights")
        entries = overview.get('entries', [])
        if not entries:
            st.write("ARCHON hasn't stored any learning experiences yet.")
            return

        for entry in entries[:25]:
            with st.expander(f"{entry['title']} — {entry.get('source', 'unspecified')}"):
                st.caption(entry.get('timestamp', 'recent'))
                st.write(entry.get('summary', ''))

        if len(entries) > 25:
            st.caption(f"Showing 25 of {len(entries)} entries. Use knowledge tools to export the rest.")
    
    def run(self):
        """Main run method"""
        st.set_page_config(
            page_title="ARCHON AI - Enhanced Interface",
            page_icon="*",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Sidebar navigation
        page = st.sidebar.selectbox(
            label="Select Page",
            options=["* Chat", "* File Manager", "* Process Manager", "* System Monitor", "* Learned", "* Settings"],
            key="main_navigation",
            help="Navigate to different sections of the ARCHON interface"
        )

        # Initialize ARCHON AI for all pages (settings needs it for web learning, knowledge updates, etc.)
        if not self.initialize_archon_ai():
            st.error("Unable to initialize ARCHON AI. Please check logs and retry.")
            return
        
        # Render selected page
        if page == "* Chat":
            self.render_chat_interface()
        elif page == "* File Manager":
            self.render_file_manager()
        elif page == "* Process Manager":
            self.render_process_manager()
        elif page == "* System Monitor":
            self.render_system_monitor()
        elif page == "* Learned":
            self.render_learning_overview()
        elif page == "* Settings":
            self.render_settings()

def main():
    """Main function to run the enhanced web interface"""
    app = EnhancedWebInterface()
    app.run()

if __name__ == "__main__":
    main()
