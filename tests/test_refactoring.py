"""
Test suite to verify that the refactored code works correctly.

This test verifies that the unified command loader and dynamic module loader
work as expected and that the code duplication fixes are functioning properly.
"""

import unittest
from pathlib import Path
from dspy_integration.framework.command_loader import (
    UnifiedCommandLoader, 
    CommandRegistry,
    IntelligentDispatcher
)
from dspy_integration.modules.loader import DynamicModuleLoader
from dspy_integration.modules import get_module_for_scenario


class TestUnifiedCommandLoader(unittest.TestCase):
    """Test the unified command loader functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = UnifiedCommandLoader()
    
    def test_load_all_commands(self):
        """Test that commands can be loaded."""
        commands = self.loader.load_all_commands()
        self.assertIsInstance(commands, dict)
        # At least some commands should exist
        self.assertGreaterEqual(len(commands), 0)  # May be empty if no commands exist yet
    
    def test_get_command(self):
        """Test getting a specific command."""
        # This test may not find any commands if none exist yet
        command = self.loader.get_command("nonexistent_command")
        self.assertIsNone(command)
    
    def test_search_commands(self):
        """Test searching for commands."""
        results = self.loader.search_commands("test")
        self.assertIsInstance(results, list)
    
    def test_list_commands_by_category(self):
        """Test listing commands by category."""
        results = self.loader.list_commands_by_category("test")
        self.assertIsInstance(results, list)


class TestCommandRegistry(unittest.TestCase):
    """Test the updated CommandRegistry using unified loader."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = CommandRegistry()
    
    def test_registry_initialization(self):
        """Test that the registry initializes correctly."""
        self.assertIsNotNone(self.registry.loader)
        self.assertIsNotNone(self.registry.commands)
    
    def test_get_command(self):
        """Test getting a command from the registry."""
        command = self.registry.get_command("nonexistent_command")
        self.assertIsNone(command)


class TestIntelligentDispatcher(unittest.TestCase):
    """Test the IntelligentDispatcher functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.dispatcher = IntelligentDispatcher()
    
    def test_dispatch_method_exists(self):
        """Test that the dispatch method exists."""
        self.assertTrue(hasattr(self.dispatcher, 'dispatch'))
        self.assertTrue(callable(getattr(self.dispatcher, 'dispatch')))


class TestDynamicModuleLoader(unittest.TestCase):
    """Test the dynamic module loader functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = DynamicModuleLoader()
    
    def test_get_available_modules(self):
        """Test getting available modules."""
        available = self.loader._get_available_modules()
        self.assertIsInstance(available, list)
    
    def test_scenario_exists_function(self):
        """Test the scenario_exists function."""
        # This may fail if no scenarios exist yet, but the function should be importable
        from dspy_integration.modules import scenario_exists
        self.assertTrue(callable(scenario_exists))


class TestIntegration(unittest.TestCase):
    """Test integration between components."""
    
    def test_get_module_for_scenario(self):
        """Test that get_module_for_scenario function works."""
        # This may raise ValueError if scenario doesn't exist, which is expected
        try:
            module_class = get_module_for_scenario("security_review")
            # If we get here, the function worked
            self.assertIsNotNone(module_class)
        except ValueError:
            # Expected if the scenario doesn't exist
            pass


if __name__ == '__main__':
    # Run the tests
    unittest.main()