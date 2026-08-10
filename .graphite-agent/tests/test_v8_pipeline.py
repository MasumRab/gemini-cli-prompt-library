#!/usr/bin/env python3
"""
Graphite Agent V8 Pipeline Integration Tests

Tests the unified pipeline from discover -> execute.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import subprocess
import sys


class TestV8PipelineIntegration:
    """Integration tests for V8 unified pipeline."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary git repository for testing."""
        temp_dir = tempfile.mkdtemp(prefix='gt_v8_test_')
        repo_path = Path(temp_dir)
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@v8.test'], 
                      cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'V8 Test'], 
                      cwd=repo_path, check=True, capture_output=True)
        
        # Copy graphite-agent directory
        agent_src = Path('.graphite-agent')
        agent_dst = repo_path / '.graphite-agent'
        shutil.copytree(agent_src, agent_dst)
        
        # Create a simple Python file
        (repo_path / 'test_file.py').write_text('def hello():\n    return "world"\n')
        
        # Initial commit
        subprocess.run(['git', 'add', '.'], cwd=repo_path, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], 
                      cwd=repo_path, check=True)
        
        yield repo_path
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def v8_context(self):
        """Create a V8 RunContext for testing."""
        sys.path.insert(0, str(Path('.graphite-agent/tools')))
        from lib.run_context import RunContext
        return RunContext()

    def test_pipeline_discover_stage(self, temp_repo, v8_context):
        """Test that discover stage runs successfully."""
        from tools.discover_repo import discover_repo
        from tools.replay_risk import assess_replay_risk
        from tools.validate_replay import validate_replay
        
        # Run discovery
        inventory = discover_repo()
        assert inventory is not None
        assert 'branches' in inventory
        
        # Run replay risk assessment
        risk = assess_replay_risk(inventory)
        assert risk is not None
        assert 'overall_risk' in risk
        
        # Run validation
        validation = validate_replay(inventory, risk)
        assert validation is not None
        assert 'status' in validation

    def test_pipeline_analyse_stage(self, v8_context):
        """Test that analyse stage runs successfully."""
        from tools.analyse import analyse_outputs
        
        # Run analysis
        results = analyse_outputs()
        assert results is not None
        assert 'snapshot' in results
        assert 'targets' in results
        assert 'roots' in results
        assert 'stack_order' in results

    def test_run_context_creation(self, v8_context):
        """Test RunContext creation and basic operations."""
        assert v8_context.run_id is not None
        assert len(v8_context.run_id) == 8  # Truncated UUID
        assert v8_context.agent_dir.exists()
        assert v8_context.outputs_dir.exists()

    def test_run_context_save_load(self, v8_context):
        """Test saving and loading run context."""
        # Save state
        v8_context.save_state()
        
        # Verify file exists
        context_file = v8_context.run_dir / 'run_context.json'
        assert context_file.exists()
        
        # Load state
        loaded = RunContext.load_state(v8_context.run_id)
        assert loaded.run_id == v8_context.run_id

    def test_run_context_latest(self, v8_context):
        """Test latest context operations."""
        # Save to latest
        v8_context.save_latest_state()
        
        # Load latest
        latest = RunContext.load_latest()
        assert latest is not None

    def test_run_context_outputs(self, v8_context):
        """Test output file operations."""
        test_data = {'test': 'value'}
        
        # Save output
        path = v8_context.save_output('test_output.json', test_data)
        assert path.exists()
        
        # Verify latest also has it
        latest_path = v8_context.latest_dir / 'test_output.json'
        assert latest_path.exists()

    def test_staleness_detection(self, v8_context):
        """Test staleness detection."""
        # Initially stale (never validated)
        assert v8_context.is_stale() is True
        
        # Mark as validated
        v8_context.mark_validated()
        assert v8_context.is_stale() is False

    def test_stage_status(self, v8_context):
        """Test stage completion status."""
        # Analyse stage should have snapshot
        status = v8_context.get_stage_status('analyse')
        assert 'stage' in status
        assert 'completed' in status
        assert 'missing' in status


class TestV8PipelineGating:
    """Test pipeline stage gating."""

    def test_discover_before_analyse(self):
        """Test that analyse requires discover to complete first."""
        # This will be implemented in main.py
        pass  # TODO: Implement when main.py is updated

    def test_analyse_before_triage(self):
        """Test that triage requires analyse to complete first."""
        pass  # TODO: Implement when main.py is updated

    def test_validate_before_execute(self):
        """Test that execute requires validate to complete first."""
        pass  # TODO: Implement when main.py is updated


class TestV8PipelineFiles:
    """Test file existence and structure."""

    def test_required_v8_files_exist(self):
        """Verify all required V8 files exist."""
        required_files = [
            'tools/main.py',
            'tools/lib/git_core.py',
            'tools/lib/run_context.py',
            'config/repo.yaml',
        ]
        
        for file in required_files:
            path = Path('.graphite-agent') / file
            assert path.exists(), f"Missing required file: {file}"

    def test_v8_tools_directory_structure(self):
        """Verify V8 tools directory structure."""
        tools_dir = Path('.graphite-agent/tools')
        lib_dir = tools_dir / 'lib'
        tests_dir = Path('.graphite-agent/tests')
        
        assert tools_dir.exists()
        assert lib_dir.exists()
        assert tests_dir.exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
