import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from schemas import EmailClassification, EmailAgentState
import json
from langchain_groq import ChatGroq
from groq import Groq
from langgraph.graph import StateGraph, START, END
from functools import partial

from utils import access_email

load_dotenv()

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


def categorization(state: EmailAgentState, llm) -> dict:

    structured_llm = llm.with_structured_output(EmailClassification)
    email_content = state.email_text

    messages = [
            ("system", "You are an expert email classifier."),
            ("human",  f"Classify this email: {email_content}")
    ]
    result = structured_llm.invoke(messages)
    print(f'DEBUG: \n{result}')
    return {
        "category": result.category
    }

def router(state: EmailAgentState):
    """ Determine next node based on categorization. """
    category = state.category
    if category == "reply":
        return "draft_writer"
    
    elif category == "newsletter":
        return "summarizer"

    # Fallback for notification, social, spam or others
    # TODO: for notification, just shows the subject to the user
    return "archiver"

def main():
    print("Accessing email data...")
    parsed_data = access_email()
    print('AI Email Assistant starting...')

    # 1. Setup LLM
    llm = ChatGroq(model="llama-3.1-8b-instant")

    # TODO: write functions and add "draft_writer", "summarizer", "archiver" to nodes
    workflow = StateGraph(EmailAgentState)

    workflow.add_node("categorize", partial(categorization, llm=llm))
    
    workflow.add_edge(START, "categorize")

    # workflow.add_conditional_edges("categorize", 
    #                                router,
    #                                {"draft_writer": "draft_writer_node",
    #                                 "summarizer": "summarizer_node",
    #                                 "archiver": "archiver_node"})
    # workflow.add_edge("draft_writer_node", END)
    # workflow.add_edge("summarizer_node", END)
    # workflow.add_edge("archiver_node", END)
    workflow.add_edge("categorize", END)
    
    app = workflow.compile()
    print(f'Compiling graph...')
    print("--- Starting Graph Execution ---")
    final_state = app.invoke(parsed_data)
    print("--- Graph Finished ---")    

if __name__ == "__main__":
    main()