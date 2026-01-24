from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from .structured_outputs import *

class Agents():
    def __init__(self):
        llm = ChatGroq(model="llama-3.3-70b-versatile")    # "llama-3.3-70b-versatile", "llama-3.1-8b-instant"

        # categorize email chain
        categorize_email_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert email classifier."),
            ("human",  "Classify this email: {email_content}")
        ])
        self.categorize_email = categorize_email_prompt | llm.with_structured_output(EmailClassificationOutput)

        # summarize_email_chain
        summarize_email_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a tech expert. Provide a concise summary of the following email."),
            ("human",  "Content to summarize:\n {email_content}")
        ])
        self.summarize_email = summarize_email_prompt | llm.with_structured_output(SummarizationOutput)

        # draft_response_chain
        draft_response_prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an email assistant specializing in professional correspondence. "
                "Your goal is to draft a helpful, concise, and polite response based on the provided email. "
                "Maintain a professional yet friendly tone. Always include a placeholder for the sender's name "
                "and ensure the response directly addresses the core points mentioned in the original email."
            )),
            ("human",  "Email Content:\n {email_content}")
        ])
        self.draft_response = draft_response_prompt | llm.with_structured_output(ResponseOutput)