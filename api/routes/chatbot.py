from fastapi import APIRouter
from pydantic import BaseModel
from services.chatbot import chat

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str


@router.post("/chatbot", response_model=ChatResponse)
def chatbot_api(payload: ChatRequest):
    response = chat(payload.message)
    return {"reply": response}
