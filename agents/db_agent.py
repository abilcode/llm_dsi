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

Skema basis data:
- rooms(room_id, level, height, availability, room_type)
- levels(level_id, level_name, description)
- room_types(type_id, type_name, base_rate, max_occupancy)

Peraturan penting yang harus selalu kamu patuhi:
- Selalu jawab dalam bahasa Indonesia, jangan gunakan bahasa Inggris.
- Selalu gunakan perbandingan yang sesuai saat menggunakan operator logika.
- Jika kamu ragu, tanyakan kembali ke pengguna.
- Jangan gunakan dan abaikan "user_id" yang disediakan oleh user
"""),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        llm = ChatOpenAI(model="gpt-4", temperature=0)
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
