# tools/db_tools.py
import sqlite3
from typing import List, Tuple, Any
from langchain.tools import Tool


class DatabaseManager:
    def __init__(self, db_path: str = 'guest_rooms.db'):
        self.db_path = db_path

    def execute_query(self, query: str) -> str:
        """Execute SQL query and return formatted results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)

                if query.strip().upper().startswith('SELECT'):
                    # Get column names
                    columns = [desc[0] for desc in cursor.description]
                    # Fetch all rows
                    rows = cursor.fetchall()
                    # Format results
                    result = "\n".join(
                        [f"{col}: {val}" for row in rows for col, val in zip(columns, row)]
                    )
                    return result or "No results found"
                else:
                    conn.commit()
                    return f"Success: {cursor.rowcount} rows affected"
        except sqlite3.Error as e:
            return f"Database error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"


# Initialize the database manager
db_manager = DatabaseManager()

# Create the tool
db_tools = [
    Tool(
        name="DatabaseQuery",
        func=db_manager.execute_query,
        description="""Useful for querying SQL databases. 
        Input must be a valid SQL query. 
        For rooms database, available tables are: rooms, levels, room_types
        """
    )
]