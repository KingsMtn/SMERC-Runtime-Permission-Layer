import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SPARTaVocabularyTests(unittest.TestCase):
    def test_vocabulary_example_matches_schema_enums(self):
        schema = json.loads((ROOT / "schemas" / "smerc-sparta-vocabulary-v1.schema.json").read_text(encoding="utf-8"))
        vocabulary = json.loads((ROOT / "examples" / "sparta" / "sparta_vocabulary.json").read_text(encoding="utf-8"))

        self.assertEqual(vocabulary["version"], "smerc.sparta-vocabulary.v1")
        self.assertEqual(vocabulary["adapter_interpretation"]["unknown_term_behavior"], "fail_closed")

        for field in ["lifecycle_verbs", "route_states", "control_verbs", "evidence_events", "failure_reasons"]:
            allowed = set(schema["properties"][field]["items"]["enum"])
            values = set(vocabulary[field])
            self.assertEqual(values, allowed)
            self.assertEqual(len(values), len(vocabulary[field]))

    def test_non_executable_states_include_all_hold_block_and_review_paths(self):
        vocabulary = json.loads((ROOT / "examples" / "sparta" / "sparta_vocabulary.json").read_text(encoding="utf-8"))
        non_executable = set(vocabulary["adapter_interpretation"]["non_executable_states"])
        self.assertEqual(
            non_executable,
            {"PAUSE", "BLOCK", "REVIEW_REQUIRED", "BLOCKED_ESCALATION_UNAVAILABLE"},
        )
        self.assertNotIn("EXECUTE", non_executable)
        self.assertNotIn("CONSTRAINED_EXECUTE", non_executable)

    def test_docs_link_machine_readable_vocabulary(self):
        spec = (ROOT / "specification" / "SMERC_SPARTa_Vocabulary_v1.md").read_text(encoding="utf-8")
        framework = (ROOT / "docs" / "SPARTa_v2_Execution_Adapter_Framework.md").read_text(encoding="utf-8")
        router_spec = (ROOT / "specification" / "SMERC_SPARTa_Router_v1.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for text in [spec, framework, router_spec, readme]:
            self.assertIn("smerc.sparta-vocabulary.v1", text)
        self.assertIn("examples/sparta/sparta_vocabulary.json", spec)


if __name__ == "__main__":
    unittest.main()
