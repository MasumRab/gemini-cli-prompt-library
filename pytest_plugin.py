# pytest_plugin.py - A pytest plugin to mock problematic modules
import sys
from unittest.mock import MagicMock

def pytest_configure(config):
    """Configure pytest - mock modules BEFORE any test collection happens."""
    
    # List of modules that cause Bus error or import issues
    modules_to_mock = {
        # tokenizers causes Bus error
        'tokenizers': MagicMock(),
        'tokenizers.models': MagicMock(),
        'tokenizers.decoders': MagicMock(),
        'tokenizers.normalizers': MagicMock(),
        'tokenizers.pre_tokenizers': MagicMock(),
        'tokenizers.trainers': MagicMock(),
        'tokenizers.implementations': MagicMock(),
        
        # litellm has import issues
        'litellm': MagicMock(),
        'litellm._logging': MagicMock(),
        'litellm.main': MagicMock(),
        'litellm.utils': MagicMock(),
        'litellm.utils.py': MagicMock(),
        'litellm.utils.py.httpx': MagicMock(),
        'litellm.llms': MagicMock(),
        'litellm.llms.custom_httpx': MagicMock(),
        'litellm.completion': MagicMock(),
        'litellm.completion_factory': MagicMock(),
        'litellm.embedding': MagicMock(),
        'litellm.aiosettings': MagicMock(),
        'litellm.exceptions': MagicMock(),
        'litellm.responses': MagicMock(),
        'litellm.main': MagicMock(),
        
        # httpx
        'httpx': MagicMock(),
        'httpx._client': MagicMock(),
        'httpx._transports': MagicMock(),
        'httpx._transports.default': MagicMock(),
        'httpx._urls': MagicMock(),
        'httpx._auth': MagicMock(),
        'httpx._models': MagicMock(),
        
        # anyio 
        'anyio': MagicMock(),
        'anyio._backends': MagicMock(),
        'anyio._backends._asyncio': MagicMock(),
        
        # other problematic imports
        'jinja2': MagicMock(),
        'yaml': MagicMock(),
        'pydantic': MagicMock(),
        'pydantic.fields': MagicMock(),
        'pydantic.main': MagicMock(),
        'pydantic.generics': MagicMock(),
        'pydantic.typing': MagicMock(),
        'pydantic._typing': MagicMock(),
        'pydantic.main': MagicMock(),
        'pydantic.fields': MagicMock(),
        'jsonref': MagicMock(),
        
        # openai
        'openai': MagicMock(),
        'openai.types': MagicMock(),
        'openai.types.batch': MagicMock(),
        'openai._models': MagicMock(),
        'openai._compat': MagicMock(),
    }
    
    for mod_name, mock in modules_to_mock.items():
        if mod_name not in sys.modules:
            sys.modules[mod_name] = mock
    
    # Now we need to mock dspy completely before it's imported
    # Create a mock that has all the necessary attributes
    dspy_mock = MagicMock()
    
    # Mock settings
    dspy_mock.settings = MagicMock()
    dspy_mock.settings.lm = None
    dspy_mock.settings.configure = MagicMock()
    
    # Mock Example class that can accept kwargs
    class MockExample:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        def with_inputs(self, *fields):
            return self
    
    # Mock Prediction class
    class MockPrediction:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    # Mock Signature - DSPy uses BaseModel which has __fields__
    class MockField:
        def __init__(self, **kwargs):
            pass
    
    class MockSignature:
        __fields__ = {'code': MockField(), 'review': MockField()}
    
    # Mock common classes
    dspy_mock.Signature = MockSignature
    dspy_mock.Module = type("Module", (), {})
    dspy_mock.Module.__init__ = lambda self: None
    dspy_mock.Module.forward = lambda self, *args, **kwargs: MagicMock()
    
    dspy_mock.Example = MockExample
    dspy_mock.Prediction = MockPrediction
    
    # Mock functional components
    dspy_mock.ChainOfThought = MagicMock(return_value=MagicMock())
    dspy_mock.Predict = MagicMock(return_value=MagicMock())
    dspy_mock.CoT = dspy_mock.ChainOfThought
    
    # Mock evaluators
    dspy_mock.Evaluate = MagicMock()
    dspy_mock.evaluate = MagicMock()
    
    # Mock teleprompt
    dspy_mock.teleprompt = MagicMock()
    dspy_mock.teleprompt.BootstrapFewShot = MagicMock()
    dspy_mock.teleprompt.MIPROv2 = MagicMock()
    
    # Mock functional
    dspy_mock.functional = MagicMock()
    
    # Mock InputField and OutputField
    dspy_mock.InputField = MockField
    dspy_mock.OutputField = MockField
    
    # Set up dspy mock in sys.modules
    sys.modules['dspy'] = dspy_mock
    sys.modules['dspy.predict'] = MagicMock()
    sys.modules['dspy.evaluate'] = MagicMock()
    sys.modules['dspy.teleprompt'] = MagicMock()
    sys.modules['dspy.functional'] = MagicMock()
    sys.modules['dspy.primitives'] = MagicMock()
    sys.modules['dspy.primitives.module'] = MagicMock()
    sys.modules['dspy.primitives.base_module'] = MagicMock()
    sys.modules['dspy.utils'] = MagicMock()
    sys.modules['dspy.utils.saving'] = MagicMock()
    sys.modules['dspy.streaming'] = MagicMock()
    sys.modules['dspy.streaming.messages'] = MagicMock()
    sys.modules['dspy.streaming.streamify'] = MagicMock()
    sys.modules['dspy.streaming.streaming_listener'] = MagicMock()
    sys.modules['dspy.adapters'] = MagicMock()
    sys.modules['dspy.adapters.chat_adapter'] = MagicMock()
    sys.modules['dspy.clients'] = MagicMock()
    sys.modules['dspy.clients.lm'] = MagicMock()
    sys.modules['dspy.predict.aggregation'] = MagicMock()
    sys.modules['dspy.predict.chain_of_thought'] = MagicMock()
    sys.modules['dspy.evaluate.auto_evaluation'] = MagicMock()
