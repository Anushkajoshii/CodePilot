import argparse
import os
import sys
import traceback

from dotenv import load_dotenv

from agent.graph import build_agent, init_project_root

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Run engineering project planner")
    parser.add_argument("--recursion-limit", "-r", type=int, default=100,
                        help="Recursion limit for processing (default: 100)")

    args = parser.parse_args()

    try:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            sys.exit("Set GROQ_API_KEY in your environment or .env file.")
        user_prompt = input("Enter your project prompt: ")
        project_path = init_project_root("cli_project")
        agent = build_agent(api_key)
        result = agent.invoke(
            {"user_prompt": user_prompt},
            {"recursion_limit": args.recursion_limit}
        )
        print("Final State:", result)
        print(f"Project written to: {project_path}")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        traceback.print_exc()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()