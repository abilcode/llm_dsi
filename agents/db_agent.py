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


def create_db_agent():
    """Create database query agent with schema awareness"""
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessage(content="""Kamu adalah agen spesialis SQL untuk sistem manajemen guest house.
            
            Skema basis data:
            - rooms(room_id, level, height, availability, room_type)
            - levels(level_id, level_name, description)
            - room_types(type_id, type_name, base_rate, max_occupancy)
            
            Peraturan penting yang harus selalu kamu patuhi:
            - Selalu jawab dalam bahasa Indonesia, jangan gunakan bahasa Inggris.
            - Selalu gunakan perbandingan teks dengan operator `LIKE`, jangan gunakan `=`.
            - Pastikan nilai teks yang digunakan dalam filter dikonversi menjadi huruf kecil (misalnya, 'Standard' menjadi 'standard').
            - Selalu periksa sintaks SQL sebelum menjalankan kueri.
            - Jangan pernah mengubah atau menghapus seluruh tabel.
            - Untuk kueri yang kompleks, pecah menjadi beberapa bagian jika perlu untuk kejelasan dan akurasi.
            
            Contoh kueri yang benar:
            ```sql
            SELECT * FROM rooms WHERE room_type LIKE 'standard' COLLATE NOCASE;

            """),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ]
    )

    agent = OpenAIFunctionsAgent(
        llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
        prompt=prompt,
        tools=db_tools
    )

    return AgentExecutor(
        agent=agent,
        tools=db_tools,
        verbose=True,
        handle_parsing_errors=True
    )