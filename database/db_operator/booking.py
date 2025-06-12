from utils.logger import logger
from typing import Any, Dict, List, Optional
from datetime import date, datetime
from database.connection import BaseRepository


class BookingRepository:
    def __init__(self):
        self.table_name = "bookings"

    async def create_booking(
        self,
        conn: Any,
        user_id: int,
        room_id: int,
        check_in: date,
        check_out: date,
        status: str = "booked"
    ) -> int:
        """
        Insert a new booking into the bookings table.
        """
        if status not in ('booked', 'checked_in', 'checked_out', 'cancelled'):
            logger.error(f"Invalid booking status: {status}")
            raise ValueError("Invalid booking status")

        data: Dict[str, Any] = {
            "user_id": user_id,
            "room_id": room_id,
            "check_in": check_in,
            "check_out": check_out,
            "status": status
        }

        try:
            repo = BaseRepository()
            booking_id = await repo.insert(conn, data)  # type: ignore
            logger.info(f"Inserted booking with id {booking_id}")
            return booking_id
        except Exception as e:
            logger.error(f"Failed to insert booking: {e}")
            raise

    async def get_bookings_by_user(
        self,
        conn: Any,
        user_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve bookings for a specific user.
        """
        try:
            repo = BaseRepository()
            query = (
                f"SELECT * FROM {self.table_name} "
                "WHERE user_id = %s "
                "ORDER BY created_at DESC "
                "LIMIT %s OFFSET %s"
            )
            params = (user_id, limit, offset)
            rows = await repo.fetch_all(conn, query, params)
            logger.info(
                f"Retrieved {len(rows)} bookings for user_id {user_id}")
            return rows
        except Exception as e:
            logger.error(f"Failed to retrieve bookings: {e}")
            raise

    async def update_booking_status_by_telegram_and_room(
        self,
        conn: Any,
        telegram_id: str,
        room_id: str,
        new_status: str
    ) -> None:
        """
        Update the booking status by telegram_id and room_id.
        """
        if new_status not in ('booked', 'checked_in', 'checked_out', 'cancelled'):
            logger.error(f"Invalid booking status: {new_status}")
            raise ValueError("Invalid booking status")

        try:
            repo = BaseRepository()
            query = (
                f"UPDATE {self.table_name} SET status = $1 "
                "WHERE room_id = $2 AND user_id = (SELECT user_id FROM users WHERE telegram_id = $3)"
            )
            # ✅ Flat tuple
            await repo.execute_query(conn, query, new_status, int(room_id), telegram_id)
            logger.info(
                f"Updated booking status to '{new_status}' for telegram_id {telegram_id} and room_id {room_id}")
        except Exception as e:
            logger.error(f"Failed to update booking status: {e}")
            raise
