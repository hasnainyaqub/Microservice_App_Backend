from fastapi import APIRouter
from pydantic import BaseModel
from services.chatbot import chat

router = APIRouter()

class ChatRequest(BaseModel):
    message: str


@router.post("/chatbot")
def chatbot_api(payload: ChatRequest):
    return chat(payload.message)
