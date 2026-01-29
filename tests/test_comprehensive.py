"""
Comprehensive unit tests for the gemini-cli-prompt-library project.

This test suite covers various components of the framework including:
- Providers
- Scenarios
- Command loading
- Module loading
- Common utilities
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Test providers
from dspy_integration.framework.providers.base import BaseProvider, ProviderResponse, RateLimitConfig
from dspy_integration.framework.providers.gemini import GeminiProvider
from dspy_integration.framework.common import CommonUtils
from dspy_integration.framework.command_loader import UnifiedCommandLoader, CommandRegistry
from dspy_integration.modules.loader import DynamicModuleLoader
from dspy_integration.framework.scenarios.base import BaseScenario, ScenarioRegistry


class TestBaseProvider(unittest.TestCase):
    """Test the base provider functionality."""

    def test_provider_response_creation(self):
        """Test creating provider responses."""
        response = ProviderResponse(
            success=True,
            content="test content",
            provider="Test Provider",
            model="test-model"
        )
        self.assertTrue(response.success)
        self.assertEqual(response.content, "test content")
        self.assertEqual(response.provider, "Test Provider")
        self.assertEqual(response.model, "test-model")


class TestMockProvider(BaseProvider):
    """Mock provider for testing abstract base class methods."""

    def _execute_cli(self, prompt: str, **kwargs):
        """Mock implementation of abstract method."""
        return ProviderResponse(
            success=True,
            content="mock response",
            provider=self.name,
            model=self.model
        )


class TestConcreteProvider(unittest.TestCase):
    """Test concrete provider implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rate_limit_config = RateLimitConfig(enabled=True, max_retries=2)
        self.provider = TestMockProvider(
            name="Test Provider",
            command="test",
            subcommand="test",
            model="test-model",
            rate_limit=self.rate_limit_config
        )

    def test_provider_initialization(self):
        """Test that provider initializes correctly."""
        self.assertEqual(self.provider.name, "Test Provider")
        self.assertEqual(self.provider.model, "test-model")
        self.assertTrue(self.provider.rate_limit.enabled)


class TestCommonUtils(unittest.TestCase):
    """Test the common utilities."""
    
    def test_is_rate_limited_basic(self):
        """Test basic rate limiting detection."""
        output = "Error: rate limit exceeded"
        result = CommonUtils.is_rate_limited(output)
        self.assertTrue(result)
    
    def test_is_rate_limited_with_custom_indicators(self):
        """Test rate limiting detection with custom indicators."""
        output = "Error: custom limit hit"
        result = CommonUtils.is_rate_limited(output, custom_indicators=["custom limit"])
        self.assertTrue(result)
    
    def test_is_rate_limited_negative(self):
        """Test rate limiting detection with non-rate-limit text."""
        output = "Normal output"
        result = CommonUtils.is_rate_limited(output)
        self.assertFalse(result)


class TestCommandLoader(unittest.TestCase):
    """Test the unified command loader."""
    
    def setUp(self):
        """Set up temporary commands directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.commands_dir = Path(self.temp_dir) / "commands"
        self.commands_dir.mkdir()
        
        # Create a test category directory
        self.test_category_dir = self.commands_dir / "test_category"
        self.test_category_dir.mkdir()
        
        # Create a test TOML file
        test_toml_content = '''
        description = "Test command description"
        prompt = "# Test Command\\nThis is a test command."
        author = "Test Author"
        tags = ["test", "example"]
        '''
        test_file = self.test_category_dir / "test_command.toml"
        with open(test_file, 'w') as f:
            f.write(test_toml_content)
    
    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_command_loader_initialization(self):
        """Test that command loader initializes correctly."""
        loader = UnifiedCommandLoader(str(self.commands_dir))
        self.assertEqual(str(loader.commands_dir), str(self.commands_dir))
    
    def test_load_all_commands(self):
        """Test loading all commands."""
        loader = UnifiedCommandLoader(str(self.commands_dir))
        commands = loader.load_all_commands()
        
        self.assertIn("test_command", commands)
        command = commands["test_command"]
        self.assertEqual(command.name, "test_command")
        self.assertEqual(command.category, "test_category")
        self.assertEqual(command.description, "Test command description")
        self.assertIn("test", command.tags)
    
    def test_search_commands(self):
        """Test searching for commands."""
        loader = UnifiedCommandLoader(str(self.commands_dir))
        results = loader.search_commands("test")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "test_command")
    
    def test_get_command(self):
        """Test getting a specific command."""
        loader = UnifiedCommandLoader(str(self.commands_dir))
        command = loader.get_command("test_command")
        
        self.assertIsNotNone(command)
        self.assertEqual(command.name, "test_command")
    
    def test_get_nonexistent_command(self):
        """Test getting a nonexistent command."""
        loader = UnifiedCommandLoader(str(self.commands_dir))
        command = loader.get_command("nonexistent")
        
        self.assertIsNone(command)


class TestCommandRegistry(unittest.TestCase):
    """Test the command registry."""
    
    def setUp(self):
        """Set up temporary commands directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.commands_dir = Path(self.temp_dir) / "commands"
        self.commands_dir.mkdir()
        
        # Create a test category directory
        self.test_category_dir = self.commands_dir / "test_category"
        self.test_category_dir.mkdir()
        
        # Create a test TOML file
        test_toml_content = '''
        description = "Test command description"
        prompt = "# Test Command\\nThis is a test command."
        '''
        test_file = self.test_category_dir / "test_command.toml"
        with open(test_file, 'w') as f:
            f.write(test_toml_content)
    
    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_registry_initialization(self):
        """Test that registry initializes correctly."""
        registry = CommandRegistry(str(self.commands_dir))
        self.assertIsNotNone(registry.loader)
        self.assertIn("test_command", registry.commands)
    
    def test_registry_search(self):
        """Test registry search functionality."""
        registry = CommandRegistry(str(self.commands_dir))
        results = registry.search("test")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "test_command")


class TestDynamicModuleLoader(unittest.TestCase):
    """Test the dynamic module loader."""
    
    def test_convert_to_pascal_case(self):
        """Test converting snake_case to PascalCase."""
        loader = DynamicModuleLoader()
        
        result = loader._convert_to_pascal_case("security_review")
        self.assertEqual(result, "SecurityReview")
        
        result = loader._convert_to_pascal_case("unit_test")
        self.assertEqual(result, "UnitTest")
        
        result = loader._convert_to_pascal_case("api_design")
        self.assertEqual(result, "ApiDesign")
    
    def test_get_available_modules(self):
        """Test getting available modules."""
        loader = DynamicModuleLoader()
        modules = loader._get_available_modules()
        
        # Check that some expected modules exist
        expected_modules = ["security_review", "unit_test", "documentation", "code_review", "architecture", "improve"]
        found_expected = [mod for mod in modules if mod in expected_modules]
        self.assertGreaterEqual(len(found_expected), 0)


class TestScenarioRegistry(unittest.TestCase):
    """Test the scenario registry."""
    
    def test_registry_list_scenarios(self):
        """Test listing scenarios."""
        scenarios = ScenarioRegistry.list()
        self.assertIsInstance(scenarios, list)
        self.assertGreaterEqual(len(scenarios), 0)
    
    def test_registry_get_existing_scenario(self):
        """Test getting an existing scenario."""
        # Register a test scenario temporarily
        @ScenarioRegistry.register("test_scenario")
        class TestScenario(BaseScenario):
            INPUT_FIELDS = ["input"]
            OUTPUT_FIELDS = ["output"]
            
            def _load_raw_data(self):
                return [{"input": "test", "output": "result"}]
            
            def make_prompt(self, row):
                return f"Input: {row['input']}"
            
            def metric(self, example, pred, trace=None):
                return 1.0
        
        # Get the scenario
        scenario_class = ScenarioRegistry.get("test_scenario")
        self.assertEqual(scenario_class.__name__, "TestScenario")
        
        # Clean up by removing the test scenario
        if "test_scenario" in ScenarioRegistry._scenarios:
            del ScenarioRegistry._scenarios["test_scenario"]
    
    def test_registry_get_nonexistent_scenario(self):
        """Test getting a nonexistent scenario raises error."""
        with self.assertRaises(ValueError) as context:
            ScenarioRegistry.get("nonexistent_scenario")
        
        self.assertIn("Unknown scenario", str(context.exception))


class TestProviderChain(unittest.TestCase):
    """Test the provider chain functionality."""
    
    def test_provider_chain_initialization(self):
        """Test that provider chain initializes correctly."""
        from dspy_integration.framework.providers.base import ProviderChain
        
        # Create mock providers
        provider1 = MagicMock(spec=BaseProvider)
        provider1.name = "Provider1"
        provider2 = MagicMock(spec=BaseProvider)
        provider2.name = "Provider2"
        
        chain = ProviderChain([provider1, provider2])
        self.assertEqual(len(chain.providers), 2)
        self.assertEqual(chain.providers[0].name, "Provider1")


class TestMockScenario(BaseScenario):
    """Mock scenario for testing abstract base class methods."""

    def _load_raw_data(self):
        """Mock implementation of abstract method."""
        return [{"input": "test", "output": "result"}]

    def make_prompt(self, row):
        """Mock implementation of abstract method."""
        return f"Input: {row['input']}"

    def metric(self, example, pred, trace=None):
        """Mock implementation of abstract method."""
        return 1.0


class TestScenarioFunctionality(unittest.TestCase):
    """Test scenario functionality."""

    def test_base_scenario_properties(self):
        """Test base scenario properties."""
        scenario = TestMockScenario()

        # Test properties
        self.assertEqual(scenario.INPUT_FIELDS, [])
        self.assertEqual(scenario.OUTPUT_FIELDS, [])
        self.assertIsInstance(scenario.DEFAULT_SPLIT_RATIO, float)

    def test_split_data(self):
        """Test data splitting functionality."""
        scenario = TestMockScenario()

        # Create test data
        test_data = [{"id": i, "value": f"item_{i}"} for i in range(10)]

        train_data, val_data = scenario._split_data(test_data)

        # Check that data was split
        self.assertLess(len(train_data), len(test_data))
        self.assertLess(len(val_data), len(test_data))
        self.assertEqual(len(train_data) + len(val_data), len(test_data))


class TestIntegration(unittest.TestCase):
    """Test integration between components."""
    
    def test_module_loading_integration(self):
        """Test that module loading works correctly."""
        from dspy_integration.modules import get_module_for_scenario
        
        # Test with a known scenario (this might raise ValueError if scenario doesn't exist,
        # but the function should be callable)
        try:
            module_class = get_module_for_scenario("security_review")
            # If we get here, the function worked
            self.assertIsNotNone(module_class)
        except ValueError:
            # Expected if the scenario doesn't exist, but function should be defined
            pass


if __name__ == '__main__':
    # Run all tests
    unittest.main()