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
    sentences = nltk.sent_tokenize(script)

    SPEAKER = "v2/en_speaker_6"
    silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence

    pieces = []
    for sentence in sentences:
        audio_array = generate_audio(sentence, history_prompt=SPEAKER)
        pieces += [audio_array, silence.copy()]


    write_wav("bark_generation_myfunc.wav", SAMPLE_RATE, np.concatenate(pieces))

# audio_generate(script)