from langgraph.graph import END, StateGraph
from .state import GraphState
from .nodes import Nodes

class Workflow():
    def __init__(self):
        workflow = StateGraph(GraphState)
        nodes = Nodes()

        workflow.add_node("load_new_emails", nodes.load_new_emails)
        workflow.add_node("categorize_email", nodes.categorize_email)
        workflow.add_node("summarize_email", nodes.summarize_email)
        workflow.add_node("draft_response", nodes.draft_response)
        workflow.add_node("archive_email", nodes.archive_email)

        workflow.add_edge("load_new_emails", "categorize_email")
        workflow.add_conditional_edges("categorize_email",
                                       nodes.route_based_on_category,
                                       {"drafter": "draft_response",
                                        "summarizer": "summarize_email",
                                        "archiver": "archive_email"})
        workflow.add_edge("load")
        workflow.add_edge("draft_response", END)
        workflow.add_edge("summarize_email", END)
        workflow.add_edge("archive_email", END)
        
        self.app = workflow.compile()