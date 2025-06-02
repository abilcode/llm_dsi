from agents.main_agent import MainAgent
import pyfiglet
from dotenv import load_dotenv

load_dotenv()
def display_welcome():
    print(pyfiglet.figlet_format("Hotel Assistant"))
    print("Welcome to the Hotel Assistant!")
    print("Type 'exit' to end the conversation\n")


def main():
    #display_welcome()
    agent = MainAgent()

    while True:
        try:
            user_input = input("You: ")

            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break

            if not user_input.strip():
                continue

            response = agent.run(user_input)
            print(f"\nAssistant: {response}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Sorry, something went wrong: {str(e)}")


if __name__ == "__main__":
    main()