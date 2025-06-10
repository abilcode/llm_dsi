import json
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.schema import SystemMessage
from langchain.chat_models import ChatOpenAI
from tools.transaction_tools import transaction_tools
from langchain.schema import AIMessage, HumanMessage


class TransactionAgentWrapper:
    def __init__(self):
        # Load few-shot examples (you can create this JSON file for better responses)
        try:
            with open('agents/few_shot/transaction_few_shot.json', 'r') as f:
                transaction_examples = json.load(f)
            formatted_examples = ""
            for item in transaction_examples:
                formatted_examples += f"""
                Pengguna: {item['user_input']}
                Agen: {item['expected_response']}
                """
        except FileNotFoundError:
            formatted_examples = """
            Pengguna: Saya mau bayar sewa bulan ini
            Agen: Baik, saya akan membantu Anda melakukan pembayaran sewa. Untuk memproses pembayaran, saya perlu informasi berikut:
            1. Nama lengkap Anda
            2. Nomor kamar
            3. Metode pembayaran yang dipilih (Transfer Bank, Cash, dll)

            Pengguna: Nama saya Budi, kamar 101, mau transfer bank
            Agen: Terima kasih informasinya, Pak Budi. Saya akan cek tagihan Anda untuk kamar 101. [checks bills and processes payment]

            Pengguna: Cek tagihan saya dong
            Agen: Tentu, saya akan mengecek tagihan Anda. Bisa tolong berikan nama lengkap untuk pencarian tagihan?
            """

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""Kamu adalah agen spesialis transaksi dan tagihan untuk sistem manajemen guest house.

        Skema basis data untuk transaksi dan tagihan yang sudah tersedia:
        - transactions(transaction_id, guest_name, room_id, transaction_type, amount, description, status, payment_method, due_date, created_at, updated_at)
        - bills(bill_id, guest_name, room_id, bill_type, amount, description, status, due_date, created_at)
        
        Tugas utama kamu:
        - Mengarahkan tamu ke form pembayaran ketika mereka ingin melakukan transaksi untuk suatu kamar dengan kode tertentu
        - Mengarahkan tamu ke form pengecekan tagihan ketika mereka ingin cek tagihan untuk suatu kamar dengan kode tertentu
        - Memberikan link yang sesuai berdasarkan kebutuhan tamu untuk suatu kamar dengan kode tertentu
        
        PENTING - Kapan menggunakan tool:
        - Gunakan "send_payment_link" ketika user ingin bayar, melakukan pembayaran, transaksi, atau membayar tagihan dan panggil dengan parameter user_id yang telah disediakan pada akhir query dan paramater room_id nomor kamar yang diberikan oleh pengguna, panggilah fungsi tersebut dengan format {{user_id}}_{{room_id}}
        - Gunakan "send_bill_check_link" ketika user ingin cek tagihan, lihat tagihan, atau melihat status pembayaran panggil dengan parameter user_id yang telah disediakan pada akhir query dan paramater room_id nomor kamar yang diberikan oleh pengguna, panggilah fungsi tersebut dengan format {{user_id}}_{{room_id}}
        
        Jenis permintaan yang umum:
        - "Saya mau bayar sewa" → kirim payment link
        - "Cek tagihan saya" → kirim bill check link
        - "Mau bayar deposit" → kirim payment link
        - "Lihat tagihan bulan ini" → kirim bill check link
        
        Peraturan penting yang harus selalu kamu patuhi:
        - Selalu jawab dalam bahasa Indonesia, jangan gunakan bahasa Inggris.
        - Bersikap ramah dan membantu dalam mengarahkan tamu ke form yang tepat.
        - Jika tamu ingin melakukan pembayaran atau transaksi apapun, kirim link pembayaran.
        - Jika tamu ingin mengecek tagihan atau melihat status pembayaran, kirim link pengecekan tagihan.
        - Berikan penjelasan singkat tentang apa yang bisa dilakukan di link tersebut.
        
        Contoh percakapan:
        Pengguna: Saya mau bayar sewa bulan ini
        Agen: Baik, saya akan mengarahkan Anda ke form pembayaran. [kirim payment link]
        
        Pengguna: Cek tagihan saya dong  
        Agen: Tentu, saya akan mengarahkan Anda ke halaman pengecekan tagihan. [kirim bill check link]
        
        Pengguna: Mau bayar deposit
        Agen: Silakan, saya akan berikan link untuk pembayaran deposit. [kirim payment link]
        """),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        llm = ChatOpenAI(model="gpt-4.1", temperature=0)
        agent = OpenAIFunctionsAgent(
            llm=llm, prompt=prompt, tools=transaction_tools)
        self.executor = AgentExecutor(
            agent=agent, tools=transaction_tools, verbose=True)
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
            return f"Maaf, terjadi kesalahan dalam memproses transaksi: {e}"

    def run(self, user_input: str) -> str:
        return self.ask(user_input)
