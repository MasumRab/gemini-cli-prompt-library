import unittest
from dspy_integration.framework.dispatcher import dispatch


class TestDispatcher(unittest.TestCase):
    def test_dispatch(self):
        # Test that a specific input returns the expected command
        user_input = "my test is broken"
        recommended_command = dispatch(user_input)
        self.assertIsNotNone(recommended_command)
        self.assertEqual(recommended_command.name, "test-case")

        # Test another input
        user_input = "refactor my code"
        recommended_command = dispatch(user_input)
        self.assertIsNotNone(recommended_command)
        self.assertEqual(recommended_command.name, "refactor")


if __name__ == "__main__":
    unittest.main()
