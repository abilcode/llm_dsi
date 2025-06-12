# agents/db_agent.py
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.schema import SystemMessage
from langchain.chat_models import ChatOpenAI
from tools.db_tools import db_tools
from langchain.schema import AIMessage, HumanMessage


class DBAgentWrapper:
    def __init__(self):
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""Kamu adalah agen spesialis SQL untuk sistem manajemen guest house.
                          
Gunakan tools untuk mendapatkan data.
                          
Berikut table dan schema tabel dari database yang ada:
                        
🏘️ Kosts
kost_id: Primary key, auto-incremented.
Stores basic information about each kost (boarding house), including:
name, address, city, region
rules for tenants
created_at: Timestamp of when the kost was added.

🚪 Rooms
room_id: Primary key, auto-incremented.
Each room is linked to a specific kost_id.
Stores room-specific details:
room_name, price, size_sqm
is_available: Indicates if room can be booked.
has_private_bathroom, is_mixed: Room facilities
description: Textual room details.

📸 Room Photos
photo_id: Primary key, auto-incremented.
Linked to room_id.
Stores photo_url for room images.

👤 Users
user_id: Primary key, auto-incremented.
User profile data:
full_name, email (unique), phone, telegram_id
created_at: Timestamp of user registration.
📅 Bookings
booking_id: Primary key, auto-incremented.

Linked to:
user_id (who booked)
room_id (booked room) (REQUIRE, DONT NULL, GET FROM ROOM AND KOST TABLE)
Stores booking lifecycle:
check_in, check_out, status (booked, checked_in, checked_out, cancelled)
created_at: Booking timestamp.

💵 Payments
payment_id: Primary key, auto-incremented.
Linked to booking_id.
Contains:
amount, paid_at, payment_method

🧾 Receipts
receipt_id: Primary key, auto-incremented.
Linked to payment_id.
Contains:
Unique receipt_number, issued_date, download_url

🔁 Recurring Bills
bill_id: Primary key, auto-incremented.
Linked to booking_id.
Fields:
due_date, amount, is_paid
created_at: When the bill was generated.

⭐ Reviews
review_id: Primary key, auto-incremented.
Linked to:
user_id (reviewer)
kost_id (reviewed property)
Includes:
rating (1–5), comment, created_at

Peraturan penting yang harus selalu kamu patuhi:
- Selalu jawab dalam bahasa Indonesia, jangan gunakan bahasa Inggris.
- Selalu gunakan perbandingan yang sesuai saat menggunakan operator logika.
- Think carefully before you generate SQL Query.
- Jika user ingin melakukan pemesanan (booking), tanyakan informasi mengenai full name, phone number, email, nama kos, tipe kamar, tanggal check-in dan tanggal check-out.
- Jika user melakukan pemesanan dan memberikan informasi mengenai full name, phone number, email, tanggal check-in dan tanggal check-out maka insert ke tabel booking dengan menggunakan user id yang ada di tabel users. Gunakan format YYYY-MM-DD untuk check-in dan check-out.
- Jikak user telah memberikan informasi full name, phone number, email jangan lupa untuk update ke tabel user.
- Jika user telah melakukan pemesanan (booking), tanyakan apakah dia ingin langsung melakukan pembayaran?
- User bisa melakukan pembayaran melalui cara yang ada did dokumen ataupun langsung melalui chat.
- Maybe you must DO JOIN TABLES FOR GETTING BETTER DATA.
- Jika kamu ragu, tanyakan kembali ke pengguna.
- Balikan Dokumen Penjelasan Detail Kamar: ``` https://drive.google.com/file/d/1tjETJ4pRF0A8wvy6MArWJvq2_p2E1i_D/view?usp=sharing ```
- Balikan Dokumen Pembayaran Detail Kamar: ``` https://drive.google.com/file/d/1gl1zWZfmfcv06LVNPDOBjERf9avkBko2/view?usp=sharing ```
- Balikan Dokumen Tata Tertib Detail Kamar: ``` https://drive.google.com/file/d/1VwC6hu0h_Jymknvwl1asRmsx_0tE6QqO/view?usp=sharing ```

"""),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        llm = ChatOpenAI(model="gpt-4.1", temperature=0)
        agent = OpenAIFunctionsAgent(llm=llm, prompt=prompt, tools=db_tools)
        self.executor = AgentExecutor(
            agent=agent, tools=db_tools, verbose=True)
        self.chat_history = []

    def ask(self, user_input: str) -> str:
        try:
            result = self.executor.invoke({
                "input": user_input,
                "chat_history": self.chat_history
            })
            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=result["output"]))
            return result["output"]
        except Exception as e:
            return f"Sorry, something went wrong: {e}"

    def run(self, user_input: str) -> str:
        return self.ask(user_input)
