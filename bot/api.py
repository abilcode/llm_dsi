from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

app = FastAPI(title="Telegram Message Blast API", version="1.0.0")

telegram_bot = None


class MessageBlastRequest(BaseModel):
    recipients: List[str]
    message: str
    parse_mode: Optional[str] = None


class SingleMessageRequest(BaseModel):
    user_id: int
    message: str
    parse_mode: Optional[str] = None


class MessageBlastResponse(BaseModel):
    blast_id: str
    status: str
    total_recipients: int
    successful: List[str]
    failed: List[Dict[str, str]]
    timestamp: datetime


class UserListResponse(BaseModel):
    total_users: int
    users: List[Dict[str, Any]]


blast_results = {}


def init_bot(bot_instance):
    global telegram_bot
    telegram_bot = bot_instance


@app.get("/")
async def root():
    return {"message": "Telegram Message Blast API", "status": "running"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "bot_connected": telegram_bot is not None,
        "timestamp": datetime.now()
    }


@app.post("/send-message")
async def send_single_message(request: SingleMessageRequest):
    if not telegram_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")

    try:
        success = await telegram_bot.send_message_to_user(
            user_id=request.user_id,
            message=request.message,
            parse_mode=request.parse_mode
        )

        if success:
            return {
                "status": "success",
                "message": f"Message sent to user {request.user_id}",
                "timestamp": datetime.now()
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to send message to user {request.user_id}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
