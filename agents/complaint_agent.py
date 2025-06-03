import json
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from langchain.chat_models import ChatOpenAI
from tools.complaint_tools import complaint_tools


class ComplaintAgentWrapper:
    def __init__(self, ):
        self.chat_history = []

        # ==== Load Few-shot Examples from JSON ====
        with open('agents/few_shot/complaint_tools_few_shot.json', 'r') as f:
            complaint_data = json.load(f)

        fewshot_messages = []
        for ex in complaint_data:
            fewshot_messages.append(HumanMessage(content=ex["user_input"]))
            reasoning = "\n".join(f"- {step}" for step in ex["chain_of_thought"])
            if ex["action"]:
                tool = ex["action"]["tool"]
                params = ex["action"]["parameters"]
                action = f"Memanggil fungsi `{tool}` dengan parameter: {params}"
            else:
                action = "Tidak bisa mengambil tindakan karena informasi belum lengkap."
            fewshot_messages.append(AIMessage(content=f"Langkah berpikir:\n{reasoning}\n\nTindakan:\n{action}"))

        # ==== Prompt Template ====
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""Kamu adalah agen layanan pelanggan untuk guest house. 
Tugasmu adalah mencatat, menampilkan, dan memperbarui status komplain dari tamu.

Selalu jawab dalam bahasa Indonesia. Jika data yang dibutuhkan tidak lengkap, tanyakan kembali ke pengguna."""),
            *fewshot_messages,
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # ==== Agent Setup ====
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        agent = OpenAIFunctionsAgent(llm=llm, prompt=prompt, tools=complaint_tools)
        self.executor = AgentExecutor(agent=agent, tools=complaint_tools, verbose=True)

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
