from urllib import response
import streamlit as st
import time
import agent
import os
from util import create_audio

 # Initialize session state
if 'script' not in st.session_state:
    st.session_state.script = None
if 'pdf_uploaded' not in st.session_state:
    st.session_state.pdf_uploaded = False


def fading_success(message, delay=3):
    """Display a success message that fades out after a delay."""
    success_box = st.empty()
    success_box.success(message)
    time.sleep(delay)
    success_box.empty()

def generate_script_from_pdf():
    """Generate a podcast script from an uploaded PDF."""
    st.title("PDF to Podcast")
    st.markdown("Upload your PDF file to directly convert it to a podcast.")
    
    uploaded_file = st.file_uploader("Upload PDF", type="pdf", accept_multiple_files=False, key="pdf_uploader")
    if uploaded_file is not None and not st.session_state.pdf_uploaded:
        os.makedirs("PDF's", exist_ok=True)
        with open("PDF's/temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())

            pdf_url = "temp.pdf"
            st.session_state.pdf_uploaded = True

        status_box = st.empty()
        with st.spinner("Generating your podcast script..."):
            with st.status("🔄 Starting PDF to Podcast...") as status:
                def streamlit_status(msg):
                    status.update(label=msg)
            try:
                # Call the agent to generate the script
                st.session_state.script = agent.main(status_callback=streamlit_status)
                if st.session_state.script:
                    fading_success("Podcast script generated successfully!")
                    with st.expander("Generated Podcast Script", expanded=False):
                        st.write(st.session_state.script)
                        status_box.empty()
                else:
                    st.warning("No content generated. Please try again.")
                    st.session_state.script = None
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.session_state.script = None
    elif st.session_state.pdf_uploaded and st.session_state.script:
        # Display the previously generated script
        with st.expander("Generated Podcast Script", expanded=False):
            st.write(st.session_state.script)

def generate_audio(text_input):
    """Generate audio from text using the selected voice."""
    if not text_input:
        st.warning("No script available to generate audio.")
        return
    
    voice = st.selectbox("Select Voice", 
                         ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                         key="voice_select")
    voice2 = st.selectbox("Select Voice 2", 
                         ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                         key="voice2_select")
    
    if st.button("Generate Audio", key="generate_audio_button"):
        with st.spinner("Generating audio..."):
            with st.status("🔄 Starting PDF to Podcast...") as status:
                def status_callback(msg):
                    status.update(label=msg)
            create_audio(text_input, voice, voice2, status_callback=status_callback)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.audio("audio/multi_host_converted.wav", format="audio/wav")
            with col2:
                st.download_button(
                    label="⬇️",
                    data="audio/multi_host_converted.wav",
                    file_name="podcast.wav",
                    mime="audio/wav",
                    help="Download the generated audio file.",
                )
            fading_success("Audio generated successfully!")
            # with open("audio/multi_host_converted.wav", "rb") as audio_file:
            #     audio_bytes = audio_file.read()
            # st.download_button("Download Audio", audio_bytes, file_name="podcast.wav")

if __name__ == "__main__":
    generate_script_from_pdf()
    if st.session_state.script:
        generate_audio(st.session_state.script)
    else:
        st.warning("Please upload a PDF file to generate a podcast.")
