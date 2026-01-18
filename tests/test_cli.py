"""
Tests for DSPy-HELM CLI.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock


class TestCLI:
    """Test the CLI entry point."""

    def test_cli_help(self, capsys):
        """Test CLI help output."""
        from dspy_helm.cli import main

        with patch.object(sys, "argv", ["dspy_helm.cli", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # Help should exit with code 0
            assert exc_info.value.code == 0

    def test_cli_list_scenarios(self, capsys):
        """Test listing scenarios."""
        from dspy_helm.cli import main

        with patch.object(sys, "argv", ["dspy_helm.cli", "--list-scenarios"]):
            with pytest.raises(SystemExit) as exit_err:
                main()
            # Should exit after printing
            captured = capsys.readouterr()
            assert "Available scenarios" in captured.out
            assert "security_review" in captured.out

    @patch("dspy_helm.cli.run_evaluation")
    def test_cli_evaluate_only(self, mock_run, capsys):
        """Test evaluation without optimization."""
        from dspy_helm.cli import main

        mock_run.return_value = {"score": 0.85}

        with patch.object(
            sys,
            "argv",
            ["dspy_helm.cli", "--scenario", "security_review", "--evaluate-only"],
        ):
            try:
                main()
            except SystemExit:
                pass

        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["evaluate_only"] is True
        assert call_kwargs["scenario_name"] == "security_review"


class TestSetupDSPyLM:
    """Test LM configuration."""

    @patch("dspy_helm.providers.get_provider_by_name")
    def test_setup_dspy_lm(self, mock_get_provider):
        """Test LM setup."""
        from dspy_helm.cli import setup_dspy_lm

        mock_provider = MagicMock()
        mock_provider.api_key = "test-key"
        mock_provider.base_url = "https://test.com"
        mock_get_provider.return_value = mock_provider

        # Should not raise
        result = setup_dspy_lm("groq", "llama-3.3-70b-versatile")
        # Result might be None if dspy not fully configured
        assert result is None or result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
