import unittest
from dspy_integration.framework.manifest import get_commands


class TestManifest(unittest.TestCase):
    def test_get_commands(self):
        commands = get_commands()
        self.assertEqual(len(commands), 42)

        # Check that a few expected commands are present
        command_names = [cmd["name"] for cmd in commands]
        self.assertIn("coverage-analysis", command_names)
        self.assertIn("smart-refactor", command_names)
        self.assertIn("debug-error", command_names)
        self.assertIn("scheduled-codebase-audit", command_names)


if __name__ == "__main__":
    unittest.main()
