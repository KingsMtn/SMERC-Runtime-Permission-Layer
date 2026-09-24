import copy
import unittest

from reference_engine.adversarial_challenge_corpus import (
    CHALLENGES,
    build_corpus,
    run_corpus,
    simulated_control_executor,
    validate_corpus,
)


class AdversarialChallengeCorpusTests(unittest.TestCase):
    def setUp(self):
        self.corpus = build_corpus(
            environment_id="sandbox:assurance-suite",
            authorized_by="owner:security-lead",
            expires_at=1000,
        )

    def test_corpus_contains_six_priority_failure_modes(self):
        validated = validate_corpus(self.corpus, now=100)
        self.assertEqual(len(validated), 6)
        self.assertEqual({item["scenario_id"] for item in validated}, {item["id"] for item in CHALLENGES})

    def test_corpus_is_digest_bound(self):
        tampered = copy.deepcopy(self.corpus)
        tampered["scenarios"][0]["objective"] = "changed"
        with self.assertRaisesRegex(ValueError, "digest"):
            validate_corpus(tampered, now=100)

    def test_all_simulated_controls_holding_passes_suite(self):
        executors = {
            item["id"]: simulated_control_executor(holds=True, reason_code=item["expected"])
            for item in CHALLENGES
        }
        report = run_corpus(self.corpus, executors, now=100)
        self.assertEqual(report["suite_verdict"], "PASS")
        self.assertEqual(report["verdict_counts"], {"PASS": 6, "FAIL": 0, "INCOMPLETE": 0})
        self.assertEqual(len(report["suite_sha256"]), 64)

    def test_one_control_miss_fails_entire_suite(self):
        executors = {
            item["id"]: simulated_control_executor(
                holds=item["id"] != "rollback-residual",
                reason_code="CONTROL_RESPONSE",
            )
            for item in CHALLENGES
        }
        report = run_corpus(self.corpus, executors, now=100)
        self.assertEqual(report["suite_verdict"], "FAIL")
        self.assertEqual(report["verdict_counts"]["FAIL"], 1)

    def test_missing_executor_is_incomplete_not_pass(self):
        report = run_corpus(self.corpus, {}, now=100)
        self.assertEqual(report["suite_verdict"], "INCOMPLETE")
        self.assertEqual(report["verdict_counts"]["INCOMPLETE"], 6)
        self.assertTrue(all(item["stopped_reason"] == "executor_missing" for item in report["reports"]))

    def test_generated_corpus_never_allows_production(self):
        for scenario in self.corpus["scenarios"]:
            self.assertFalse(scenario["containment"]["production_access"])
            self.assertIn("production", scenario["containment"]["prohibited_targets"])


if __name__ == "__main__":
    unittest.main()

