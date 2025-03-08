# importing required modules
from pypdf import PdfReader

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



