import json
import os
import unittest
from unittest.mock import patch, mock_open

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scripts.generate_manifest as gm


class TestGenerateManifest(unittest.TestCase):
    @patch('scripts.generate_manifest.os.path.isdir')
    @patch('scripts.generate_manifest.os.listdir')
    def test_description_scraping_and_ordering(self, mock_listdir, mock_isdir):
        # Setup mock file system
        mock_isdir.return_value = True

        def side_effect_listdir(path):
            if path == 'commands':
                return ['cat1', 'cat2']
            if path == 'commands/cat1':
                return ['b.toml', 'a.toml']
            if path == 'commands/cat2':
                return ['c.toml']
            return []

        mock_listdir.side_effect = side_effect_listdir

        # We have 3 files. We will mock open to return specific TOML content.
        # /cat1:b - No description, prompt has "# Title" -> Should be "Title"
        # /cat1:a - Has description "Explicit" -> Should be "Explicit"
        # /cat2:c - Neither -> Should be "No description available."

        file_contents = {
            'commands/cat1/b.toml': b'prompt = "# Title\\nBody"',
            'commands/cat1/a.toml': b'description = "Explicit"\nprompt = "# Ignore"',
            'commands/cat2/c.toml': b'prompt = "No headings here"',
        }

        def side_effect_open(filepath, mode='r'):
            if mode == 'rb':
                return mock_open(read_data=file_contents.get(filepath, b''))()
            return mock_open(read_data='template {{COMMAND_MANIFEST}}')()

        # Mock json dump to capture the generated manifest
        captured_manifest = {}
        def mock_json_dump(obj, fp, indent=None):
            captured_manifest.update(obj)

        with patch('scripts.generate_manifest.open', side_effect_open):
            with patch('scripts.generate_manifest.json.dump', side_effect=mock_json_dump):
                gm.generate_manifest()

        # Assertions
        # 1. Check description scraping priority
        self.assertEqual(captured_manifest.get('/cat1:a'), "Explicit")
        self.assertEqual(captured_manifest.get('/cat1:b'), "Title")
        self.assertEqual(captured_manifest.get('/cat2:c'), "No description available.")

        # 2. Check deterministic key ordering
        keys = list(captured_manifest.keys())
        expected_keys = ['/cat1:a', '/cat1:b', '/cat2:c']
        self.assertEqual(keys, expected_keys)

if __name__ == '__main__':
    unittest.main()