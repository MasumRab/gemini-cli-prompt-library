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
    @patch("os.environ.get")
    def test_get_repository_env_var(self, mock_env_get):
        mock_env_get.return_value = "owner/repo"
        self.assertEqual(get_repository(), "owner/repo")

    @patch("os.environ.get")
    @patch("subprocess.run")
    def test_get_repository_git_config_https(self, mock_run, mock_env_get):
        mock_env_get.return_value = None
        mock_process = MagicMock()
        mock_process.stdout = "https://github.com/test-owner/test-repo.git\n"
        mock_run.return_value = mock_process
        self.assertEqual(get_repository(), "test-owner/test-repo")

    @patch("os.environ.get")
    @patch("subprocess.run")
    def test_get_repository_git_config_ssh(self, mock_run, mock_env_get):
        mock_env_get.return_value = None
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

    @patch("os.environ.get")
    @patch("scripts.update_active_context.fetch_paginated")
    @patch("scripts.update_active_context.get_repository")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_main_missing_token(
        self, mock_file, mock_get_repo, mock_fetch, mock_env_get
    ):
        mock_env_get.return_value = None
        main()

        # Verify degraded state is written
        mock_file().write.assert_called_once_with(
            "*GitHub Token missing - Context unavailable*\n"
        )
        mock_fetch.assert_not_called()

    @patch("os.environ.get")
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

    @patch("os.environ.get")
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

    @patch("os.environ.get")
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


if __name__ == "__main__":
    unittest.main()
