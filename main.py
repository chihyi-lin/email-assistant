from dotenv import load_dotenv
from src.graph import GraphCompiler

load_dotenv()
graph_compiler = GraphCompiler()
# graph_compiler.invoke()
initial_state = {"emails": [],
                "current_email": None,
                "category": "",
                "drafted_subject": "",
                "drafted_body": "",
                "summarization": "",
                "error": ""}

for output in graph_compiler.compiled_graph.stream(initial_state):
    # output is a dict: {"node_name": {"updated_state_keys": "values"}}
    for node_name, state_update in output.items():
        print(f'\n--- Finished Node: {node_name}, state_update:\n')
        print(state_update)