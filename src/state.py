from pydantic import BaseModel, Field
from typing import List, TypedDict

class Email(BaseModel):
    id: str = Field(..., description="Unique id of the email")
    sender: str = Field(..., description="Email address of the sender")
    date: str = Field(..., description="Date of the email")
    subject: str = Field(..., description="Subject of the email")
    body: str = Field(..., description="Content of the email")

class GraphState(TypedDict):
    emails: List[Email]
    current_email: Email
    # generated content
    category: str
    drafted_subject: str
    drafted_body: str
    summarization: str