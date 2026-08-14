import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("check.py")
SPEC = importlib.util.spec_from_file_location("flow_challenge_check", MODULE_PATH)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK)


class ChallengeCheckerTests(unittest.TestCase):
    def test_comment_text_does_not_satisfy_rule(self):
        challenge = {
            "required": [{"label": "pipeline", "pattern": r"\|>"}],
        }
        failures = CHECK.check_patterns(challenge, "# use |> here\nreturn 0\n")
        self.assertEqual(failures, ["missing required syntax: pipeline"])

    def test_hash_inside_string_is_retained(self):
        source = 'println("# signal") # real comment\nreturn 0\n'
        stripped = CHECK.strip_flow_comments(source)
        self.assertIn('"# signal"', stripped)
        self.assertNotIn("real comment", stripped)

    def test_forbidden_text_in_comment_does_not_fail(self):
        challenge = {
            "required": [{"label": "match", "pattern": r"\bmatch\b"}],
            "forbidden": [{"label": "shortcut", "pattern": r"\bwhile\b"}],
        }
        failures = CHECK.check_patterns(
            challenge,
            "match value { default { return 0 } } # never use while\n",
        )
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
