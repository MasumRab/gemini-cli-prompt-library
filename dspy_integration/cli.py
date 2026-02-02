import argparse
from dspy_integration.framework.dispatcher import dispatch

# TODO [Medium Priority]: Update to use IntelligentDispatcher class.
# Reason: Currently uses the legacy function-based dispatch() from framework/dispatcher.py.
# Should instantiate and use the class-based IntelligentDispatcher for consistency.

def main():
    parser = argparse.ArgumentParser(description="Dispatch a command based on natural language input.")
    parser.add_argument("user_input", type=str, help="The natural language input from the user.")
    args = parser.parse_args()

    recommended_command = dispatch(args.user_input)

    if recommended_command:
        # Format the command for display
        command_name = f'/{recommended_command["category"]}:{recommended_command["name"]}'

        # Create a placeholder for arguments based on the user input
        placeholder_args = f'--prompt "{args.user_input}"'

        print(f'[1] {command_name} {placeholder_args}')
    else:
        print("No command recommendation found.")

if __name__ == "__main__":
    main()
