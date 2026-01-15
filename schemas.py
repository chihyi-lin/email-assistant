from typing import Literal, Optional
from pydantic import BaseModel, Field

EmailCategory = Literal["reply", "newsletter", "notification", "social", "spam", "others"]

class EmailClassification(BaseModel):
    category: EmailCategory = Field(
        description="The primary intent of the email."
        )
    
# The State of the Graph
class EmailAgentState(BaseModel):
    sender_name: str
    sender_email: str
    email_date: str
    email_text: str
    email_id: str

    category: Optional[EmailCategory] = None

    # generated content
    draft_response: Optional[str] = None
    summarization: Optional[str] = None