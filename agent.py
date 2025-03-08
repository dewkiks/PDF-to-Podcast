from typing_extensions import TypedDict
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langchain_together import ChatTogether

from util import PdfRead

class PDFState(TypedDict):
    pdf_content: AnyMessage
    outline: AnyMessage
    structured_outline: AnyMessage
    podcast_dialog: AnyMessage

class Agent:
    def __init__(self, model):
        
        self.model = model
        graph = StateGraph(PDFState)

        graph.add_node("create_outline", self.create_outline)
        graph.add_node("create_structured_outline", self.create_structured_outline)
        graph.add_edge("create_structured_outline", END)
        graph.add_edge("create_outline", "create_structured_outline")
        graph.set_entry_point("create_outline")
        self.graph = graph.compile()
        
    def create_outline(self, state: PDFState):
        print("Creating Outline")
        # Get the content in a safer way
        pdf_content = state['pdf_content']
        if hasattr(pdf_content, 'content'):
            pdf_content = pdf_content.content
        
        prompt = f"""
                You are an expert at creating structured outlines based on content.
                Your task is to deeply think about the content understand its meaning and create a high-level structural outline of the Content given below inside the angle brackets.

                Expected Output: A hierarchical outline with main topics and subtopics

                <{pdf_content}>.

                Make sure to only include the high level struture only. Do not include any other data.
            """
        result = self.llm(prompt)
        return {'outline': result}

    def create_structured_outline(self, state: PDFState):
        outline_content = state['outline']
        if hasattr(outline_content, 'content'):
            outline_content = outline_content.content
        
        prompt = f"""
            You are an expert at transforming basic outlines into an outline suitable for a 2 person conversation.
            Your task is to create a conversation plan between two people based on the outline provided below inside the angle barackets.
            This plan or outline should be very structured and should include,
                1) Introduction
                2) Main Segment
                3) transition
                4) Conclusion
            Expected Output: A conversion plan that organizes content for spoken delivery

            The content: <{outline_content}>.
        """
        result = self.llm(prompt)
        return {'structured_outline': result}

    def llm(self, prompt):
        # Check if prompt is already a message object - use base class instead of subscripted generic
        if not isinstance(prompt, (dict, str)) and hasattr(prompt, 'content'):
            # It's already a message object
            message = prompt
        else:
            # If it's a string or other type, convert it to a HumanMessage
            message = HumanMessage(content=str(prompt))
        
        # Make sure we're invoking with the right format for Together AI
        return self.model.invoke([message])
        
def main():
    llm = ChatTogether(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        together_api_key="84e8df9a595039765758ae96105665d37e873e9619a2c209ee31a108db5875ef"
    )
    pdf = PdfRead("PDF's/dbms.pdf")
    content = pdf.get_text()
    agent = Agent(llm)
    
    # Start with a simple string, not a message object
    result = agent.graph.invoke({'pdf_content': content})
    
    # Print the content of the message
    structured_outline = result['structured_outline'].content if hasattr(result['structured_outline'], 'content') else result['structured_outline']
    print(structured_outline)

main()
