from colorama import Fore, Style
from .agents import Agents
from .state import *
from .utils import GmailTool
class Nodes():
    def __init__(self):
        self.agent = Agents()
        self.gmail_tool = GmailTool()

    def load_new_emails(self, state: GraphState) -> GraphState:
        print(Fore.BLUE + "Loading new emails...\n" + Style.RESET_ALL)
        unanswered_emails = self.gmail_tool.fetch_unanswered_emails(3)
        emails = []
        for email_dict in unanswered_emails:
            emails.append(Email(**email_dict))
        if emails:
            return {"emails": emails, "current_email": emails[-1]}
        return {"emails": emails}

    def check_new_emails_exist(self, state: GraphState):
        if state["emails"]:
            print(Fore.BLUE + "New emails exist\n" + Style.RESET_ALL)
            return "exist"
        print(Fore.BLUE + "No new emails\n" + Style.RESET_ALL)
        return "not_exist"       

    def categorize_email(self, state: GraphState) -> GraphState:
        """Categorize an email using the agent."""
        print(Fore.BLUE + "Checking email category...\n" + Style.RESET_ALL)
        # current_email = state["emails"][-1]
        # Truncate to roughly 2000 tokens (approx 1500 words) so it won't exceed token limit
        email_content = state["current_email"].body[:5000]       
        result = self.agent.categorize_email.invoke({"email_content": email_content})
        print(Fore.CYAN + "Category: " + result.category + Style.RESET_ALL)
        return {
            "category": result.category}
    
    def route_based_on_category(self, state: GraphState) -> str:
        """Determine next node based on its category."""
        print(Fore.BLUE + "Routing based on the category...\n" + Style.RESET_ALL)
        category = state["category"]
        if category == "reply":
            return "drafter" 
        elif category == "newsletter":
            return "summarizer"
        # Fallback for notification, social, spam or others
        # TODO: for notification, social, spam or others just shows the subject to the user
        return "archiver"
    
    def summarize_email(self, state: GraphState) -> GraphState:
        """Summarize an email using the agent."""
        print(Fore.BLUE + "Summarizing the email...\n" + Style.RESET_ALL)
        email_content = state["current_email"].body
        result = self.agent.summarize_email.invoke({"email_content": email_content})
        print(Fore.CYAN + "Summary: \n" + result.summarization + Style.RESET_ALL)
        # Update the email list for graph state
        remaining_emails = state["emails"][:-1]
        return {"summarization": result.summarization,
                "emails": remaining_emails}
    
    def draft_response(self, state: GraphState) -> GraphState:
        # TODO: save draft with Gmail api
        """Draft a response using the agent."""
        print(Fore.BLUE + "Drafting a response...\n" + Style.RESET_ALL)
        email_content = state["current_email"].body
        result = self.agent.draft_response.invoke({"email_content": email_content})
        print(Fore.CYAN + f"Drafted Subject: \n{result.subject}\n" + f"Drafted Body: \n{result.body}\n" + Style.RESET_ALL)
        remaining_emails = state["emails"][:-1]
        return {"drafted_subject": result.subject,
                "drafted_body": result.body,
                "emails": remaining_emails}

    def archive_email(self, state: GraphState) -> GraphState:
        # TODO: actual archiving in Gmail api
        email_subject = state["current_email"].subject
        print(Fore.BLUE + "Archiving the email: " + email_subject + "\n" + Style.RESET_ALL)
        remaining_emails = state["emails"][:-1]
        return {"emails": remaining_emails,
                "current_email": remaining_emails[-1]}