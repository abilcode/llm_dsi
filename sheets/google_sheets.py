import os
from typing import Any, Dict, List
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from gspread_formatting import CellFormat, Color, format_cell_range

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

load_dotenv()

service_account_info = {
    "type": "service_account",
    "project_id": os.getenv("SHEETS_SERVICE_ACCOUNT_PROJECT_ID"),
    "private_key_id": os.getenv("SHEETS_SERVICE_ACCOUNT_PRIVATE_KEY_ID"),
    "private_key": os.getenv("SHEETS_SERVICE_ACCOUNT_PRIVATE_KEY", "").replace("\\n", "\n"),
    "client_email": os.getenv("SHEETS_SERVICE_ACCOUNT_CLIENT_EMAIL"),
    "client_id": os.getenv("SHEETS_SERVICE_ACCOUNT_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/pak-kos%40playground-461814.iam.gserviceaccount.com"
}
credentials = Credentials.from_service_account_info(
    service_account_info,
    scopes=SCOPES
)
gc = gspread.authorize(credentials)

SPREADSHEET_ID = "1wVXA5nGxWwkjb3yEqQIohshgIEG0-pH0NQvgomnEdsA"
SHEET_NAME = "Sheet1"

GREEN = CellFormat(backgroundColor=Color(0.0, 1.0, 0.0))
RED = CellFormat(backgroundColor=Color(1.0, 0.0, 0.0))

room_id_to_cell = {
    "1": "B6",
    "2": "C6",
    "3": "E5",
    "4": "H4",
}


def update_room_colors_in_sheet(
    room_availability: List[Dict[str, Any]],
):
    sh = gc.open_by_key(SPREADSHEET_ID)
    worksheet = sh.worksheet(SHEET_NAME)

    for room in room_availability:
        print(room)
        room_id = room.get("room_id")
        is_available = room.get("is_available")

        if room_id is None or is_available is None:
            print(f"Skipping invalid room entry: {room}")
            continue

        cell = room_id_to_cell.get(room_id)
        if not cell:
            print(f"No cell mapping found for room_id {room_id}, skipping.")
            continue

        color = GREEN if is_available else RED

        try:
            format_cell_range(worksheet, cell, color)
        except Exception as e:
            print(f"Error updating cell {cell} for room {room_id}: {e}")
