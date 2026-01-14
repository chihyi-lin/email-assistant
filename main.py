import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from schemas import EmailClassification, EmailAgentState

from langchain_groq import ChatGroq
from groq import Groq
from langgraph.graph import StateGraph, START, END
from functools import partial

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


def access_email(state: EmailAgentState):
    """Fetches email and updates the state."""
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', maxResults=2).execute()
    messages = results.get('messages', [])

    if not messages:
        return {"email_text": None}
    
    msg = service.users().messages().get(userId='me', id=messages[0]['id']).execute()
    # Update the state with the email text
    return {"email_text": msg['snippet']}

def categorization(state: EmailAgentState, llm) -> dict:

    # client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    structured_llm = llm.with_structured_output(EmailClassification)
    email_content = state["email_text"]

    messages = [
            ("system", "You are an expert email classifier."),
            ("human",  f"Classify this email: {email_content}")
    ]
    result = structured_llm.invoke(messages)
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
    return "archiver"

def main():
    print('AI Email Assistant starting...')

    # 1. Setup LLM
    llm = ChatGroq(model="llama-3.1-8b-instant")
    

    # TODO: write functions and add "draft_writer", "summarizer", "archiver" to nodes
    workflow = StateGraph(EmailAgentState)
    workflow.add_node("access_email", access_email)
    workflow.add_node("categorize", partial(categorization, llm=llm))
    
    workflow.add_edge(START, "access_email")
    workflow.add_edge("access_email", "categorize")
    workflow.add_conditional_edges("categorize", 
                                   router,
                                   {"draft_writer": "draft_writer_node",
                                    "summarizer": "summarizer_node",
                                    "archiver": "archiver_node"})
    workflow.add_edge("draft_writer_node", END)
    workflow.add_edge("summarizer_node", END)
    workflow.add_edge("archiver_node", END)
    
    app = workflow.compile()

if __name__ == "__main__":
    main()