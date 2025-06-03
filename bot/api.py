from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from database.connection import database
from sheets.google_sheets import update_room_colors_in_sheet


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(title="Telegram Message Blast API",
              version="1.0.0", lifespan=lifespan)

telegram_bot = None


class MessageBlastRequest(BaseModel):
    recipients: List[str]
    message: str
    parse_mode: Optional[str] = None


class SingleMessageRequest(BaseModel):
    user_id: int


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
    return {"message": "Pak Kos API", "status": "running"}


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
            message="Waktu tenggat sudah dekat, jangan lupa bayar kosanmu ya!",
            parse_mode="markdown"
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


@app.post("/update-room-availability")
async def update_room_availability():
    try:
        rows = await database.fetch_all("SELECT room_id, is_available FROM rooms")
        room_data = [dict(row) for row in rows]
        update_room_colors_in_sheet(room_data)

        return {"status": "success", "updated_rooms": len(room_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
