from typing_extensions import TypedDict
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langchain_together import ChatTogether
from util import PdfRead
from util import create_audio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class PDFState(TypedDict):
    pdf_content: AnyMessage
    outline: AnyMessage
    structured_outline: AnyMessage
    segment_transcript: AnyMessage
    deep_dive: AnyMessage
    transcript: AnyMessage 
    podcast_dialogue: AnyMessage
    outline_fusion: AnyMessage
    revision_content: AnyMessage
    genpodcast_dialogue: AnyMessage

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

        graph.add_node("transcript_optimization", self.transcript_optimization)
        graph.add_edge("create_deep_dive","transcript_optimization")

        graph.add_node("create_podcast_dialogue", self.create_podcast_dialog)
        graph.add_edge("transcript_optimization","create_podcast_dialogue")

        graph.add_node("create_outline_fusion",self.create_outline_fusion)
        graph.add_edge("create_podcast_dialogue","create_outline_fusion")

        graph.add_node("create_revision", self.create_revision)
        graph.add_edge("create_outline_fusion","create_revision")

        graph.add_node("structured_podcast_dialog", self.structured_podcast_dialog)
        graph.add_edge("create_revision","structured_podcast_dialog")

        graph.add_edge("structured_podcast_dialog", END)
        graph.set_entry_point("create_outline")

        self.graph = graph.compile()
    
    def create_outline(self, state: PDFState):
        print("Generating Outline")
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
        print("Generating Structured Outline")
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
        print("Generating Segment Transcript")
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
        print("Creating a Deep Dive")
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
    
    def transcript_optimization(self, state:PDFState):
        print("Optimizing Transcript")
        transcript_content= state['deep_dive']
        if hasattr(transcript_content, 'content'):
            transcript_content = transcript_content.content

        prompt = f"""
                You are an expert in content refinement and podcast script optimization. Your role is to improve the clarity, coherence, and engagement of the provided podcast transcript.  

                Objectives:  
                - Enhance readability & flow: Ensure smooth transitions between topics and speakers.  
                - Remove redundancy: Eliminate unnecessary repetition while preserving meaning.  
                - Improve clarity: Reword complex or awkward sentences for better understanding.  
                - Enhance engagement: Add slight conversational adjustments to make the dialogue more dynamic and engaging.  
                - Maintain speaker style: Keep the natural tone and personality of each speaker intact.  

                Expected Output:  
                A refined and optimized podcast transcript that flows naturally, engages the listener, and keeps the conversation structured without losing its authenticity.  

                Content to Optimize:  
                <{transcript_content}>  

                Output Format:  
                - Maintain the same dialogue format (`[Host]:`, `[Guest]:`).  
                - Ensure the final transcript is polished and ready for production.  

                Only provide the optimized transcript—no additional commentary or explanations.  
                """
        result = self.llm(prompt)
        return {'transcript':result}
    
    def create_podcast_dialog(self, state: PDFState):
        print("Generating podcast dialog's")
        podcast_content = state ['transcript']
        if hasattr(podcast_content, 'content'):
            podcast_content = podcast_content.content 
        prompt = f"""
                this is the transcript content you should work with <{podcast_content}>

                You are an expert in podcast scriptwriting and conversational structuring. Your task is to take the provided transcript and turn it into a highly engaging, natural-sounding podcast dialogue between two speakers.

                Objectives:
                Ensure Conversational Flow: Transform the transcript into a fluid, engaging discussion between two hosts.
                Add Personality & Tone: Make the dialogue sound lively, with a friendly, professional, and engaging tone.
                Smooth Transitions: Ensure natural progression from one topic to another.
                Increase Engagement: Include rhetorical questions, relatable anecdotes, or humor where appropriate.
                Maintain Clarity: Keep explanations precise and digestible for listeners.
                Expected Format:
                The podcast should be structured as follows:

                Introduction - Briefly introduce the topic, set expectations, and engage the audience.
                Main Discussion - Dive into key insights from the transcript in a back-and-forth conversation.
                Transitions - Ensure seamless topic changes without abrupt jumps.
                Conclusion - Summarize key takeaways and invite further engagement 
                
                only output the raw result. do not include any other data
                """
        result = self.llm(prompt)
        return {'podcast_dialogue': result}
    
    def create_outline_fusion(self, state: PDFState):
        print("Creating an outline")
        outline_content = state ['podcast_dialogue']
        if hasattr(outline_content, 'content'):
            outline_content = outline_content.content 
        prompt = f"""
                this is the transcript content you should work with <{outline_content}>

                You are an expert in podcast scriptwriting and conversational structuring. Your task is to take the provided transcript and turn it into a highly engaging, natural-sounding podcast dialogue between two speakers.

                Objectives:
                Ensure Conversational Flow: Transform the transcript into a fluid, engaging discussion between two hosts.
                Add Personality & Tone: Make the dialogue sound lively, with a friendly, professional, and engaging tone.
                Smooth Transitions: Ensure natural progression from one topic to another.
                Increase Engagement: Include rhetorical questions, relatable anecdotes, or humor where appropriate.
                Maintain Clarity: Keep explanations precise and digestible for listeners.
                Expected Format:
                The podcast should be structured as follows:

                Introduction - Briefly introduce the topic, set expectations, and engage the audience.
                Main Discussion - Dive into key insights from the transcript in a back-and-forth conversation.
                Transitions - Ensure seamless topic changes without abrupt jumps.
                Conclusion - Summarize key takeaways and invite further engagement 
                
                only output the raw result. do not include any other data
                """
        result = self.llm(prompt)
        return {'outline_fusion': result}
    
    def create_revision(self, state:PDFState):
        outline_fusion_content = state ['outline_fusion']
        if hasattr(outline_fusion_content, 'content'):
            outline_fusion_content = outline_fusion_content.content 
        prompt = f"""
                You are an expert podcast editor. Refine the podcast dialogue using the structured outline to ensure clarity, coherence, and engagement.

                Requirements:
                - Improve flow, making the conversation **more natural and engaging**.
                - Ensure key topics follow the structured outline.
                - Maintain humor and conversational tone.
                - Add minor improvements for storytelling.

                The content: <{outline_fusion_content}> 

                Only provide the optimized transcript—no additional commentary or explanations.  
                """
        result = self.llm(prompt)
        return {'revision_content': result}
    
    def structured_podcast_dialog(self, state: PDFState):
        print("Generating ")
        revision_content = state ['revision_content']
        if hasattr(revision_content, 'content'):
            revision_content = revision_content.content 
        prompt = f"""
                Podcast Script Generation
                You are an expert podcast scriptwriter. Your task is to take the refined podcast dialogue and transform it into a final, polished podcast script that is ready for production.

                Objectives:
                Ensure Broadcast Readiness: The final output should sound professional and engaging, as if recorded for a real podcast.
                Enhance Flow & Delivery: Adjust pacing, sentence structure, and transitions for a smooth listening experience.
                Add Sound Cues & Pauses: Include [music fades in], [dramatic pause], or [laughter] to make the script more dynamic.
                Keep it Conversational: Maintain a lively, natural, and engaging tone between the hosts.
                Structure for Production: Make it easy to read aloud with clear formatting.

                **Intro Music Fades In**                 
                Alex: "Welcome back to *Deep Dive Talks*! Today, we’re diving into [topic]—a subject that has more depth than most people realize."  
                Sam: "[chuckles] That’s right! Did you know that [interesting fact]? It’s one of those things that once you learn, you’ll never see the same way again."  
                Alex: "Let’s start by breaking it down. [Core concept explanation]."  
                Sam: "[Pause] Exactly! And what’s really interesting is that… [Example or Story]."  
                ...  
                Alex: "Alright, let’s wrap things up. Today we covered [key takeaways]."  
                Sam: "Thanks for tuning in! Don’t forget to subscribe and share if you found this useful!"  
                **Outro Music Fades In**

                The content: <{revision_content}> 

                Only provide the optimized transcript—no additional commentary or explanations.  
                """
        result = self.llm(prompt)
        return {'genpodcast_dialogue': result}
        
    def llm(self, prompt):
        if not isinstance(prompt, (dict, str)) and hasattr(prompt, 'content'):
            message = prompt
        else:
            message = HumanMessage(content=str(prompt))
        
        return self.model.invoke([message])
    

def main():
    # Retrieve API key from environment variables
    together_api_key = os.getenv("TOGETHER_API_KEY")
    if not together_api_key:
        raise ValueError("TOGETHER_API_KEY not found in environment variables")

    llm = ChatTogether(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        together_api_key=together_api_key
    )
    pdf = PdfRead("PDF's/dbms.pdf")
    content = pdf.get_text()
    agent = Agent(llm)
    
    result = agent.graph.invoke({'pdf_content': content})
    
    state = 'genpodcast_dialogue'
    result = result[state].content if hasattr(result[state], 'content') else result[state]
    print(result)
    create_audio(result)


if __name__ == "__main__":
    main()
