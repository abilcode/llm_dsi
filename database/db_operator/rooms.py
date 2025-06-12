from typing import Any, List, Dict
import logging

from database.connection import BaseRepository

logger = logging.getLogger(__name__)


class RoomsRepository:
    def __init__(self):
        self.table_name = "rooms"

    async def get_all_available_rooms(
        self,
        conn: Any,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all available rooms (where is_available is True).
        """
        try:
            repo = BaseRepository()
            query = (
                f"SELECT * FROM {self.table_name} "
                "WHERE is_available = TRUE "
                "ORDER BY room_id ASC "
                "LIMIT %s OFFSET %s"
            )
            params = (limit, offset)
            rows = await repo.fetch_all(conn, query, params)
            logger.info(f"Retrieved {len(rows)} available rooms")
            return rows
        except Exception as e:
            logger.error(f"Failed to retrieve available rooms: {e}")
            raise

    async def update_room_availability_by_id(
        self,
        conn: Any,
        room_id: str,
        is_available: bool
    ) -> None:
        """
        Update the room availability status by room_id.
        """
        try:
            repo = BaseRepository()
            query = (
                f"UPDATE {self.table_name} SET is_available = $1 "
                "WHERE room_id = $2"
            )
            await repo.execute_query(conn, query, is_available, int(room_id))
            logger.info(
                f"Updated room_id {room_id} availability to {is_available}")
        except Exception as e:
            logger.error(f"Failed to update room availability: {e}")
            raise
