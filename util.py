# importing required modules
from pypdf import PdfReader
import numpy as np
import os
import streamlit as st
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
from tts import generate_audio
from scipy.io import wavfile
from scipy.io.wavfile import write as write_wav 

SAMPLE_RATE = 24000

os.makedirs("PDF's", exist_ok=True)
class PdfRead:
    def __init__(self, name, start=None, end=None, status_callback=None):
        self.name = name
        self.status_callback = status_callback or (lambda x: None)
        # creating a pdf reader object
        self.reader = PdfReader("PDF's/temp.pdf")
        # printing number of pages in pdf file
        # page_length = len(self.reader.pages)
        # print(len(self.reader.pages))

        page_length = 2 # PAGE LENGTH DEFAULTED TO 2 AS WE HAVE LIMITED RESOURCES, THIS WAS MADE FOR CLOUD RUNNING SO THAT PEOPLE CAN TEST IT OUT

        self.text = ""
        begin = 0
        finish = page_length
        
        if start != None and end != None:
            begin = start
            finish = end
        elif start != None and end == None:
            begin = start
            end = start
        self.status_callback(f"Reading from Pdf...")
        print(f"Reading from pages: {begin} to {finish}")
        for i in range(begin, finish):
                # getting a specific page from the pdf file
                page = self.reader.pages[i]

                # extracting text from page
                self.text += page.extract_text()

    def get_text(self) -> str:
        return str(self.text)


# def audio_generate(script, voice1, voice2):
#     script = script.replace("\n", " ").strip()
#     speaker_lookup = {"Alex": voice1, "Sam": voice2}
    
#     sentences = nltk.sent_tokenize(script)
#     silence = np.zeros(int(0.25 * 1))  # quarter second of silence

#     pieces = []
#     for sentence in sentences:
#         SPEAKER = speaker_lookup[sentence[0].split(":")[0]]
#         print(SPEAKER)
#         audio_array = generate_audio(sentence, history_prompt=SPEAKER)
#         pieces += [audio_array, silence.copy()]


#     write_wav("audio/multi_host.wav", SAMPLE_RATE, np.concatenate(pieces))


def apply_fade(audio_array, fade_ms=30):
    """Applies a linear fade in/out to a NumPy audio array."""
    fade_samples = int(SAMPLE_RATE * fade_ms / 1000)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    audio_array = audio_array.astype(np.float32)

    if len(audio_array) > 2 * fade_samples:
        audio_array[:fade_samples] *= fade_in
        audio_array[-fade_samples:] *= fade_out
    return audio_array

def create_audio(script, voice1, voice2,status_callback=lambda x: None):
    print("Starting Audio generation...")
    status_callback("🔄 Starting audio generation...")
    script = script.strip().split("\n")
    speaker_lookup = {"Alex": voice1, "Sam": voice2}
    host_line_count = {"Alex": 0, "Sam": 0}
    silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence
    pieces = []

    for line in script:
        if line and not line.startswith("**"):
            host_name = line.split(":")[0]
            if host_name in speaker_lookup:
                host_line_count[host_name] += 1
                SPEAKER = speaker_lookup[host_name]
                print(f"Processing {host_name}'s #{host_line_count[host_name]} line:")
                status_callback(f"Processing {host_name}'s #{host_line_count[host_name]} line:")
            else:
                SPEAKER = "alloy"
                print(f"Processing additional line:")

            if ":" in line:
                line = line.split(":", 1)[1].strip()
            else:
                line = line.strip()

            sentences = nltk.sent_tokenize(line)
            for sentence in sentences:
                audio_array = generate_audio(sentence, history_prompt=SPEAKER)
                faded = apply_fade(audio_array)
                pieces += [faded, silence.copy()]
    
    final_audio = np.concatenate(pieces)
    write_wav("audio/multi_host.wav", SAMPLE_RATE, final_audio)
    
    # Normalize and convert to 16-bit PCM
    data_16bit = (final_audio / np.max(np.abs(final_audio)) * 32767).astype(np.int16)
    wavfile.write("audio/multi_host_converted.wav", SAMPLE_RATE, data_16bit)
    status_callback("Audio generation complete!")


# file_path = 'example.md'
# with open(file_path, 'r') as file:
#      file_content = file.read()
# create_audio(file_content,"echo","nova")

