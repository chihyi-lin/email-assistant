from dotenv import load_dotenv
from src.graph import Workflow

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from src.schemas import EmailClassification, EmailAgentState
import json
from groq import Groq
from langgraph.graph import StateGraph, START, END
from functools import partial

from utils import access_email

load_dotenv()

workflow = Workflow()
app = workflow.app


# --- GMAIL SETUP ---
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Handles OAuth2 authentication and returns the Gmail service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


# def categorization(state: EmailAgentState, llm) -> dict:
#     """Call LLM to categorize emails. Returns category."""
#     structured_llm = llm.with_structured_output(EmailClassification)
#     email_content = state.email_text

#     messages = [
#             ("system", "You are an expert email classifier."),
#             ("human",  f"Classify this email: {email_content}")
#     ]
#     result = structured_llm.invoke(messages)
#     print({result})
#     return {"category": result.category}


# def router(state: EmailAgentState):
#     """ Determine next node based on categorization. """
#     category = state.category
    
#     if category == "newsletter":
#         return "summarizer"

#     # Fallback for notification, social, spam or others
#     # TODO: for notification, social, spam or others just shows the subject to the user
#     return "archiver"


# def summarizer(state: EmailAgentState, llm) -> dict:
#     """Call LLM to summarize an email. Returns summary."""

#     email_content = state.email_text

#     messages = [
#             ("system", "You are a tech expert. Summarize the content using bullet points. Focus on key technical takeaways and actionable insights. Max 8 sentences."),
#             ("human",  f"Content to summarize: {email_content}")
#     ]
#     result = llm.invoke(messages)
#     summary_text = result.content
#     print(f'Generated summary for tech newsletter: {summary_text}')
#     return {"summarization": summary_text}

def archiver(state: EmailAgentState):
    pass

def main():
    print("Accessing email data...")
    parsed_data = access_email()
    print('AI Email Assistant starting...')

    # workflow = StateGraph(EmailAgentState)
    # workflow.add_node("categorize", partial(categorization, llm=llm))
    # workflow.add_node("summarize", partial(summarizer, llm=llm))
    # workflow.add_node("archive", archiver)
    # workflow.add_edge(START, "categorize")
    # workflow.add_conditional_edges("categorize", 
    #                                router,
    #                                {"summarizer": "summarize",
    #                                 "archiver": "archive"})
    # workflow.add_edge("summarize", END)
    # workflow.add_edge("archive", END)
    # app = workflow.compile()
    # print(f'Compiling graph...')
    # print("--- Starting Graph Execution ---")
    # final_state = app.invoke(parsed_data)
    # # TODO: Printout final EmailClassification
    # print("--- Graph Finished ---")    

if __name__ == "__main__":
    main()