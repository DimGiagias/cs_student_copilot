import argparse
import os
from agents.coordinator import route_query

def main():
    parser = argparse.ArgumentParser(description="CS Student Copilot CLI")
    subparsers = parser.add_subparsers(dest="command_group", help="Available agent groups", required=True)
    
    study_parser = subparsers.add_parser("studybuddy", help="Interact with StudyBuddy to manage and query your knowledge base")
    study_subparsers = study_parser.add_subparsers(dest="study_command", help="StudyBuddy commands", required=True)
    
    # studybuddy index
    index_parser = study_subparsers.add_parser("index", help="Index documents from a directory into your knowledge base")
    index_parser.add_argument("--path", type=str, help="Path to the directory with your documents (e.g., './my_notes'). Defaults to 'course_materials'.")
    
    # studybuddy ask
    ask_parser = study_subparsers.add_parser("ask", help="Ask a question to your indexed knowledge base")
    ask_parser.add_argument("query", type=str, help="The question you want to ask")

    args = parser.parse_args()

    response = None
    agent_display_name = args.command_group.capitalize()
    
    if args.command_group == "studybuddy":
        if args.study_command == "index":
            directory_path = args.path if args.path else "the default directory"
            agent_input = f"Please index the documents in {directory_path}."
            print(f"Asking StudyBuddy to index directory: '{args.path or 'deafault directory'}'...\n")
            response = route_query(query=agent_input, agent_name="studybuddy")
        elif args.study_command == "ask":
            print(f"Asking StudyBuddy: {args.query}\n")
            response = route_query(query=args.query, agent_name="studybuddy")
        else:
            response = "Unknown studybuddy command."
    else:
        print(f"Unknown command group: {args.command_group}")
        parser.print_help()
        return

    if response:
        print(f"\n{agent_display_name}'s Response:")
        print(response)
    else:
        print(f"No response received from {agent_display_name}.")


if __name__ == "__main__":
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY is not set in your environment or .env file.")
        print("Please set it up before running the CLI.")
    else:
        main()