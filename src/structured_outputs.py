from typing import Literal
from pydantic import BaseModel, Field

EmailCategory = Literal["response_required", "newsletter", "notification", "social", "spam", "others"]

class EmailClassificationOutput(BaseModel):
    category: EmailCategory = Field(
        description="The primary intent of the email."
        )

class SummarizationOutput(BaseModel):
    summarization: str = Field(
        description="Summarization of the email."
    )

class ResponseOutput(BaseModel):
    subject: str = Field(
        description="The subject of the drafted email."
    )
    body: str = Field(
        description="The body of the drafted email."
    )