from colorama import Fore, Style
from .agents import Agents
from .state import GraphState

class Nodes():
    def __init__(self):
        self.agent = Agents()

    def load_new_emails(self, state: GraphState):
        # TODO
        pass

    def categorize_email(self, state: GraphState) -> GraphState:
        """Categorize an email using the agent."""
        print(Fore.BLUE + "Checking email category...\n" + Style.RESET_ALL)
        current_email = state["emails"][-1]
        email_content = current_email.body       
        result = self.agent.categorize_email.invoke({"email_content": email_content})
        return {
            "category": result.category,
            "current_email": current_email}
    
    def route_based_on_category(state: GraphState) -> str:
        """Determine next node based on its category."""
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
        email_content = state["current_email"].body
        result = self.agent.summarize_email.invoke({"email_content": email_content})
        return {"summarization": result.summarization}
    
    def draft_response(self, state: GraphState) -> GraphState:
        """Draft a response using the agent."""
        email_content = state["current_email"].body
        result = self.agent.draft_response.invoke({"email_content": email_content})
        return {"drafted_subject": result.subject,
                "drafted_body": result.body}

    def archive_email(self, state: GraphState):
        # TODO: Print out the subjects of emails that should be archived
        pass