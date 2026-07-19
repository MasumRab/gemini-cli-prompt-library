import sys

from tools.sessions.config import calculate_grade
from .test_api_connection import test_connection


def test_grading():
    print("Testing grading logic...")
    data = {"completion_rate": 1.0, "activities": [None] * 10, "error_count": 0, "feedback_score": 1.0}
    grade, score = calculate_grade(data)
    print(f"Grade: {grade}, Score: {score}")
    assert grade == "A+"

    data = {"completion_rate": 0.5, "activities": [], "error_count": 5}
    grade, score = calculate_grade(data)
    print(f"Grade: {grade}, Score: {score}")
    assert grade == "C"
    print("Grading logic test passed.")

def main():
    try:
        test_connection()
        test_grading()
        print("\nAll feature tests passed.")
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
