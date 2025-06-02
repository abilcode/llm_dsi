from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.schema import SystemMessage
from langchain.chat_models import ChatOpenAI
from tools.doc_tools import setup_document_retriever


def create_doc_agent():
    """Create document retrieval agent"""
    doc_tools = setup_document_retriever()

    prompt = ChatPromptTemplate(
        messages=[
            SystemMessage(content=""""
            Kamu adalah agen pencarian informasi khusus untuk dokumen guest house.
            
            Tugas utama kamu adalah:
            - Menjawab pertanyaan berdasarkan informasi yang ditemukan dari basis data dokumen (vector database).
            - Jangan gunakan pengetahuan umum atau menjawab dengan asumsi pribadi.
            - Jika jawabannya **ada di dokumen**, berikan jawaban tersebut secara lengkap dan jelas dalam bahasa Indonesia.
            - Jika jawabannya **tidak ditemukan** dalam dokumen, jawab dengan kalimat seperti: "Maaf, saya tidak menemukan informasi tersebut dalam dokumen yang tersedia."
            
            Peraturan penting:
            - Selalu gunakan bahasa Indonesia!
            - Jangan berbohong atau menebak jika tidak yakin jawabannya ada di dokumen.
            """),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ]
    )

    agent = OpenAIFunctionsAgent(
        llm=ChatOpenAI(model="gpt-3.5-turbo"),
        prompt=prompt,
        tools=doc_tools
    )

    return AgentExecutor(
        agent=agent,
        tools=doc_tools,
        verbose=True
    )