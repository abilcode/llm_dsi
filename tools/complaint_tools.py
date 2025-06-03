from langchain.tools import Tool
from pydantic.v1 import BaseModel
from typing import Optional
import sqlite3
import pandas as pd
from datetime import datetime

# Database connection
conn = sqlite3.connect("guest_rooms.db")


def create_complaints_table():
    """Create complaints table if it doesn't exist"""
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT,
            room_id TEXT,
            description TEXT NOT NULL,
            status TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()


# Initialize table
create_complaints_table()


def save_complaint(complaint_data: str):
    """Save a new complaint to the database
    Expected format: 'guest_name|room_id|description'
    """
    try:
        parts = complaint_data.split('|')
        if len(parts) != 3:
            return "Format data tidak valid. Gunakan format: guest_name|room_id|description"

        guest_name, room_id, description = parts

        c = conn.cursor()
        c.execute('''
            INSERT INTO complaints (guest_name, room_id, description, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (guest_name.strip(), room_id.strip(), description.strip(), 'Pending', datetime.now()))
        conn.commit()
        complaint_id = c.lastrowid
        return f"Keluhan berhasil disimpan dengan ID: {complaint_id}. Tim pengelola akan segera menangani keluhan Anda."
    except sqlite3.Error as e:
        return f"Terjadi kesalahan saat menyimpan keluhan: {str(e)}"
    except Exception as e:
        return f"Terjadi kesalahan dalam memproses data: {str(e)}"


def get_complaint_by_id(complaint_id_str: str):
    """Get complaint details by ID"""
    try:
        complaint_id = int(complaint_id_str.strip())
        c = conn.cursor()
        c.execute('''
            SELECT complaint_id, guest_name, room_id, description, status, created_at
            FROM complaints WHERE complaint_id = ?
        ''', (complaint_id,))
        result = c.fetchone()
        if result:
            return {
                'complaint_id': result[0],
                'guest_name': result[1],
                'room_id': result[2],
                'description': result[3],
                'status': result[4],
                'created_at': result[5]
            }
        else:
            return "Keluhan dengan ID tersebut tidak ditemukan."
    except ValueError:
        return "ID keluhan harus berupa angka."
    except sqlite3.Error as e:
        return f"Terjadi kesalahan saat mengambil data keluhan: {str(e)}"


def get_complaints_by_user(guest_name: str):
    """Get all complaints by guest name"""
    try:
        guest_name = guest_name.strip()
        c = conn.cursor()
        c.execute('''
            SELECT complaint_id, room_id, description, status, created_at
            FROM complaints WHERE guest_name = ?
            ORDER BY created_at DESC
        ''', (guest_name,))
        results = c.fetchall()
        if results:
            complaints = []
            for row in results:
                complaints.append({
                    'complaint_id': row[0],
                    'room_id': row[1],
                    'description': row[2],
                    'status': row[3],
                    'created_at': row[4]
                })
            return complaints
        else:
            return f"Tidak ada keluhan ditemukan untuk tamu: {guest_name}"
    except sqlite3.Error as e:
        return f"Terjadi kesalahan saat mengambil data keluhan: {str(e)}"


def get_all_complaints():
    """Get all complaints with pagination"""
    try:
        c = conn.cursor()
        c.execute('''
            SELECT complaint_id, guest_name, room_id, description, status, created_at
            FROM complaints
            ORDER BY created_at DESC
            LIMIT 20
        ''')
        results = c.fetchall()
        if results:
            complaints = []
            for row in results:
                complaints.append({
                    'complaint_id': row[0],
                    'guest_name': row[1],
                    'room_id': row[2],
                    'description': row[3],
                    'status': row[4],
                    'created_at': row[5]
                })
            return complaints
        else:
            return "Belum ada keluhan yang terdaftar."
    except sqlite3.Error as e:
        return f"Terjadi kesalahan saat mengambil data keluhan: {str(e)}"


def update_complaint_status(status_data: str):
    """Update complaint status
    Expected format: 'complaint_id|status'
    """
    try:
        parts = status_data.split('|')
        if len(parts) != 2:
            return "Format data tidak valid. Gunakan format: complaint_id|status"

        complaint_id = int(parts[0].strip())
        status = parts[1].strip()

        c = conn.cursor()
        c.execute('''
            UPDATE complaints 
            SET status = ?
            WHERE complaint_id = ?
        ''', (status, complaint_id))
        conn.commit()

        if c.rowcount > 0:
            return f"Status keluhan ID {complaint_id} berhasil diubah menjadi: {status}"
        else:
            return f"Keluhan dengan ID {complaint_id} tidak ditemukan."
    except ValueError:
        return "ID keluhan harus berupa angka."
    except sqlite3.Error as e:
        return f"Terjadi kesalahan saat mengupdate status keluhan: {str(e)}"


# Tool schemas - Remove the schemas since we're using string input
# class SaveComplaintSchema(BaseModel):
#     user_name: str
#     room_number: str
#     complaint_type: str
#     description: str

# class GetComplaintByIdSchema(BaseModel):
#     complaint_id: int

# class GetComplaintsByUserSchema(BaseModel):
#     user_name: str

# class UpdateComplaintStatusSchema(BaseModel):
#     complaint_id: int
#     status: str

# Tools
complaint_tools = [
    Tool.from_function(
        name="save_complaint",
        description="Simpan keluhan baru ke database. Format input: 'guest_name|room_id|description'. Contoh: 'John Doe|101|AC tidak dingin'",
        func=save_complaint,
    ),
    Tool.from_function(
        name="get_complaint_by_id",
        description="Ambil detail keluhan berdasarkan ID keluhan. Input: ID keluhan (angka).",
        func=get_complaint_by_id,
    ),
    Tool.from_function(
        name="get_complaints_by_user",
        description="Ambil semua keluhan dari tamu tertentu berdasarkan nama. Input: nama tamu.",
        func=get_complaints_by_user,
    ),
    Tool.from_function(
        name="get_all_complaints",
        description="Ambil semua keluhan yang ada (maksimal 20 keluhan terbaru).",
        func=get_all_complaints,
    ),
    Tool.from_function(
        name="update_complaint_status",
        description="Update status keluhan. Format input: 'complaint_id|status'. Contoh: '1|Resolved'",
        func=update_complaint_status,
    ),
]