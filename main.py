import uvicorn
from dotenv import load_dotenv
from src.graph import GraphCompiler
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from fastapi import FastAPI
from langchain_core.runnables import RunnableLambda

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

async def process_emails_streaming():
    """
    Yields state updates in real-time.
    """
    try:
        for state in GraphCompiler().run():
            for node_name, state in state.items():
                yield {
                    "current_log": state.get('current_log', ""),
                    "error": state.get("error", ""),
                }
    except Exception as e:
        yield {
            "error": f"Error: {str(e)}"
        }

email_agent_streaming = RunnableLambda(process_emails_streaming)

# Create the Fast API route with streaming support
add_routes(app, email_agent_streaming, path="/email", enable_feedback_endpoint=True, playground_type="default")

def main():
    # Start the API
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()