from langchain.tools import Tool
from pydantic.v1 import BaseModel
from typing import List
import psycopg2
from database.connection import DATABASE_URL

class DatabaseConnection:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.autocommit = True

    def __enter__(self):
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

def list_tables(show=None):
    with DatabaseConnection() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' AND table_type='BASE TABLE';
        """)
        rows = cursor.fetchall()
        return "\n".join(row[0] for row in rows)

def describe_tables(table_names: List[str]):
    if not table_names:
        return "No tables provided."

    descriptions = []
    with DatabaseConnection() as cursor:
        for table in table_names:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s;
            """, (table,))
            rows = cursor.fetchall()
            schema = f"Table: {table}\n"
            for row in rows:
                column_name, data_type, is_nullable, column_default = row
                schema += f"  {column_name}: {data_type}, Nullable: {is_nullable}, Default: {column_default}\n"
            descriptions.append(schema)
    return "\n\n".join(descriptions)

def run_pg_query(query: str):
    with DatabaseConnection() as cursor:
        try:
            cursor.execute(query)
            try:
                rows = cursor.fetchall()
                return rows if rows else "Query executed successfully."
            except psycopg2.ProgrammingError:
                # No results to fetch (e.g., INSERT/UPDATE)
                return "Query executed successfully."
        except Exception as e:
            return f"Error running query: {str(e)}"

# === Tool schemas ===
class ListTablesArgsSchema(BaseModel):
    pass

class RunQueryArgsSchema(BaseModel):
    query: str


class DescribeTablesArgsSchema(BaseModel):
    table_names: List[str]


class PandasQueryArgsSchema(BaseModel):
    query: str


# === Tools ===
db_tools = [
    Tool.from_function(
        name="list_tables",
        description="Gunakan ini untuk menampilkan semua nama tabel di database. Tidak ada argument di function ini.",
        func=list_tables,
        args_schema=ListTablesArgsSchema
    ),
    Tool.from_function(
        name="describe_tables",
        description="Berikan daftar nama tabel, kembalikan definisi skema SQL dari tabel-tabel tersebut.",
        func=describe_tables,
        args_schema=DescribeTablesArgsSchema
    ),
    Tool.from_function(
        name="run_pg_query",
        description="Jalankan query SQL biasa untuk mendapatkan data dari database.",
        func=run_pg_query,
        args_schema=RunQueryArgsSchema
    )
]
