import unittest
from pathlib import Path

from reference_engine.smerc_f_profile_packet import (
    SMERC_F_PROFILE_PACKET_VERSION,
    build_profile_packet,
    render_markdown,
)


ACTIONS = Path("examples/financial_action_requests.json")


class SMERCFProfilePacketTests(unittest.TestCase):
    def test_builds_packet_across_financial_policies(self):
        packet = build_profile_packet(ACTIONS, policies=["conservative", "balanced", "permissive"])
        self.assertEqual(packet["version"], SMERC_F_PROFILE_PACKET_VERSION)
        self.assertEqual(packet["action_count"], 5)
        self.assertEqual(packet["profile"], "SMERC-F")
        self.assertIn("balanced", packet["state_distribution"])
        self.assertGreater(packet["high_restraint_count"], 0)
        self.assertEqual(len(packet["evaluations"]), 15)

    def test_signal_taxonomy_includes_governance_and_agent_signals(self):
        packet = build_profile_packet(ACTIONS)
        self.assertIn("governance", packet["signal_taxonomy"])
        self.assertIn("agent", packet["signal_taxonomy"])
        self.assertIn("reversibility", packet["signal_taxonomy"]["governance"])
        self.assertIn("agent_velocity", packet["signal_taxonomy"]["agent"])

    def test_markdown_blocks_financial_overclaims(self):
        markdown = render_markdown(build_profile_packet(ACTIONS, policies=["balanced"]))
        self.assertIn("not a banking product", markdown)
        self.assertIn("not a cryptocurrency", markdown)
        self.assertIn("Commercial Limits", markdown)
        self.assertIn("No automated money movement", markdown)

    def test_unknown_policy_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown financial policy"):
            build_profile_packet(ACTIONS, policies=["balanced", "unknown"])


if __name__ == "__main__":
    unittest.main()
