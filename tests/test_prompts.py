import json
import unittest
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

class TestPrompts(unittest.TestCase):
    def test_prompts_directory_exists(self):
        self.assertTrue(PROMPTS_DIR.exists(), f"Prompts directory {PROMPTS_DIR} does not exist")

    def test_all_prompts_are_valid_json(self):
        json_files = list(PROMPTS_DIR.glob("*.json"))
        self.assertGreater(len(json_files), 0, "No JSON prompt files found")

        for file_path in json_files:
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    self.assertIsInstance(data, (dict, list), f"File {file_path.name} is not a valid JSON structure")
                except json.JSONDecodeError as e:
                    self.fail(f"Invalid JSON in {file_path.name}: {e}")

if __name__ == "__main__":
    unittest.main()
