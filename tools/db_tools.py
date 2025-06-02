from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.schema import SystemMessage
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from pydantic.v1 import BaseModel
from typing import List
import sqlite3
import pandas as pd

# === Better DB tools implemented inline here ===
conn = sqlite3.connect("guest_rooms.db")

def list_tables():
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    rows = c.fetchall()
    return "\n".join(row[0] for row in rows if row[0] is not None)

def describe_tables(table_names: List[str]):
    c = conn.cursor()
    tables = ', '.join("'" + table + "'" for table in table_names)
    rows = c.execute(f"SELECT sql FROM sqlite_master WHERE type='table' and name IN ({tables});")
    return '\n'.join(row[0] for row in rows if row[0] is not None)

def run_sqlite_query(query: str):
    c = conn.cursor()
    try:
        c.execute(query)
        return c.fetchall()
    except sqlite3.OperationalError as e:
        return f"Terjadi error saat menjalankan query: {str(e)}"

def pandas_sqlite_query(query: str):
    try:
        c = conn.cursor()
        c.execute(query)
        data = c.fetchall()
        col_names = [desc[0] for desc in c.description]
        df = pd.DataFrame(data, columns=col_names)
        return df
    except sqlite3.OperationalError as e:
        return f"Terjadi error saat menjalankan query Pandas: {str(e)}"

# === Tool schemas ===
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
        description="Gunakan ini untuk menampilkan semua nama tabel di database.",
        func=list_tables,
    ),
    Tool.from_function(
        name="describe_tables",
        description="Berikan daftar nama tabel, kembalikan definisi skema SQL dari tabel-tabel tersebut.",
        func=describe_tables,
        args_schema=DescribeTablesArgsSchema
    ),
    Tool.from_function(
        name="run_sqlite_query",
        description="Jalankan query SQL biasa untuk mendapatkan data dari database.",
        func=run_sqlite_query,
        args_schema=RunQueryArgsSchema
    ),
    Tool.from_function(
        name="pandas_sqlite_query",
        description="Gunakan ini saat pengguna menyebut Pandas atau meminta data dalam bentuk tabel/visualisasi.",
        func=pandas_sqlite_query,
        args_schema=PandasQueryArgsSchema
    ),
]