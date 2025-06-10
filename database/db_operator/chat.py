from utils.logger import logger
from typing import Any, Dict
from datetime import datetime
from database.connection import BaseRepository, DatabaseConnection
from database.db_operator.users import UsersRepository

class ChatRepository:
    def __init__(self):
        self.table_name = "messages"

    async def insert_chat(
        self,
        user_id: int,
        chat_type: str,
        role: str,
        chat: str,
        sent_at: datetime = None
    ) -> int:
        """
        Insert a chat message into the messages table.

        Args:
            user_id: ID of the user (telegram_id).
            chat_type: 'IN' for incoming, 'OUT' for outgoing.
            role: 'AGENT' or 'USER'.
            chat: The chat message content.
            sent_at: Optional datetime for when the message was sent.

        Returns:
            The inserted message_id.
        """

        users_db = UsersRepository()
        try:
            async with DatabaseConnection() as conn:
                internal_user_id = await users_db.insert_user(telegram_id=user_id)

                if chat_type not in ('IN', 'OUT'):
                    logger.error(f"Invalid chat_type: {chat_type}")
                    raise ValueError("chat_type must be 'IN' or 'OUT'")
                if role not in ('AGENT', 'USER'):
                    logger.error(f"Invalid role: {role}")
                    raise ValueError("role must be 'AGENT' or 'USER'")
                if not chat:
                    logger.error("Chat message cannot be empty")
                    raise ValueError("chat cannot be empty")

                data: Dict[str, Any] = {
                    "user_id": internal_user_id,
                    "chat_type": chat_type,
                    "role": role,
                    "chat": chat
                }
                if sent_at:
                    data["sent_at"] = sent_at

                repo = BaseRepository(self.table_name)
                message_id = await repo.insert(conn, data)
                logger.info(f"Inserted chat message with id {message_id}")
                return message_id
        except Exception as e:
            logger.error(f"Failed to insert chat message: {e}")
            raise

    async def get_chat_history(
        self,
        user_id: int,
        limit: int = 5,
        offset: int = 0
        ) -> list:
        """
        Retrieve chat history between USER and AGENT for a given user_id.

        Args:
            user_id: ID of the user (telegram_id).
            limit: Number of messages to retrieve (default: 5).
            offset: Number of messages to skip (default: 0).

        Returns:
            List of chat messages sorted by sent_at descending.
        """
        try:
            async with DatabaseConnection() as conn:
                users_db = UsersRepository()
                # Get internal user_id from telegram_id
                internal_user_id = await users_db.get_internal_user_id(conn=conn, telegram_id=user_id)
                if internal_user_id is None:
                    logger.warning(f"No user found for telegram_id {user_id}")
                    return []

                repo = BaseRepository(self.table_name)
                query = (
                    f"SELECT * FROM {self.table_name} "
                    "WHERE user_id = %s AND role IN ('USER', 'AGENT') "
                    "ORDER BY sent_at DESC "
                    "LIMIT %s OFFSET %s"
                )
                params = (internal_user_id, limit, offset)
                rows = await repo.fetch_all(conn, query, params)
                logger.info(f"Retrieved {len(rows)} chat messages for user_id {user_id}")
                return rows
        except Exception as e:
            logger.error(f"Failed to retrieve chat history: {e}")
            raise
