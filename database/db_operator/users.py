from utils.logger import logger
from typing import Any, Dict
from datetime import datetime
from database.connection import BaseRepository, DatabaseConnection

class UsersRepository:
    def __init__(self):
        self.table_name = "users"

    async def insert_user(
        self,
        full_name: str = None,
        email: str = None,
        phone: str = None,
        telegram_id: str = None,
        created_at: datetime = None
    ) -> int:
        """
        Insert a new user into the users table.

        Args:
            full_name: Full name of the user.
            email: Email address (must be unique and not null).
            phone: Phone number (optional).
            telegram_id: Telegram ID (optional).
            created_at: Optional datetime for when the user was created.

        Returns:
            The inserted user_id.
        """
        # Validate and process inputs
        if not full_name or not full_name.strip():
            full_name = f'{telegram_id}@TELEGRAM'
        full_name_clean = full_name.strip()

        # If email is empty, generate from full_name
        if not email or not email.strip():
            email_clean = f"{full_name_clean.replace(' ', '').lower()}@gmail.com"
            logger.warning(f"Email is empty, using generated email: {email_clean}")
        else:
            email_clean = email.strip()

        data: Dict[str, Any] = {
            "full_name": full_name_clean,
            "email": email_clean
        }
        if phone:
            data["phone"] = phone.strip()
        if telegram_id:
            data["telegram_id"] = telegram_id.strip()
        if created_at:
            data["created_at"] = created_at

        try:
            async with DatabaseConnection() as conn:
                repo = BaseRepository(self.table_name)
                user_id = await repo.insert(conn, data)
                logger.info(f"Inserted user with id {user_id}")
                return user_id
        except Exception as e:
            logger.error(f"Failed to insert user: {e}")
            raise
