from colorama import Fore, Style
from .agents import Agents
from .state import *
from .utils import GmailTool
class Nodes():
    def __init__(self):
        self.agent = Agents()
        self.gmail_tool = GmailTool()

    def load_new_emails(self, state: GraphState) -> GraphState:
        print(Fore.BLUE + "Loading new emails with Gmail API...\n" + Style.RESET_ALL)
        unanswered_emails = self.gmail_tool.fetch_unanswered_emails(4)
        emails = []
        for email_dict in unanswered_emails:
            emails.append(Email(**email_dict))
        return {"emails": emails}

    def route_check_new_emails_exist(self, state: GraphState) -> str:
        if state["emails"]:
            print(Fore.BLUE + "New emails exist\n" + Style.RESET_ALL)
            return "exist"
        print(Fore.BLUE + "No new emails\n" + Style.RESET_ALL)
        return "not_exist"       

    def add_current_email(self, state: GraphState) -> GraphState:
        current_email = state["emails"][-1]
        print(Fore.BLUE + f"Current email: {current_email}\n" + Style.RESET_ALL)
        return {"current_email": current_email}

    def categorize_email(self, state: GraphState) -> GraphState:
        """Categorize an email using the agent."""
        print(Fore.BLUE + "Checking email category...\n" + Style.RESET_ALL)
        # Truncate to roughly 2000 tokens (approx 1500 words) so it won't exceed token limit
        email_content = state["current_email"].body[:5000]
        try:       
            result = self.agent.categorize_email.invoke({"email_content": email_content})
            print(Fore.GREEN + f"Category: {result.category}\n" + Style.RESET_ALL)
            return {"category": result.category}
        except Exception as e:
            print(f"{Fore.RED}Error in categorization: {e}{Style.RESET_ALL}")
            # Return a marker so the graph knows this one failed
            return {"category": "Error occurs", "error": str(e)}            
    
    def route_based_on_category(self, state: GraphState) -> str:
        """Determine next node based on its category."""
        category = state["category"]
        if category == "reply":
            print(Fore.BLUE + "To drafter...\n" + Style.RESET_ALL)
            return "drafter" 
        elif category == "newsletter":
            print(Fore.BLUE + "To summarizer...\n" + Style.RESET_ALL)
            return "summarizer"
        # Fallback for notification, social, spam or others
        print(Fore.BLUE + "To archiver...\n" + Style.RESET_ALL)
        return "archiver"
    
    def summarize_email(self, state: GraphState) -> GraphState:
        """Summarize an email using the agent."""
        print(Fore.BLUE + "Summarizing the email...\n" + Style.RESET_ALL)
        email_content = state["current_email"].body
        try:
            result = self.agent.summarize_email.invoke({"email_content": email_content})
            print(Fore.GREEN + "Summary: \n" + result.summarization + Style.RESET_ALL)
            return {"summarization": result.summarization}
        except Exception as e:
            print(f"{Fore.RED}Error in summarization: {e}{Style.RESET_ALL}")
            return {"summarization": "Error occurs", "error": str(e)}   

    def draft_response(self, state: GraphState) -> GraphState:
        # TODO: save draft with Gmail api
        """Draft a response using the agent."""
        print(Fore.BLUE + "Drafting a response...\n" + Style.RESET_ALL)
        email_content = state["current_email"].body
        try:
            result = self.agent.draft_response.invoke({"email_content": email_content})
            print(Fore.GREEN + f"Drafted Subject: \n{result.subject}\n" + f"Drafted Body: \n{result.body}\n" + Style.RESET_ALL)
            return {"drafted_subject": result.subject,
                    "drafted_body": result.body}
        except Exception as e:
            print(f"{Fore.RED}Error in drafting: {e}{Style.RESET_ALL}")
            return {"drafted_subject": "Error occurs",
                    "drafted_body": "Error occurs", 
                    "error": str(e)}  

    def archive_email(self, state: GraphState) -> GraphState:
        # TODO: actual archiving in Gmail api
        email_subject = state["current_email"].subject
        print(Fore.BLUE + "Archiving the email...\n" + Style.RESET_ALL)
        return state
    
    def pop_email(self, state: GraphState) -> GraphState:
        """Remove the processed email from email lists."""
        state["emails"].pop()
        print(Fore.BLUE + "Processed email has been removed\n" + Style.RESET_ALL)
        return {"emails": state['emails']}