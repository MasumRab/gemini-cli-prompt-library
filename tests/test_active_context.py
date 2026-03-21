import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the sys.path so we can import scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests  # noqa: E402
from scripts.update_active_context import (  # noqa: E402
    get_repository,
    fetch_paginated,
    main,
)


class TestActiveContextUpdater(unittest.TestCase):
    @patch("scripts.update_active_context.os.environ.get")
    def test_get_repository_env_var(self, mock_env_get):
        mock_env_get.return_value = "owner/repo"
        self.assertEqual(get_repository(), "owner/repo")

    @patch("scripts.update_active_context.os.environ.get")
    @patch("scripts.update_active_context.shutil.which")
    @patch("subprocess.run")
    def test_get_repository_git_config_https(self, mock_run, mock_which, mock_env_get):
        mock_env_get.return_value = None
        mock_which.return_value = "/usr/bin/git"
        mock_process = MagicMock()
        mock_process.stdout = "https://github.com/test-owner/test-repo.git\n"
        mock_run.return_value = mock_process
        self.assertEqual(get_repository(), "test-owner/test-repo")

    @patch("scripts.update_active_context.os.environ.get")
    @patch("scripts.update_active_context.shutil.which")
    @patch("subprocess.run")
    def test_get_repository_git_config_ssh(self, mock_run, mock_which, mock_env_get):
        mock_env_get.return_value = None
        mock_which.return_value = "/usr/bin/git"
        mock_process = MagicMock()
        mock_process.stdout = "git@github.com:test-owner2/test-repo2.git\n"
        mock_run.return_value = mock_process
        self.assertEqual(get_repository(), "test-owner2/test-repo2")

    @patch("requests.get")
    def test_fetch_paginated_single_page(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": 1}, {"id": 2}]
        mock_response.headers = {}
        mock_get.return_value = mock_response

        results = fetch_paginated("http://example.com/api", {})
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], 1)

    @patch("requests.get")
    def test_fetch_paginated_multi_page(self, mock_get):
        # Setup responses for two pages
        response1 = MagicMock()
        response1.json.return_value = [{"id": 1}]
        response1.headers = {"Link": '<http://example.com/api?page=2>; rel="next"'}

        response2 = MagicMock()
        response2.json.return_value = [{"id": 2}]
        response2.headers = {}

        mock_get.side_effect = [response1, response2]

        results = fetch_paginated("http://example.com/api", {})
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[1]["id"], 2)
        self.assertEqual(mock_get.call_count, 2)

    @patch("scripts.update_active_context.os.environ.get")
    @patch("scripts.update_active_context.fetch_paginated")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_main_missing_token(self, mock_file, mock_fetch, mock_env_get):
        mock_env_get.return_value = None
        main()

        # Verify degraded state is written
        mock_file().write.assert_called_once_with(
            "*GitHub Token missing - Context unavailable*\n"
        )
        mock_fetch.assert_not_called()

    @patch("scripts.update_active_context.os.environ.get")
    @patch("scripts.update_active_context.get_repository")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_main_missing_repo(self, mock_file, mock_get_repo, mock_env_get):
        mock_env_get.return_value = "fake_token"
        mock_get_repo.return_value = ""
        main()

        # Verify degraded state is written
        mock_file().write.assert_called_once_with(
            "*Repository cannot be determined - Context unavailable*\n"
        )

    @patch("scripts.update_active_context.os.environ.get")
    @patch("scripts.update_active_context.get_repository")
    @patch("scripts.update_active_context.fetch_paginated")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_main_success_with_prs(
        self, mock_file, mock_fetch, mock_get_repo, mock_env_get
    ):
        mock_env_get.return_value = "fake_token"
        mock_get_repo.return_value = "owner/repo"

        # Mock PRs
        mock_prs = [
            {
                "number": 101,
                "title": "Fix bug",
                "html_url": "https://github.com/owner/repo/pull/101",
                "user": {"login": "dev1"},
            }
        ]

        # Mock Files
        mock_files = [{"filename": "src/main.py"}, {"filename": "README.md"}]

        mock_fetch.side_effect = [mock_prs, mock_files]

        main()

        # Collect all writes
        written_content = "".join(
            [call.args[0] for call in mock_file().write.call_args_list]
        )

        self.assertIn("# Active GitHub Context", written_content)
        self.assertIn(
            "| [#101](https://github.com/owner/repo/pull/101) | Fix bug | @dev1 | `src/main.py`<br>`README.md` |",
            written_content,
        )
        self.assertEqual(mock_fetch.call_count, 2)

    @patch("scripts.update_active_context.os.environ.get")
    @patch("scripts.update_active_context.get_repository")
    @patch("scripts.update_active_context.fetch_paginated")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_main_api_failure(self, mock_file, mock_fetch, mock_get_repo, mock_env_get):
        mock_env_get.return_value = "fake_token"
        mock_get_repo.return_value = "owner/repo"

        # Simulate API timeout/failure
        mock_fetch.side_effect = requests.RequestException("API timeout")

        main()

        written_content = "".join(
            [call.args[0] for call in mock_file().write.call_args_list]
        )
        self.assertIn(
            "*GitHub API request failed - Context unavailable*", written_content
        )

    @patch("scripts.update_active_context.os.environ.get")
    @patch("scripts.update_active_context.get_repository")
    @patch("scripts.update_active_context.fetch_paginated")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_main_invalid_max_pr_process(
        self, mock_file, mock_fetch, mock_get_repo, mock_env_get
    ):
        # We need to reload the module to trigger the parse of MAX_PR_PROCESS
        # but since that happens at import time, we'll just mock the value directly for the test
        import scripts.update_active_context

        original_max = scripts.update_active_context.MAX_PR_PROCESS

        # Manually force the fallback behavior for the test
        scripts.update_active_context.MAX_PR_PROCESS = 1

        mock_env_get.return_value = "fake_token"
        mock_get_repo.return_value = "owner/repo"

        # Create 2 PRs, but MAX is 1
        mock_prs = [
            {
                "number": 1,
                "title": "PR 1",
                "html_url": "url1",
                "user": {"login": "dev"},
            },
            {
                "number": 2,
                "title": "PR 2",
                "html_url": "url2",
                "user": {"login": "dev"},
            },
        ]

        mock_files = [{"filename": "file.txt"}]

        # First call gets PRs, second call gets files for PR1
        mock_fetch.side_effect = [mock_prs, mock_files]

        main()

        written_content = "".join(
            [call.args[0] for call in mock_file().write.call_args_list]
        )

        # Only PR 1 should be processed and written
        self.assertIn("PR 1", written_content)
        self.assertNotIn("PR 2", written_content)
        self.assertEqual(
            mock_fetch.call_count, 2
        )  # 1 for PRs list, 1 for the *single* PR's files

        # Restore
        scripts.update_active_context.MAX_PR_PROCESS = original_max

    @patch("scripts.update_active_context.os.environ.get")
    @patch("scripts.update_active_context.get_repository")
    @patch("scripts.update_active_context.fetch_paginated")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_main_markdown_sanitization(
        self, mock_file, mock_fetch, mock_get_repo, mock_env_get
    ):
        mock_env_get.return_value = "fake_token"
        mock_get_repo.return_value = "owner/repo"

        # PR with dangerous characters
        mock_prs = [
            {
                "number": 999,
                "title": "Fix | critical \n bug",
                "html_url": "url",
                "user": {"login": "hacker|dev"},
            }
        ]

        mock_files = [{"filename": "src/|file\n.py"}]

        mock_fetch.side_effect = [mock_prs, mock_files]

        main()

        written_content = "".join(
            [call.args[0] for call in mock_file().write.call_args_list]
        )

        # Verify sanitization
        self.assertIn("Fix &#124; critical   bug", written_content)
        self.assertIn("hacker&#124;dev", written_content)
        self.assertIn("`src/&#124;file .py`", written_content)
        self.assertNotIn("\n bug", written_content)


if __name__ == "__main__":
    unittest.main()
