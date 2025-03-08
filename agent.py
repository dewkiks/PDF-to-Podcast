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
    segment_transcript: AnyMessage

class Agent:
    def __init__(self, model):
        
        self.model = model
        graph = StateGraph(PDFState)

        graph.add_node("create_outline", self.create_outline)
        graph.add_node("create_structured_outline", self.create_structured_outline)
        graph.add_node("create_segment_transcript", self.create_segment_transcript)
        graph.add_edge("create_outline", "create_structured_outline")
        graph.add_edge("create_structured_outline", "create_segment_transcript")
        graph.add_edge("create_segment_transcript", END)
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
            Expected Output: A conversion plan that organizes content for spoken delivery.

            The content: <{outline_content}>.

            Make sure to only include the outline. Do not include any other data like "here is your.." and any other stuff like that.
        """
        result = self.llm(prompt)
        return {'structured_outline': result}
    
    def create_segment_transcript(self, state: PDFState):
        segment_content = state['structured_outline']
        if hasattr(segment_content, 'content'):
            segment_content = segment_content.content
        
        prompt = f"""
            You are an expert at creating transcripts based on based on segments provided.
            So you will be provided different segments you have to convert each segment into natural sounding spoken language and add more detail for each segment.
            When you recive the structured outline for a conversation you have to analyse the contents think deeply and create a well structured result for each segments.
            So from the provided data look into each segments and for each segments you should convert it into a natural sounding spoke language, add more detail, match the style of a podcast between 2 people.
            Your output should look like this:
            example:
                Person 1: "Hello listeners, and welcome to today's episode! Have you ever wondered ..."
                Person 2: "I'm really excited about this topic. Most people have heard ..."

            The content is provided between the angle brackets.

            The content: <{segment_content}>

            Make sure to only add the result. No extra text like "Here is your.. " or "here you go .." no need of such texts before the result.
        """

        result = self.llm(prompt)
        return {'segment_transcript': result}

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
    result = result['segment_transcript'].content if hasattr(result['segment_transcript'], 'content') else result['segment_transcript']
    print(result)

main()
