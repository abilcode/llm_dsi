import os
import asyncpg
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

class DatabaseConnection:
    def __init__(self, dsn=DATABASE_URL):
        self.dsn = dsn
        self.conn = None

    async def __aenter__(self):
        try:
            self.conn = await asyncpg.connect(self.dsn)
            logger.info("Successfully connected to PostgreSQL database.")
            return self.conn
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    async def __aexit__(self, exc_type, exc, tb):
        if self.conn:
            await self.conn.close()
            logger.info("Database connection closed.")

class BaseRepository:
    def __init__(self, table_name):
        self.table_name = table_name

    async def insert(self, conn, data: dict):
        try:
            columns = ', '.join(data.keys())
            values = ', '.join(f'${i+1}' for i in range(len(data)))
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({values}) RETURNING *"
            result = await conn.fetchrow(query, *data.values())
            logger.info(f"Inserted into {self.table_name}: {result}")
            return result
        except Exception as e:
            logger.error(f"Insert failed: {e}")
            raise

    async def delete(self, conn, id_column, id_value):
        try:
            query = f"DELETE FROM {self.table_name} WHERE {id_column} = $1 RETURNING *"
            result = await conn.fetchrow(query, id_value)
            logger.info(f"Deleted from {self.table_name}: {result}")
            return result
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            raise

    async def select_one(self, conn, id_column, id_value):
        try:
            query = f"SELECT * FROM {self.table_name} WHERE {id_column} = $1"
            result = await conn.fetchrow(query, id_value)
            logger.info(f"Selected one from {self.table_name}: {result}")
            return result
        except Exception as e:
            logger.error(f"Select one failed: {e}")
            raise

    async def fetch_all(self, conn):
        try:
            query = f"SELECT * FROM {self.table_name}"
            results = await conn.fetch(query)
            logger.info(f"Fetched all from {self.table_name}: {len(results)} records")
            return results
        except Exception as e:
            logger.error(f"Fetch all failed: {e}")
            raise

    async def update(self, conn, id_column, id_value, data: dict):
        try:
            set_clause = ', '.join(f"{k} = ${i+2}" for i, k in enumerate(data.keys()))
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE {id_column} = $1 RETURNING *"
            params = [id_value] + list(data.values())
            result = await conn.fetchrow(query, *params)
            logger.info(f"Updated {self.table_name}: {result}")
            return result
        except Exception as e:
            logger.error(f"Update failed: {e}")
            raise

from databases import Database
database = Database(os.getenv("DATABASE_URL", ""))
