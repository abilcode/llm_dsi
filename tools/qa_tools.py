from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from langchain.schema import Document
from typing import List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentQATool:
    """Professional document Q&A tool for guest house management system"""

    def __init__(self, persist_dir: str = "emb_qa", model: str = "gpt-3.5-turbo"):
        """
        Initialize the Document Q&A Tool

        Args:
            persist_dir (str): Directory for vector database persistence
            model (str): OpenAI model to use for Q&A
        """
        self.persist_dir = persist_dir
        self.model = model
        self.embeddings = None
        self.db = None
        self.qa_chain = None
        self._initialize_components()

    def _initialize_components(self):
        """Initialize embeddings, vector database, and QA chain"""
        try:
            logger.info("Initializing Document Q&A components...")

            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings()

            # Initialize vector database
            self.db = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings,
            )

            # Create retriever with enhanced search parameters
            retriever = self.db.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}  # Return top 3 most relevant documents
            )

            # Initialize QA chain with custom prompt
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(
                    model=self.model,
                    temperature=0.1,  # Low temperature for consistent responses
                ),
                retriever=retriever,
                chain_type="stuff",
                return_source_documents=True,
                verbose=False
            )

            logger.info("Document Q&A components initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Document Q&A components: {str(e)}")
            raise

    def search_documents(self, query: str) -> str:
        """
        Search and answer questions based on document content

        Args:
            query (str): User's question

        Returns:
            str: Professional response in Indonesian
        """
        try:
            if not query or not query.strip():
                return "Maaf, pertanyaan tidak boleh kosong. Silakan ajukan pertanyaan yang lebih spesifik."

            # Clean and validate query
            cleaned_query = query.strip()

            # Run QA chain
            result = self.qa_chain({"query": cleaned_query})

            # Extract answer and sources
            answer = result.get("result", "").strip()
            source_docs = result.get("source_documents", [])

            # Format response professionally
            if answer and not self._is_no_answer(answer):
                formatted_response = self._format_professional_response(answer, source_docs)
                return formatted_response
            else:
                return self._format_no_answer_response(cleaned_query)

        except Exception as e:
            logger.error(f"Error in document search: {str(e)}")
            return "Maaf, terjadi kendala teknis saat mencari informasi. Silakan coba lagi atau hubungi administrator."

    def _is_no_answer(self, answer: str) -> bool:
        """Check if the answer indicates no relevant information was found"""
        no_answer_indicators = [
            "tidak tahu",
            "tidak ada informasi",
            "tidak ditemukan",
            "tidak dapat menjawab",
            "i don't know",
            "no information",
            "not found"
        ]
        return any(indicator in answer.lower() for indicator in no_answer_indicators)

    def _format_professional_response(self, answer: str, source_docs: List[Document]) -> str:
        """Format the response in a professional manner"""
        # Clean up the answer
        cleaned_answer = answer.strip()

        # Ensure proper Indonesian greeting and professional tone
        if not cleaned_answer.startswith(("Berdasarkan", "Menurut", "Sesuai")):
            cleaned_answer = f"Berdasarkan peraturan guest house, {cleaned_answer.lower()}"

        # Add source confidence if available
        if source_docs:
            confidence_note = "\n\nInformasi ini berdasarkan dokumen peraturan resmi guest house."
            return cleaned_answer + confidence_note

        return cleaned_answer

    def _format_no_answer_response(self, query: str) -> str:
        """Format response when no relevant information is found"""
        return (
            f"Maaf, saya tidak menemukan informasi yang relevan mengenai '{query}' "
            "dalam dokumen peraturan yang tersedia. "
            "\n\nUntuk informasi lebih lanjut, silakan hubungi pengelola guest house secara langsung "
            "atau ajukan pertanyaan yang lebih spesifik terkait peraturan dan kebijakan guest house."
        )

    def get_available_topics(self) -> str:
        """Return information about available topics in the database"""
        try:
            # Get a sample of documents to understand available content
            if self.db:
                docs = self.db.similarity_search("peraturan", k=5)
                if docs:
                    return (
                        "Saya dapat membantu Anda dengan informasi mengenai:\n"
                        "• Peraturan dan tata tertib guest house\n"
                        "• Jam malam dan akses masuk-keluar\n"
                        "• Kebijakan tamu dan kunjungan\n"
                        "• Aturan kebersihan dan fasilitas\n"
                        "• Larangan dan sanksi\n"
                        "• Kebijakan umum guest house\n\n"
                        "Silakan ajukan pertanyaan spesifik terkait topik-topik di atas."
                    )

            return (
                "Saya siap membantu menjawab pertanyaan Anda mengenai peraturan dan "
                "kebijakan guest house. Silakan ajukan pertanyaan spesifik."
            )

        except Exception as e:
            logger.error(f"Error getting available topics: {str(e)}")
            return "Silakan ajukan pertanyaan mengenai peraturan guest house."


def setup_document_retriever(persist_dir: str = "emb_qa", model: str = "gpt-3.5-turbo") -> List[Tool]:
    """
    Initialize and return document retrieval tools

    Args:
        persist_dir (str): Directory for vector database persistence
        model (str): OpenAI model to use

    Returns:
        List[Tool]: List of LangChain tools for document retrieval
    """
    try:
        qa_tool = DocumentQATool(persist_dir=persist_dir, model=model)

        return [
            Tool(
                name="DocumentRetrieval",
                func=qa_tool.search_documents,
                description=(
                    "Gunakan tool ini untuk mencari dan menjawab pertanyaan berdasarkan "
                    "dokumen peraturan guest house. Input berupa pertanyaan dalam bahasa Indonesia. "
                    "Tool ini dapat menjawab pertanyaan tentang peraturan, kebijakan, larangan, "
                    "dan tata tertib guest house."
                )
            ),
            Tool(
                name="GetAvailableTopics",
                func=qa_tool.get_available_topics,
                description=(
                    "Gunakan tool ini untuk mendapatkan informasi tentang topik-topik yang "
                    "tersedia dalam dokumen peraturan guest house. Berguna ketika user "
                    "bertanya secara umum atau tidak spesifik."
                )
            )
        ]

    except Exception as e:
        logger.error(f"Error setting up document retriever: {str(e)}")

        # Return a fallback tool
        def fallback_response(query: str) -> str:
            return (
                "Maaf, sistem pencarian dokumen sedang mengalami kendala. "
                "Silakan hubungi administrator atau coba lagi nanti."
            )

        return [
            Tool(
                name="DocumentRetrieval",
                func=fallback_response,
                description="Fallback tool for document retrieval"
            )
        ]


# Utility function for testing
def test_qa_tool():
    """Test function for the QA tool"""
    try:
        tools = setup_document_retriever()
        doc_tool = tools[0]

        test_queries = [
            "Jam berapa jam malam di guest house?",
            "Bolehkah membawa tamu laki-laki?",
            "Apa aturan tentang kebersihan?"
        ]

        print("Testing Document Q&A Tool:")
        print("=" * 50)

        for query in test_queries:
            print(f"\nQ: {query}")
            response = doc_tool.func(query)
            print(f"A: {response}")
            print("-" * 30)

    except Exception as e:
        print(f"Test failed: {str(e)}")


if __name__ == "__main__":
    # Run test if script is executed directly
    test_qa_tool()