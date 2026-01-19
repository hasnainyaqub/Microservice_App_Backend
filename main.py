from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.recommend import router as recommend_router
from api.routes.chatbot import router as chatbot_router

# === Initialize FastAPI App ===
app = FastAPI(title="Restaurant Recommendation API")

# === Root Endpoint ===
@app.get("/")
def home():
    return {"message": "Restaurant Recommendation API Running"}

# === Health Check Endpoint ===
@app.get("/health")
def health():
    return {"status": "ok"}

# === Configure CORS Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://192.168.1.2:3000",
        "http://192.168.1.2:3001",
        "http://192.168.1.11:3000",
        "http://192.168.1.11:3001",
        "http://192.168.100.12:3000",
        "http://192.168.100.12:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# === Include Routers ===
app.include_router(recommend_router, prefix="/api")
app.include_router(chatbot_router, prefix="/api")
