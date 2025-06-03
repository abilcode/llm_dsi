from fastapi import FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel
from typing import List
from datetime import datetime

from utils.logger import logger
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


class SingleMessageRequest(BaseModel):
    telegram_ids: List[int]
    message: str


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


@app.post("/send-messages")
async def send_messages(request: SingleMessageRequest):
    if not telegram_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")

    received_users = []

    for id in request.telegram_ids:
        try:
            success = await telegram_bot.send_message_to_user(
                user_id=id,
                message=request.message,
                parse_mode="markdown"
            )

            if success:
                received_users.append(id)
            else:
                logger.error(f"Failed to sent to user {id}")
        except Exception as e:
            logger.error(f"Failed to sent to user {id}")

    return {
        "status": "success",
        "message": f"Message sent to users {received_users}",
        "timestamp": datetime.now()
    }


@app.post("/update-room-availability")
async def update_room_availability():
    try:
        rows = await database.fetch_all("SELECT room_id, is_available FROM rooms")
        room_data = [dict(row) for row in rows]
        update_room_colors_in_sheet(room_data)

        return {"status": "success", "updated_rooms": len(room_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/payment-callback")
async def payment_callback():
    return
