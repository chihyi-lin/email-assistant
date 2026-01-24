from pydantic import BaseModel, Field
from typing import List, TypedDict, Optional

class Email(BaseModel):
    id: str = Field(..., description="Unique id of the email")
    threadId: str = Field(..., description="Thread id of the email")
    messageId: str = Field(..., description="Message id of the email")
    references: str = Field(..., description="References of the email")
    sender: str = Field(..., description="Email address of the sender")
    subject: str = Field(..., description="Subject of the email")
    date: str = Field(..., description="Date of the email")
    body: str = Field(..., description="Content of the email")

class GraphState(TypedDict):
    emails: List[Email]
    current_email: Optional[Email]
    # generated content
    category: str
    drafted_subject: str
    drafted_body: str
    summarization: str
    error: str  # log what went wrong during LLM calls