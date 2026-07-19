import sys
import unittest
from unittest.mock import Mock, patch

from tools.api.jules_api_client import JulesAPIClient, jules_request


class _FakeResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


class JulesAPIClientTest(unittest.TestCase):
    def test_jules_request_accepts_empty_success_response(self):
        with patch("urllib.request.urlopen", return_value=_FakeResponse(b"")):
            response = jules_request(
                "sessions/123:sendMessage",
                method="POST",
                body={"prompt": "hello"},
                api_key="test-key",
            )

        self.assertEqual(response, {})

    def test_send_message_uses_documented_custom_method_and_prompt_body(self):
        client = JulesAPIClient(api_key="test-key")
        client._request = Mock(return_value={})

        response = client.send_message("123", "hello")

        self.assertEqual(response, {})
        client._request.assert_called_once_with(
            "sessions/123:sendMessage", method="POST", body={"prompt": "hello"}
        )

    def test_send_message_preserves_resource_name(self):
        client = JulesAPIClient(api_key="test-key")
        client._request = Mock(return_value={})

        client.send_message("sessions/123", "hello")

        client._request.assert_called_once_with(
            "sessions/123:sendMessage", method="POST", body={"prompt": "hello"}
        )


if __name__ == "__main__":
    unittest.main()
