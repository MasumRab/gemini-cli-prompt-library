import argparse
from dspy_integration.framework.dispatcher import dispatch


def main():
    # TODO [High Priority]: Implement full CLI args parsing (argparse/click).
    # See JOBS_FOR_JULES.md for requirements (forgiving parsing, robot mode).
    parser = argparse.ArgumentParser(
        description="Dispatch a command based on natural language input."
    )
    parser.add_argument(
        "user_input", type=str, help="The natural language input from the user."
    )
    # TODO: Add robot mode and smart dispatch integration.
    # parser.add_argument("--robot", action="store_true", help="Enable robot/AI mode")
    args = parser.parse_args()

    recommended_command = dispatch(args.user_input)

    if recommended_command:
        # Format the command for display
        command_name = f'/{recommended_command.category}:{recommended_command.name}'

        # Create a placeholder for arguments based on the user input
        placeholder_args = f'--prompt "{args.user_input}"'

        print(f"[1] {command_name} {placeholder_args}")
    else:
        print("No command recommendation found.")


if __name__ == "__main__":
    main()
