from langchain.agents import Tool, initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from agents.db_agent import DBAgentWrapper
from agents.qa_agent import QAAgentWrapper
from agents.complaint_agent import ComplaintAgentWrapper
from agents.transaction_agent import TransactionAgentWrapper
from utils.zeroshot_formatter import ZeroShotTextFormatter
from utils.logger import logger
from datetime import datetime
import pytz
from database.db_operator.chat import ChatRepository

class MainAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True)

        # Initialize sub-agents
        self.db_agent = DBAgentWrapper()
        self.qa_agent = QAAgentWrapper()
        self.complaint_agent = ComplaintAgentWrapper()
        self.transaction_agent = TransactionAgentWrapper()
        self.formatter = ZeroShotTextFormatter(use_llm=True)
        self.chat_db = ChatRepository()

        # Define tools for the main agent
        self.tools = [
            Tool(
                name="DatabaseAgent",
                func=self.db_agent.run,
                description="Berguna untuk menjawab pertanyaan terkait kost-kostan baik dari ketersediaan kamar dan juga keadaan kost-kostan, jangan insert user_id kedalam sini"
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
            ),
            Tool(
                name="TransactionAgent",
                func=self.transaction_agent.run,
                description="Berguna ketika user ingin: bayar sewa, bayar tagihan, bayar deposit, melakukan pembayaran, cek tagihan, lihat tagihan, transfer uang, pembayaran bulanan, atau hal apapun yang berkaitan dengan uang dan pembayaran, selalu pastikan user_id dimasukkan ke sini"
            )
        ]

        # Initialize main agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            max_iterations=3
        )

    async def run(self, query, user_id):

        try:
            jakarta_tz = pytz.timezone('Asia/Jakarta')
            sent_at = datetime.now(jakarta_tz)

            await self.chat_db.insert_chat(
                user_id=user_id,
                chat_type='IN',
                role='USER',
                chat=query,
                sent_at=sent_at
            )
            logger.info("User chat inserted successfully.")
        except Exception as e:
            logger.error(f"Error inserting user chat: {e}")

        # Run agent
        try:
            raw_result = self.agent.run(input=f"{query}, user_id = {user_id}")
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            raise

        formatted_result = self.formatter.format_text(raw_result)

        try:
            sent_at = datetime.now(jakarta_tz)

            await self.chat_db.insert_chat(
                user_id=user_id,
                chat_type='OUT',
                role='AGENT',
                chat=formatted_result,
                sent_at=sent_at
            )
            logger.info("Agent chat inserted successfully.")
        except Exception as e:
            logger.error(f"Error inserting agent chat: {e}")

        return formatted_result
