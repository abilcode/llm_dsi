from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool


def setup_document_retriever(persist_dir="emb_qa"):
    """Initialize document retrieval system"""
    embeddings = OpenAIEmbeddings()
    db = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
    )
    retriever = db.as_retriever()

    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-3.5-turbo"),
        retriever=retriever,
        chain_type="stuff"
    )

    return [
        Tool(
            name="DocumentRetrieval",
            func=qa_chain.run,
            description="Useful for answering questions from documents"
        )
    ]