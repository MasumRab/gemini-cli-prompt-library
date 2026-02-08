from dspy_integration.framework.manifest import get_commands

# TODO [High Priority]: Replace functional dispatch with IntelligentDispatcher class
# The IntelligentDispatcher class from registry.py should be moved here.
# TODO [Performance]: Avoid calling get_commands() on every request; use Registry caching.

def dispatch(user_input):
    commands = get_commands()
    user_input = user_input.lower()

    best_match = None
    max_score = 0

    for command in commands:
        score = 0
        name_tokens = set(command["name"].lower().replace("-", " ").split())
        description_tokens = set(command["description"].lower().split())

        # Prioritize exact matches in the name
        if command["name"].replace("-", " ") in user_input:
            score += 10

        # Prioritize longer matches
        name_match_len = len(name_tokens.intersection(user_input.split()))
        description_match_len = len(description_tokens.intersection(user_input.split()))

        score += (name_match_len * 5) + description_match_len

        if score > max_score:
            max_score = score
            best_match = command

    return best_match

if __name__ == "__main__":
    test_input = "my test is broken"
    recommended_command = dispatch(test_input)
    print(recommended_command)
