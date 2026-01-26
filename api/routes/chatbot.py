from fastapi import APIRouter
from typing import List, Dict
from pydantic import BaseModel
from services.chatbot import chat

router = APIRouter()

class Message(BaseModel):
    role: str
    message: str
    time: str

class HistoryMessage(Message):
    id: int

class ChatPayload(BaseModel):
    new_message: Message
    history: List[HistoryMessage]


@router.post("/chatbot")
def chatbot_api(payload: ChatPayload):
    return chat(
        payload.new_message.message,
        payload.history
    )
