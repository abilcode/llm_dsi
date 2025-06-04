from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

from midtrans.client import create_payment_link
from utils.logger import logger
from database.connection import database
from sheets.google_sheets import update_room_colors_in_sheet


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await database.connect()
#     yield
#     await database.disconnect()

app = FastAPI(title="Telegram Message Blast API",
              version="1.0.0")

telegram_bot = None


class SingleMessageRequest(BaseModel):
    telegram_ids: List[int]
    message: str


class GeneratePaymentLinkRequest(BaseModel):
    booking_id: int
    price: float


class PaymentCallbackRequest(BaseModel):
    order_id: str
    transaction_status: str


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


@app.post('/generate-payment-link')
async def generate_payment_link(request: GeneratePaymentLinkRequest):
    try:
        payment_link = create_payment_link(request.booking_id, request.price)

        return {"status": "success", "payment_link": payment_link}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/payment-callback")
async def payment_callback(request: PaymentCallbackRequest):
    try:
        booking_id = request.order_id
        transaction_status = request.transaction_status

        if not booking_id:
            raise HTTPException(
                status_code=400, detail="Missing order_id in payload")

        # Add Update transaction query here

        logger.info("payment success", transaction_status, booking_id)
    except Exception as e:
        logger.error(f"Failed to handle payment callback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
