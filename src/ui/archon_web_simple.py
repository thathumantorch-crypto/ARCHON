"""
Simple ARCHON Web Interface - Working version without Unicode and KeyError issues
"""

import streamlit as st
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.archon_ai import ArchonAI

class SimpleArchonWeb:
    """Simple working web interface for ARCHON"""
    
    def __init__(self):
        self.archon_ai = None
        self._initialize_archon()
        self._setup_session_state()
    
    def _initialize_archon(self):
        """Initialize ARCHON AI system"""
        try:
            self.archon_ai = ArchonAI()
            st.success("ARCHON AI System Initialized Successfully!")
        except Exception as e:
            st.error(f"Failed to initialize ARCHON: {e}")
    
    def _setup_session_state(self):
        """Setup Streamlit session state"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'tts_enabled' not in st.session_state:
            st.session_state.tts_enabled = True
        if 'voice_rate' not in st.session_state:
            st.session_state.voice_rate = 200
        if 'voice_volume' not in st.session_state:
            st.session_state.voice_volume = 0.9
    
    def run(self):
        """Run the simple ARCHON web interface"""
        st.set_page_config(
            page_title="ARCHON - Simple Web Interface",
            page_icon="A",
            layout="wide"
        )
        
        # Header
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;'>
            <h1>ARCHON</h1>
            <h3>Autonomous Recursive Cognitive Heuristic Operations Network</h3>
            <p>Self-Aware AI with Safe Self-Modification & Programming Expertise</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        with st.sidebar:
            st.header("ARCHON Control Panel")
            
            if self.archon_ai:
                status = self.archon_ai.get_archon_status()
                
                st.subheader("System Status")
                st.metric("Identity", status['archon_core']['identity'])
                st.metric("Uptime", status['archon_core']['uptime'])
                st.metric("Capabilities", len(status['capabilities']))
                
                st.subheader("Voice Controls")
                tts_enabled = st.checkbox("Auto TTS", value=st.session_state.tts_enabled, help="Automatically speak responses")
                st.write(f"TTS Status: {'ENABLED' if st.session_state.tts_enabled else 'DISABLED'}")
                
                # Show TTS engine status
                if self.archon_ai.enhanced_tts:
                    tts_status = self.archon_ai.enhanced_tts.get_status()
                    if tts_status['initialized']:
                        st.success("Enhanced TTS: Operational")
                        st.write(f"Current Voice: {tts_status['current_voice']['name']}")
                        st.write(f"Available Voices: {len(tts_status['available_voices'])}")
                    else:
                        st.error("Enhanced TTS: Not initialized")
                elif self.archon_ai.tts_engine:
                    st.info("Standard TTS: Available")
                else:
                    st.error("TTS: Not available")
                
                voice_rate = st.slider("Speech Rate", 100, 300, st.session_state.voice_rate, help="Adjust speech speed")
                voice_volume = st.slider("Volume", 0.1, 1.0, st.session_state.voice_volume, help="Adjust speech volume")
                
                # Update TTS settings if changed
                if self.archon_ai.tts_engine:
                    try:
                        self.archon_ai.tts_engine.set_rate(st.session_state.voice_rate)
                        self.archon_ai.tts_engine.set_volume(st.session_state.voice_volume)
                    except:
                        pass
                
                st.subheader("Learning Metrics")
                st.metric("Conversations", status.get('conversation_history_length', 0))
                st.metric("Learning Events", status['archon_core']['performance_metrics']['learning_events'])
                
                if st.button("Introduce ARCHON"):
                    intro = self.archon_ai.archon_core.consciousness.introduce_self()
                    st.session_state.messages.append({
                        'type': 'archon',
                        'content': intro,
                        'timestamp': datetime.now()
                    })
                    
                    # Auto-speak introduction if TTS is enabled
                    if st.session_state.tts_enabled:
                        try:
                            self.archon_ai.speak_response(intro)
                        except:
                            pass
        
        # Main content
        st.header("Conversation with ARCHON")
        
        # Display conversation history
        for message in st.session_state.messages:
            if message['type'] == 'user':
                st.markdown(f"""
                <div style='background: #e3f2fd; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid #2196f3;'>
                    <strong>You:</strong> {message['content']}
                    <br><small>{message['timestamp'].strftime('%H:%M:%S')}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background: #f3e5f5; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid #9c27b0;'>
                    <strong>ARCHON:</strong> {message['content']}
                    <br><small>{message['timestamp'].strftime('%H:%M:%S')}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Add speak button for each ARCHON message
                col1, col2 = st.columns([4, 1])
                with col2:
                    if st.button(f"🔊 Speak", key=f"speak_{message['timestamp']}"):
                        try:
                            speech_result = self.archon_ai.speak_response(message['content'])
                            if speech_result['success']:
                                st.success("Speaking...")
                            else:
                                st.warning(f"Speech issue: {speech_result['message']}")
                        except Exception as e:
                            st.warning(f"TTS Error: {e}")
        
        # Input area
        st.subheader("Send Message to ARCHON")
        
        user_input = st.text_area(
            "Type your message:",
            placeholder="Ask ARCHON anything - programming help, system tasks, or just conversation...",
            height=100
        )
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            send_button = st.button("Send Message", type="primary")
        
        with col2:
            st.write("")
        
        # Handle message sending
        if send_button and user_input and self.archon_ai:
            with st.spinner("ARCHON is thinking..."):
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
                
                # TTS - Speak the response if enabled
                if st.session_state.tts_enabled:
                    print("Auto TTS is enabled - attempting to speak...")
                    try:
                        # Use enhanced TTS if available
                        speech_result = self.archon_ai.speak_response(response['archon_response'])
                        if speech_result['success']:
                            st.success("🔊 ARCHON is speaking...")
                            print(f"TTS Success: {speech_result['message']}")
                            
                            # Show TTS details
                            if 'voice' in speech_result:
                                voice_name = speech_result['voice'].get('name', 'Unknown')
                                st.info(f"Voice: {voice_name}")
                        else:
                            st.warning(f"Speech issue: {speech_result['message']}")
                            print(f"TTS Error: {speech_result['message']}")
                    except Exception as e:
                        st.warning(f"TTS Error: {e}")
                        print(f"TTS Exception: {e}")
                else:
                    print("Auto TTS is disabled")
                
                # Show additional info
                if response['learning_occurred']:
                    st.info("Learning occurred during this interaction")
                
                if response['self_modification_occurred']:
                    st.warning("Self-modification analysis performed")
                
                if response['programming_assistance']:
                    st.success("Programming assistance provided")
                
                st.rerun()
        
        # Programming assistance section
        st.header("Programming Assistance")
        
        code_input = st.text_area(
            "Enter code for analysis:",
            placeholder="Paste your Python, JavaScript, or other code here...",
            height=150
        )
        
        if st.button("Analyze Code") and code_input and self.archon_ai:
            with st.spinner("Analyzing code..."):
                analysis_message = f"Analyze this code: ```python\n{code_input}\n```"
                response = self.archon_ai.process_message(analysis_message)
                
                st.markdown("### ARCHON's Analysis")
                st.write(response['archon_response'])
        
        # System information
        st.header("System Information")
        
        if st.button("Get System Info") and self.archon_ai:
            try:
                from computer.system_controller import SystemController
                sc = SystemController()
                info = sc.get_system_info()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("System", f"{info['system']} {info['version']}")
                    st.metric("CPU Cores", info['cpu']['count'])
                    st.metric("Architecture", info['machine'])
                
                with col2:
                    st.metric("Total Memory", f"{info['memory']['total_gb']:.1f} GB")
                    st.metric("Available Memory", f"{info['memory']['available_gb']:.1f} GB")
                    st.metric("Memory Usage", f"{info['memory']['percent']:.1f}%")
                
            except Exception as e:
                st.error(f"Error getting system info: {e}")

def main():
    """Main function"""
    interface = SimpleArchonWeb()
    interface.run()

if __name__ == "__main__":
    main()
