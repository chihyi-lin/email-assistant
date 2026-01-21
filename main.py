from dotenv import load_dotenv
from src.graph import Workflow

load_dotenv()
workflow = Workflow()
workflow.invoke()