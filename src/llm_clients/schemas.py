from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    model: str = Field(min_length=1, description="Provider model name")
    prompt: str = Field(min_length=1, max_length=20_000)


class ChatResponse(BaseModel):
    model: str
    text: str