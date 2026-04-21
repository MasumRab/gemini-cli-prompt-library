from dataclasses import dataclass
from dspy_integration.framework.manifest import get_commands
import re


@dataclass
class Command:
    name: str
    category: str
    description: str


def normalize_text(text: str) -> str:
    """Normalize text for matching/scoring (strip punctuation, lowercase)."""
    return re.sub(r"[^\w\s]", "", text).lower()


def dispatch(user_input):
    # TODO [Phase 3 - CASS Integration]: Replace this simple keyword matching with Hybrid Search.
    # TODO [Medium Priority]: Integrate `IntelligentDispatcher`
    # for better routing logic.

    commands = get_commands()
    user_input_normalized = normalize_text(user_input)

    best_match = None
    max_score = 0

    for command in commands:
        score = 0
        normalized_name = normalize_text(command["name"].replace("-", " "))
        normalized_description = normalize_text(command["description"])

        name_tokens = set(normalized_name.split())
        description_tokens = set(normalized_description.split())

        # Prioritize exact matches in the name
        if normalized_name in user_input_normalized:
            score += 10

        # Prioritize longer matches
        user_tokens = set(user_input_normalized.split())
        name_match_len = len(name_tokens.intersection(user_tokens))
        description_match_len = len(description_tokens.intersection(user_tokens))

        score += (name_match_len * 5) + description_match_len

        if score > max_score:
            max_score = score
            best_match = command

    if best_match:
        return Command(
            name=best_match["name"],
            category=best_match.get(
                "category", "unknown"
            ),  # Handle missing category safely
            description=best_match["description"],
        )
    return None


if __name__ == "__main__":
    test_input = "my test is broken"
    recommended_command = dispatch(test_input)
    print(recommended_command)
