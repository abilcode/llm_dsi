# agents/complaint_agent.py
import json
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.schema import SystemMessage
from langchain.chat_models import ChatOpenAI
from tools.complaint_tools import complaint_tools
from langchain.schema import AIMessage, HumanMessage


class ComplaintAgentWrapper:
    def __init__(self):
        # Load few-shot examples
        try:
            with open('agents/few_shot/complaint_few_shot.json', 'r') as f:
                complaint_examples = json.load(f)
            formatted_examples = ""
            for item in complaint_examples:
                formatted_examples += f"""
                Pengguna: {item['user_input']}
                Agen: {item['expected_response']}
                """
        except FileNotFoundError:
            formatted_examples = ""

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""Kamu adalah agen spesialis keluhan untuk sistem manajemen guest house.

Skema basis data untuk keluhan:
- complaints(complaint_id, guest_name, room_id, description, status, created_at)

Tugas utama kamu:
- Membantu tamu menyimpan keluhan mereka ke database
- Meminta informasi yang diperlukan jika ada yang kurang (nama tamu, room_id, deskripsi keluhan)
- Memberikan konfirmasi setelah keluhan berhasil disimpan
- Melihat status keluhan yang sudah ada

PENTING - Format untuk menyimpan keluhan:
- Gunakan tool save_complaint dengan format: "guest_name|room_id|description"
- Contoh: "Nabil|2|Genteng bocor"
- Untuk update status: gunakan format "complaint_id|status"

Peraturan penting yang harus selalu kamu patuhi:
- Selalu jawab dalam bahasa Indonesia, jangan gunakan bahasa Inggris.
- Bersikap ramah dan memahami keluhan tamu.
- Pastikan semua informasi yang diperlukan lengkap sebelum menyimpan ke database.
- Jika informasi kurang, tanyakan dengan sopan kepada tamu.
- Saat menyimpan keluhan, gabungkan semua informasi dengan format yang benar menggunakan separator "|"

Informasi yang diperlukan untuk keluhan:
1. Nama tamu (guest_name)
2. ID/nomor kamar (room_id) 
3. Deskripsi keluhan (description)

Contoh percakapan:
{formatted_examples}
"""),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        llm = ChatOpenAI(model="gpt-4.1", temperature=0)
        agent = OpenAIFunctionsAgent(llm=llm, prompt=prompt, tools=complaint_tools)
        self.executor = AgentExecutor(agent=agent, tools=complaint_tools, verbose=True)
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
            return f"Maaf, terjadi kesalahan: {e}"

    def run(self, user_input: str) -> str:
        return self.ask(user_input)