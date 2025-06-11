import json
from typing import Optional, List
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from langchain.chat_models import ChatOpenAI
from tools.qa_tools import setup_document_retriever
from utils.logger import logger


class QAAgentWrapper:
    """Professional Q&A Agent for Guest House Document Retrieval"""

    def __init__(self, model: str = "gpt-4.1-mini", temperature: float = 0.1):
        """
        Initialize the Q&A Agent

        Args:
            model (str): OpenAI model to use
            temperature (float): Temperature for model responses
        """
        self.model = model
        self.temperature = temperature
        self.chat_history = []
        self.executor = None
        self._initialize_agent()

    def _load_few_shot_examples(self) -> str:
        """Load and format few-shot examples from JSON file"""
        try:
            with open('agents/few_shot/qa_tools_few_shot.json', 'r', encoding='utf-8') as f:
                qa_data = json.load(f)

            formatted_examples = ""
            for i, item in enumerate(qa_data[:8], 1):  # Use first 8 examples
                formatted_examples += f"""
                    Contoh {i}:
                    Pengguna: {item['question']}
                    Asisten: {item['answer']}
                """
            return formatted_examples

        except FileNotFoundError:
            logger.warning(
                "Few-shot examples file not found, using default examples")
            return self._get_default_examples()
        except Exception as e:
            logger.error(f"Error loading few-shot examples: {str(e)}")
            return self._get_default_examples()

    def _get_default_examples(self) -> str:
        """Provide default examples if file is not available"""
        return """
Contoh 1:
Pengguna: Sampai jam berapa jam malam berlaku di guest house ini?
Asisten: Berdasarkan peraturan guest house, jam malam berlaku sampai dengan pukul 23.00 WIB. Setelah jam tersebut, pintu gerbang guest house akan dikunci dan tidak dapat keluar-masuk tanpa izin khusus dari pengelola.

Contoh 2:
Pengguna: Bolehkah membawa tamu laki-laki ke kamar?
Asisten: Berdasarkan peraturan guest house, tamu laki-laki tidak diperbolehkan masuk ke area kamar. Tamu laki-laki hanya boleh menunggu di area lobby. Selain itu, semua tamu wajib melapor kepada pengelola atau pengurus guest house sebelum berkunjung.

Contoh 3:
Pengguna: Apa aturan mengenai kebersihan di guest house?
Asisten: Berdasarkan peraturan guest house, setiap penghuni bertanggung jawab atas kebersihan kamar dan area bersama. Penghuni wajib membuang sampah pada tempatnya dan tidak melakukan vandalisme. Untuk area dapur, penghuni harus langsung membersihkan kompor, alat masak, dan peralatan makan setelah digunakan.
"""

    def _create_system_prompt(self) -> str:
        """Create comprehensive system prompt for the agent"""
        examples = self._load_few_shot_examples()

        return f"""Anda adalah asisten virtual profesional untuk sistem manajemen guest house yang bertugas memberikan informasi akurat mengenai peraturan dan kebijakan guest house.

IDENTITAS DAN PERAN:
- Anda adalah asisten yang ramah, profesional, dan membantu
- Spesialisasi: Memberikan informasi tentang peraturan, kebijakan, dan tata tertib guest house
- Selalu gunakan bahasa Indonesia yang sopan dan formal

TUGAS UTAMA:
1. Menjawab pertanyaan tentang peraturan guest house berdasarkan dokumen resmi
2. Memberikan informasi yang akurat dan terkini dari database dokumen
3. Membantu penghuni memahami kebijakan dan aturan yang berlaku
4. Memberikan panduan yang jelas dan mudah dipahami

PRINSIP KERJA:
✓ SELALU gunakan tool DocumentRetrieval untuk mencari informasi dari dokumen resmi
✓ HANYA berikan informasi yang terdapat dalam dokumen, JANGAN membuat asumsi
✓ Jika informasi tidak ditemukan, sampaikan dengan jujur dan sarankan alternatif
✓ Gunakan bahasa yang sopan, profesional, dan mudah dipahami
✓ Berikan konteks dan penjelasan tambahan jika diperlukan

GAYA KOMUNIKASI:
- Selalu awali dengan sapaan yang ramah jika diperlukan
- Gunakan "Berdasarkan peraturan guest house..." untuk memberikan kredibilitas
- Berikan jawaban yang lengkap namun tidak berlebihan
- Akhiri dengan penawaran bantuan lebih lanjut jika sesuai
- Gunakan format Markdown untuk memastikan pesan yang diterima oleh pelanggan dapat dilihat dengan mudah

LARANGAN:
✗ JANGAN menjawab dengan pengetahuan umum tanpa menggunakan tool
✗ JANGAN memberikan informasi yang tidak ada dalam dokumen
✗ JANGAN menggunakan bahasa informal atau tidak sopan
✗ JANGAN membuat peraturan atau kebijakan baru

CONTOH INTERAKSI:
{examples}

PENANGANAN SITUASI KHUSUS:
- Jika dokumen tidak ditemukan: Jelaskan dengan sopan dan sarankan menghubungi pengelola
- Jika pertanyaan tidak jelas: Minta klarifikasi dengan ramah
- Jika pertanyaan di luar lingkup: Arahkan ke pengelola guest house

Berikut URL dokumentasi yang dapat diberikan kepada calon penghuni guest house:
- Balikan Dokumen Penjelasan Detail Kamar: ``` https://drive.google.com/file/d/1tjETJ4pRF0A8wvy6MArWJvq2_p2E1i_D/view?usp=sharing ```
- Balikan Dokumen Pembayaran Detail Kamar: ``` https://drive.google.com/file/d/1gl1zWZfmfcv06LVNPDOBjERf9avkBko2/view?usp=sharing ```
- Balikan Dokumen Tata Tertib Detail Kamar: ``` https://drive.google.com/file/d/1VwC6hu0h_Jymknvwl1asRmsx_0tE6QqO/view?usp=sharing ```

Selalu ingat bahwa Anda harus mengirimkan URL dokumen yang relevan kepada penghuni guest house jika mereka membutuhkan informasi lebih lanjut.
URL Dokumen ini akan membantu mereka memahami peraturan dan kebijakan dengan lebih baik.
Keluarkan dokumen URL ini dalam format Markdown yang mudah dibaca.

Ingat: Tujuan Anda adalah memberikan pelayanan informasi terbaik untuk membantu penghuni guest house memahami dan mematuhi peraturan yang berlaku."""

    def _initialize_agent(self):
        """Initialize the Q&A agent with tools and prompts"""
        try:
            logger.info("Initializing Q&A Agent...")

            # Setup tools
            doc_tools = setup_document_retriever()

            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=self._create_system_prompt()),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])

            # Initialize LLM
            llm = ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                max_tokens=1000  # Reasonable limit for responses
            )

            # Create agent
            agent = OpenAIFunctionsAgent(
                llm=llm,
                prompt=prompt,
                tools=doc_tools
            )

            # Create executor
            self.executor = AgentExecutor(
                agent=agent,
                tools=doc_tools,
                verbose=False,
                max_iterations=3,
                early_stopping_method="generate",
                handle_parsing_errors=True
            )

            logger.info("Q&A Agent initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Q&A Agent: {str(e)}")
            raise

    def ask(self, user_input: str) -> str:
        """
        Process user question and return response

        Args:
            user_input (str): User's question

        Returns:
            str: Professional response
        """
        try:
            # Validate input
            if not user_input or not user_input.strip():
                return "Maaf, pertanyaan tidak boleh kosong. Silakan ajukan pertanyaan yang lebih spesifik mengenai peraturan guest house."

            # Clean input
            cleaned_input = user_input.strip()

            # Log the interaction
            logger.info(f"Processing query: {cleaned_input[:100]}...")

            # Process with agent
            if (not self.executor):
                return "Maaf, terjadi gangguan pada sistem"

            result = self.executor.invoke({
                "input": cleaned_input,
                "chat_history": self.chat_history
            })

            # Extract response
            response = result.get("output", "").strip()

            # Update chat history
            self._update_chat_history(cleaned_input, response)

            # Validate and format response
            if response:
                return self._format_final_response(response)
            else:
                return self._get_fallback_response()

        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return self._get_error_response()

    def _update_chat_history(self, user_input: str, response: str):
        """Update chat history with latest interaction"""
        try:
            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=response))

            # Limit chat history to last 10 exchanges (20 messages)
            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]

        except Exception as e:
            logger.error(f"Error updating chat history: {str(e)}")

    def _format_final_response(self, response: str) -> str:
        """Format the final response with professional touch"""
        # Ensure response ends properly
        if not response.endswith(('.', '!', '?')):
            response += '.'

        # Add helpful closing if response is informational
        if len(response) > 100 and not response.endswith(('lebih lanjut.', 'pengelola.', 'tersedia.')):
            response += "\n\nJika ada pertanyaan lain mengenai peraturan guest house, silakan tanyakan."

        return response

    def _get_fallback_response(self) -> str:
        """Provide fallback response when normal processing fails"""
        return (
            "Maaf, saya mengalami kendala dalam memproses pertanyaan Anda. "
            "Silakan coba ajukan pertanyaan dengan cara yang berbeda atau "
            "hubungi pengelola guest house untuk informasi lebih lanjut."
        )

    def _get_error_response(self) -> str:
        """Provide error response for technical issues"""
        return (
            "Maaf, terjadi kendala teknis saat memproses pertanyaan Anda. "
            "Silakan coba lagi dalam beberapa saat atau hubungi administrator "
            "jika masalah berlanjut."
        )

    def run(self, user_input: str) -> str:
        """
        Main entry point for the agent (alias for ask method)

        Args:
            user_input (str): User's question

        Returns:
            str: Professional response
        """
        return self.ask(user_input)

    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []
        logger.info("Chat history cleared")

    def get_agent_info(self) -> dict:
        """Get information about the agent configuration"""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "chat_history_length": len(self.chat_history),
            "tools_available": len(self.executor.tools) if self.executor else 0
        }


def create_qa_agent(model: str = "gpt-4.1-mini", temperature: float = 0.1) -> QAAgentWrapper:
    """
    Factory function to create Q&A agent

    Args:
        model (str): OpenAI model to use
        temperature (float): Temperature for responses

    Returns:
        QAAgentWrapper: Initialized Q&A agent
    """
    return QAAgentWrapper(model=model, temperature=temperature)


# Test function
def test_qa_agent():
    """Test the Q&A agent with sample queries"""
    try:
        agent = create_qa_agent()

        test_queries = [
            "Halo, bisakah Anda membantu saya?",
            "Jam berapa jam malam di guest house ini?",
            "Bolehkah saya membawa teman laki-laki ke kamar?",
            "Apa aturan tentang kebersihan kamar?",
            "Bolehkah membawa hewan peliharaan?",
            "Pertanyaan yang tidak ada jawabannya"
        ]

        print("Testing Q&A Agent:")
        print("=" * 60)

        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Pertanyaan: {query}")
            response = agent.ask(query)
            print(f"   Jawaban: {response}")
            print("-" * 40)

        # Show agent info
        print(f"\nAgent Info: {agent.get_agent_info()}")

    except Exception as e:
        print(f"Test failed: {str(e)}")


if __name__ == "__main__":
    # Run test if script is executed directly
    test_qa_agent()
