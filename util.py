# importing required modules
from pypdf import PdfReader
# import os
import numpy as np
import os
os.environ["SUNO_USE_SMALL_MODELS"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import nltk
from bark.generation import (
generate_text_semantic,
preload_models,
)

from bark.api import semantic_to_waveform
from bark import generate_audio, SAMPLE_RATE
preload_models()

from scipy.io.wavfile import write as write_wav 

class PdfRead:
    def __init__(self, name, start=None, end=None):
        self.name = name
        # creating a pdf reader object
        self.reader = PdfReader("PDF's/dbms.pdf")

        # printing number of pages in pdf file
        page_length = len(self.reader.pages)
        print(len(self.reader.pages))

        self.text = ""
        begin = 0
        finish = page_length
        
        if start != None and end != None:
            begin = start
            finish = end
        elif start != None and end == None:
            begin = start
            end = start
        
        print(f"Reading from pages: {begin} to {finish}")
        for i in range(begin, finish):
                # getting a specific page from the pdf file
                page = self.reader.pages[i]

                # extracting text from page
                self.text += page.extract_text()

    def get_text(self) -> str:
        return str(self.text)


def audio_generate(script):
    script = script.replace("\n", " ").strip()
    speaker_lookup = {"Alex": "v2/en_speaker_6", "Sam": "v2/en_speaker_2"}
    
    sentences = nltk.sent_tokenize(script)
    silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence

    pieces = []
    for sentence in sentences:
        SPEAKER = speaker_lookup[sentence[0].split(":")[0]]
        print(SPEAKER)
        audio_array = generate_audio(sentence, history_prompt=SPEAKER)
        pieces += [audio_array, silence.copy()]


    write_wav("multi_host.wav", SAMPLE_RATE, np.concatenate(pieces))


def create_audio(script):
    print("Starting Audio generation...")
    script = script.strip().split("\n")
    speaker_lookup = {"Alex": "v2/en_speaker_6", "Sam": "v2/en_speaker_3"}
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
            else:
                SPEAKER = "v2/en_speaker_6"
                print(f"Processing additional line:")

            line = line.split(":").pop(1)
            sentences = nltk.sent_tokenize(line)
            for sentence in sentences:
                audio_array = generate_audio(sentence, history_prompt=SPEAKER)
                pieces += [audio_array, silence.copy()]
    
    write_wav("multi_host.wav", SAMPLE_RATE, np.concatenate(pieces))



# create_audio(script)