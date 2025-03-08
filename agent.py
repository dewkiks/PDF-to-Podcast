from typing_extensions import TypedDict
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langchain_together import ChatTogether

from util import PdfRead
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import uuid

client = ElevenLabs(
  api_key='sk_f7481f225665225959deca3089ab06ee9b805abeb08c9737'
)


class PDFState(TypedDict):
    pdf_content: AnyMessage
    outline: AnyMessage
    structured_outline: AnyMessage
    segment_transcript: AnyMessage
    deep_dive: AnyMessage

class Agent:
    def __init__(self, model):
        
        self.model = model
        graph = StateGraph(PDFState)

        graph.add_node("create_outline", self.create_outline)
        graph.add_node("create_structured_outline", self.create_structured_outline)
        graph.add_edge("create_outline", "create_structured_outline")

        graph.add_node("create_segment_transcript", self.create_segment_transcript)
        graph.add_edge("create_structured_outline", "create_segment_transcript")
        
        graph.add_node("create_deep_dive", self.create_deep_dive)
        graph.add_edge("create_segment_transcript", "create_deep_dive")

        graph.add_edge("create_deep_dive", END)
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
    
    def create_deep_dive(self, state: PDFState):
        deep_content = state['segment_transcript']
        if hasattr(deep_content, 'content'):
            deep_content = deep_content.content

        prompt =  f"""
            You are an expert at an at every topic and have a great knowledge about analogies, background and example's for all topics.
            Your role is to add depth, nuance, and additional content to import sections in a transcript provided. 
            The transcript will be a transcript for a podcast between 2 people talking about some content. You should carefully analyze the transcript.
            Find important topics or sections and provide in depth information for it. You should add depth to the content, provide analogies, provide backgroud informations and create suitable examples.


            The expected result is a a Enhaced content or transcipt with detailed explanations and insights.
            The content is provided below between the angle brackets.

            The content: <{deep_content}>
            Make sure to only add the result. No extra text like "Here is your.. " or "here you go .." no need of such texts before the result.
        """
        result = self.llm(prompt)
        return {'deep_dive': result}
    
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
    
def text_to_speech_file(text: str) -> str:
    # Calling the text_to_speech conversion API with detailed parameters
    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB", # Adam pre-made voice
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5", # use the turbo model for low latency
        # Optional voice settings that allow you to customize the output
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
            speed=1.0,
        ),
    )
    # uncomment the line below to play the audio back
    # play(response)
    # Generating a unique file name for the output MP3 file
    save_file_path = f"{uuid.uuid4()}.mp3"
    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
    print(f"{save_file_path}: A new audio file was saved successfully!")
    # Return the path of the saved audio file
    return save_file_path
        
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
    
    state = 'deep_dive'
    # Print the content of the message
    result = result[state].content if hasattr(result[state], 'content') else result[state]
    # print(result)
    text_to_speech_file(result)

main()
