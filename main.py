from dotenv import load_dotenv
from agents.db_agent import create_db_agent
from agents.doc_agent import create_doc_agent


def main():
    load_dotenv()

    # Initialize agents
    db_agent = create_db_agent()
    doc_agent = create_doc_agent()

    # # Example usage
    print("=== Database Agent ===")
    db_result = db_agent.run("How many rooms left?")
    print(db_result)

    print("\n=== Document Agent ===")
    doc_result = doc_agent.run("What is an interesting fact about English?")
    print(doc_result)


if __name__ == "__main__":
    main()