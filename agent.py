from typing_extensions import TypedDict
import operator
from langgraph.graph import StateGraph, END

from util import PdfRead

class PDFState(TypedDict):
    pdf_content: str
    outline: str
    structured_outline: str

class Agent:
    def __init__(self, model):
        self.model = model
        graph = StateGraph(PDFState)
        graph.add_node("outline", self.create_outline)
        graph.add_node("structured_outline", self.create_structured_outline)
        graph.add_edge("structured_outline", END)
        graph.add_edge("outline", "structured_outline")
        graph.compile()

    def create_outline(self, state: PDFState):
        prompt = f"""
                You are an expert at creating structured outlines based on content.
                Your task is to deeply think about the content understand its meaning and create a high-level structural outline of the Content given below inside the angle brackets.

                Expected Output: A hierarchical outline with main topics and subtopics

                <{state['pdf_content']}>.

                Make sure to only include the high level struture only. Do not include any other data.
            """
        state['outline'] = self.llm(prompt)

    def create_structured_outline(self, state: PDFState):
        prompt = f"""
            You are an expert at transforming basic outlines into an outline suitable for a 2 person conversation.
            Your task is to create a conversation plan between two people based on the outline provided below.
            This plan or outline should be very structured and should include,
                1) Introduction
                2) Main Segment
                3) transition
                4) Conclusion
            Expected Output: A conversion plan that organizes content for spoken delivery
            
        """

    def llm(self, prompt):
        return self.model.invoke(prompt)
        
