import uvicorn
from dotenv import load_dotenv
from src.graph import GraphCompiler
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from fastapi import FastAPI, BackgroundTasks
from src.state import GraphState

load_dotenv()

app = FastAPI(
    title="Gmail AI Assistant Service",
    version="1.0",
    description="LangGraph backend for the AI Gmail automation workflow")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

def get_runnable():
    graph_compiler = GraphCompiler()
    return graph_compiler.compiled_graph

runnable = get_runnable()

# Create the Fast API route to invoke the runnable
add_routes(app, runnable, path="/email", input_type=dict)

def main():
    # Start the API
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()


# initial_state = {"emails": [],
#                 "current_email": None,
#                 "category": "",
#                 "drafted_subject": "",
#                 "drafted_body": "",
#                 "summarization": "",
#                 "error": ""}

# @app.get("/status")
# def get_status():
#     return {"status": "online", "agent": "Gmail Assistant"}

# @app.post("/run-agent")
# async def run_agent(background_tasks: BackgroundTasks):
#     """
#     Trigger the email agent and returns a summary of all actions taken.
#     """
#     background_tasks.add_task(process_emails)
#     return {"message": "Agent started processing emails in the background."}

# def process_emails():
#     for output in graph_compiler.compiled_graph.stream(initial_state):
#         # output is a dict: {"node_name": {"updated_state_keys": "values"}}
#         for node_name, state_update in output.items():
#             print(f'--- Finished Node: {node_name}\n')