from utils.logger import logger
from typing import Optional
from datetime import datetime
from database.connection import DatabaseConnection


class UsersRepository:
    def __init__(self):
        self.table_name = "users"

    async def insert_user(
        self,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        telegram_id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ) -> int:
        """
        Insert a new user into the users table after checking for existing user.

        Returns:
            The inserted or existing user_id.
        """

        if not telegram_id and not email:
            raise ValueError("At least one of 'telegram_id' or 'email' must be provided.")

        if not full_name or not full_name.strip():
            full_name = f'{telegram_id}@TELEGRAM' if telegram_id else 'Anonymous'
        full_name_clean = full_name.strip()

        if not email or not email.strip():
            email_clean = f"{full_name_clean.replace(' ', '').lower()}@gmail.com"
            logger.warning(f"Email is empty, using generated email: {email_clean}")
        else:
            email_clean = email.strip()

        # Check if user exists
        check_sql = f"""
            SELECT user_id FROM {self.table_name}
            WHERE email = $1 { 'OR telegram_id = $2' if telegram_id else '' }
        """

        check_params = [email_clean]
        if telegram_id:
            check_params.append(str(telegram_id))

        # Build insert query dynamically
        columns = ["full_name", "email"]
        values = [full_name_clean, email_clean]

        if phone:
            columns.append("phone")
            values.append(phone.strip())
        if telegram_id:
            columns.append("telegram_id")
            values.append(str(telegram_id))
        if created_at:
            columns.append("created_at")
            values.append(created_at)

        placeholders = [f"${i+1}" for i in range(len(values))]
        insert_sql = f"""
            INSERT INTO {self.table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING user_id
        """

        try:
            async with DatabaseConnection() as conn:
                logger.info("Checking if user already exists...")
                result = await conn.fetchrow(check_sql, *check_params)
                if result:
                    user_id = result["user_id"]
                    logger.info(f"User already exists with id {user_id}")
                    return user_id

                logger.info("Inserting new user...")
                result = await conn.fetchrow(insert_sql, *values)
                if not result:
                    logger.error("Insert did not return user_id")
                    raise ValueError("Insert failed")
                user_id = result["user_id"]
                logger.info(f"Inserted user with id {user_id}")
                return user_id

        except Exception as e:
            logger.error(f"Failed to insert user: {e}", exc_info=True)
            raise