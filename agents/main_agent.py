from langchain.agents import AgentExecutor, Tool
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from agents.db_agent import DBAgentWrapper
from agents.qa_agent import create_qa_agent
from agents.complaint_agent import ComplaintAgentWrapper


class MainAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Initialize sub-agents
        self.db_agent = DBAgentWrapper()
        self.qa_agent = create_qa_agent()
        self.complaint_agent = ComplaintAgentWrapper()

        # Define tools for the main agent
        self.tools = [
            Tool(
                name="DatabaseAgent",
                func=self.db_agent.run,
                description="Berguna untuk menjawab pertanyaan terkait kost-kostan baik dari ketersediaan kamar dan juga keadaan kost-kostan"
            ),
            Tool(
                name="DocumentAgent",
                func=self.qa_agent.run,
                description="Berguna untuk menjawab pertanyaan seputar peraturan kost-kostan, larangan, dan juga hal-hal berbau FAQs"
            ),
            Tool(
                name="ComplaintAgent",
                func=self.complaint_agent.run,
                description="Berguna untuk menyelesaikan komplain yang diberikan user terhadap fasilitas, lingkungan, dan service kostan"
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