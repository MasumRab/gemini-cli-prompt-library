.PHONY: dev audit

dev:
	python -m dspy_integration.cli

audit:
	python3 scripts/perform_audit.py
