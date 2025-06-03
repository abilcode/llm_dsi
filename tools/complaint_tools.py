# agents/complaint_tools.py

import sqlite3
import pandas as pd
from langchain.tools import Tool
from pydantic.v1 import BaseModel
from datetime import datetime

# === DB Connection ===
conn = sqlite3.connect("guest_rooms.db")

# === Core Functions ===
def list_complaints():
    query = "SELECT complaint_id, guest_name, room_id, description, status, created_at FROM complaints ORDER BY created_at DESC"
    return pd.read_sql_query(query, conn).to_string(index=False)

def add_complaint(guest_name: str, room_id: int, description: str):
    try:
        c = conn.cursor()
        created_at = datetime.now().isoformat()
        status = "open"
        c.execute('''
                    INSERT INTO complaints (guest_name, room_id, description, status, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (guest_name, room_id, description, status, created_at))

        conn.commit()
        complaint_id = c.lastrowid  # Ambil ID otomatis
        conn.close()
        return "Komplain berhasil ditambahkan."
    except Exception as e:
        return f"Gagal menambahkan komplain: {e}"

def update_complaint_status(complaint_id: int, status: str):
    try:
        c = conn.cursor()
        c.execute(
            "UPDATE complaints SET status = ? WHERE complaint_id = ?",
            (status, complaint_id)
        )
        conn.commit()
        return "Status komplain berhasil diperbarui."
    except Exception as e:
        return f"Gagal memperbarui status: {e}"

# === Argument Schemas ===
class AddComplaintArgs(BaseModel):
    guest_name: str
    room_id: int
    description: str

class UpdateStatusArgs(BaseModel):
    complaint_id: int
    status: str

# === Tool Definitions ===
complaint_tools = [
    Tool.from_function(
        name="list_complaints",
        description="Lihat semua komplain dari tamu.",
        func=list_complaints,
    ),
    Tool.from_function(
        name="add_complaint",
        description="Tambahkan komplain baru dari tamu.",
        func=add_complaint,
        args_schema=AddComplaintArgs,
    ),
    Tool.from_function(
        name="update_complaint_status",
        description="Perbarui status komplain (contoh: open, in progress, closed).",
        func=update_complaint_status,
        args_schema=UpdateStatusArgs,
    ),
]
