from langgraph.graph import START, END, StateGraph
from .state import *
from .nodes import Nodes
class GraphCompiler():
    def __init__(self):
        workflow = StateGraph(GraphState)
        nodes = Nodes()

        workflow.add_node("load_new_emails", nodes.load_new_emails)
        workflow.add_node("add_current_email", nodes.add_current_email)
        workflow.add_node("categorize_email", nodes.categorize_email)
        workflow.add_node("summarize_email", nodes.summarize_email)
        workflow.add_node("draft_response", nodes.draft_response)
        workflow.add_node("archive_email", nodes.archive_email)
        workflow.add_node("pop_email", nodes.pop_email)

        workflow.add_edge(START, "load_new_emails")
        workflow.add_conditional_edges("load_new_emails", 
                                       nodes.route_check_new_emails_exist,
                                       {"exist": "add_current_email",
                                        "not_exist": END})
        workflow.add_edge("add_current_email", "categorize_email")
        workflow.add_conditional_edges("categorize_email",
                                       nodes.route_based_on_category,
                                       {"drafter": "draft_response",
                                        "summarizer": "summarize_email",
                                        "archiver": "archive_email"})

        workflow.add_edge("summarize_email", "pop_email")
        workflow.add_edge("draft_response", "pop_email")
        workflow.add_edge("archive_email", "pop_email")
        workflow.add_conditional_edges("pop_email", nodes.route_check_new_emails_exist,
                            {"exist": "add_current_email",
                            "not_exist": END})
        
        self.compiled_graph = workflow.compile()

    def invoke(self):
        initial_state = {"emails": [],
                        "current_email": None,
                        "category": "",
                        "drafted_subject": "",
                        "drafted_body": "",
                        "summarization": ""}
        return self.compiled_graph.invoke(initial_state)