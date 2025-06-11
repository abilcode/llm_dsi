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
    def __init__(self):
        pass

    async def insert(self, conn, query: str, *args):
        """
        Execute an INSERT SQL statement.

        Args:
            conn: The asyncpg connection object.
            query (str): The SQL INSERT query.
            *args: Parameters for the query.

        Returns:
            The inserted record.
        """
        try:
            result = await conn.fetchrow(query, *args)
            logger.info(f"Insert executed: {query} | Params: {args} | Result: {result}")
            return result
        except Exception as e:
            logger.error(f"Insert failed: {e} | Query: {query} | Params: {args}")
            raise

    async def delete(self, conn, query: str, *args):
        """
        Execute a DELETE SQL statement.

        Args:
            conn: The asyncpg connection object.
            query (str): The SQL DELETE query.
            *args: Parameters for the query.

        Returns:
            The deleted record.
        """
        try:
            result = await conn.fetchrow(query, *args)
            logger.info(f"Delete executed: {query} | Params: {args} | Result: {result}")
            return result
        except Exception as e:
            logger.error(f"Delete failed: {e} | Query: {query} | Params: {args}")
            raise

    async def select_one(self, conn, query: str, *args):
        """
        Execute a SELECT SQL statement to fetch a single record.

        Args:
            conn: The asyncpg connection object.
            query (str): The SQL SELECT query.
            *args: Parameters for the query.

        Returns:
            The first matching record or None.
        """
        try:
            result = await conn.fetchrow(query, *args)
            logger.info(f"Select one executed: {query} | Params: {args} | Result: {result}")
            return result
        except Exception as e:
            logger.error(f"Select one failed: {e} | Query: {query} | Params: {args}")
            raise

    async def fetch_all(self, conn, query: str, *args):
        """
        Execute a SELECT SQL statement to fetch all matching records.

        Args:
            conn: The asyncpg connection object.
            query (str): The SQL SELECT query.
            *args: Parameters for the query.

        Returns:
            List of records matching the query.
        """
        try:
            results = await conn.fetch(query, *args)
            logger.info(f"Fetch all executed: {query} | Params: {args} | Records: {len(results)}")
            return results
        except Exception as e:
            logger.error(f"Fetch all failed: {e} | Query: {query} | Params: {args}")
            raise

    async def update(self, conn, query: str, *args):
        """
        Execute an UPDATE SQL statement.

        Args:
            conn: The asyncpg connection object.
            query (str): The SQL UPDATE query.
            *args: Parameters for the query.

        Returns:
            The updated record.
        """
        try:
            result = await conn.fetchrow(query, *args)
            logger.info(f"Update executed: {query} | Params: {args} | Result: {result}")
            return result
        except Exception as e:
            logger.error(f"Update failed: {e} | Query: {query} | Params: {args}")
            raise

    async def execute_query(self, conn, query: str, *args):
        """
        Execute a custom SQL query.

        Args:
            conn: The asyncpg connection object.
            query (str): The SQL query to execute.
            *args: Parameters for the query.

        Returns:
            Query result.
        """
        try:
            result = await conn.fetch(query, *args)
            logger.info(f"Custom query executed: {query} | Params: {args} | Result: {result}")
            return result
        except Exception as e:
            logger.error(f"Custom query execution failed: {e} | Query: {query} | Params: {args}")
            raise

from databases import Database
database = Database(os.getenv("DATABASE_URL", ""))
