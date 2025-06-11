from utils.logger import logger
from typing import Any, Dict, List
from datetime import datetime
from database.connection import DatabaseConnection
from database.db_operator.users import UsersRepository
from typing import Optional

class ChatRepository:
    def __init__(self):
        self.table_name = "messages"

    async def insert_chat(
        self,
        user_id: int,
        chat_type: str,
        role: str,
        chat: str,
        sent_at: Optional[datetime] = None
    ) -> int:
        """
        Insert a chat message into the messages table.

        Args:
            user_id: Telegram user ID.
            chat_type: 'IN' (incoming) or 'OUT' (outgoing).
            role: 'AGENT' or 'USER'.
            chat: Chat message content.
            sent_at: Optional timestamp.

        Returns:
            Inserted message_id.
        """
        users_db = UsersRepository()

        if chat_type not in ('IN', 'OUT'):
            raise ValueError("chat_type must be 'IN' or 'OUT'")
        if role not in ('AGENT', 'USER'):
            raise ValueError("role must be 'AGENT' or 'USER'")
        if not chat:
            raise ValueError("chat cannot be empty")

        try:
            async with DatabaseConnection() as conn:
                internal_user_id = await users_db.insert_user(telegram_id=user_id)

                query = f"""
                    INSERT INTO {self.table_name} (user_id, chat_type, role, chat, sent_at)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING message_id
                """

                # Use current time if sent_at is not provided
                sent_at = sent_at or datetime.utcnow()

                logger.info(f"Inserting chat: user_id={internal_user_id}, chat_type={chat_type}, role={role}")

                result = await conn.fetchrow(query, internal_user_id, chat_type, role, chat, sent_at)

                message_id = result["message_id"] if result else None
                logger.info(f"Inserted chat message with id: {message_id}")
                return message_id

        except Exception as e:
            logger.error(f"Error inserting chat message: {e}")
            raise

    async def get_chat_history(
        self,
        user_id: int,
        limit: int = 5,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
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
                internal_user_id = await users_db.get_internal_user_id(conn=conn, telegram_id=user_id)
                if internal_user_id is None:
                    logger.warning(f"No user found for telegram_id {user_id}")
                    return []

                sql = (
                    f"SELECT * FROM {self.table_name} "
                    "WHERE user_id = %s AND role IN ('USER', 'AGENT') "
                    "ORDER BY sent_at DESC "
                    "LIMIT %s OFFSET %s"
                )
                params = (internal_user_id, limit, offset)
                async with conn.cursor() as cur:
                    await cur.execute(sql, params)
                    columns = [desc[0] for desc in cur.description]
                    rows = await cur.fetchall()
                    result = [dict(zip(columns, row)) for row in rows]
                logger.info(f"Retrieved {len(result)} chat messages for user_id {user_id}")
                return result
        except Exception as e:
            logger.error(f"Failed to retrieve chat history: {e}")
            raise
