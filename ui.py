import streamlit as st
import streamlit_player as stp
import agent
import requests
import time
import json

def fading_success(message, delay=3):
    """Display a success message that fades out after a delay."""
    success_box = st.empty()
    success_box.success(message)
    time.sleep(delay)
    success_box.empty()

st.title("PDF to Podcast")
st.markdown("Upload your PDF file to directly convert it to a podcast.")
pdf_file = st.file_uploader(" ", type="pdf", accept_multiple_files=False)
if pdf_file is not None:
        # Save the uploaded PDF file to a temporary location
        with open("temp.pdf", "wb") as f:
            f.write(pdf_file.getbuffer())
        pdf_url = "temp.pdf"
        with st.spinner("Generating your podcast..."):
            try:
                script = agent.main()  # Only gets called on button click
                script = "this is the script"
                if script:
                    fading_success("Podcast generated successfully!")
                    with st.expander("Generated Podcast Script", expanded=False):
                        st.write("Podcast Script", script, height=300)
                else:
                    st.warning("No content generated. Please try again.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")    



