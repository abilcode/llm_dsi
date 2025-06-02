from langchain.agents import AgentExecutor, Tool
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from agents.db_agent import DBAgentWrapper
from agents.doc_agent import create_doc_agent


class MainAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Initialize sub-agents
        self.db_agent = DBAgentWrapper()
        self.doc_agent = create_doc_agent()

        # Define tools for the main agent
        self.tools = [
            Tool(
                name="DatabaseAgent",
                func=self.db_agent.run,
                description="Useful for answering questions about room availability, bookings, and guest house data"
            ),
            Tool(
                name="DocumentAgent",
                func=self.doc_agent.run,
                description="Useful for answering questions about guest policies, facilities, and general information"
            )
        ]

        # Initialize main agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent="chat-conversational-react-description",
            verbose=True,
            memory=self.memory,
            max_iterations=3
        )

    def run(self, query):
        return self.agent.run(input=query)