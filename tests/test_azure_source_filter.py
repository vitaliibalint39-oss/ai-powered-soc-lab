"""Offline checks for selecting the Azure Wazuh agent and optional rule filter."""
import os
import unittest
from unittest.mock import Mock, patch

import soc_assistant


def empty_page():
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"_scroll_id": "test-scroll", "hits": {"hits": []}}
    return response


class AzureSourceFilterTests(unittest.TestCase):
    def test_default_local_agent_kept(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(soc_assistant.get_agent_name(), "ubuntu-soc")
            self.assertEqual(soc_assistant.get_rule_id(), "")

    def test_explicit_azure_agent_and_rule_filter_in_query(self):
        with patch.dict(os.environ, {"SOC_AGENT_NAME": "azure-devops-lab", "SOC_RULE_ID": "5710"}, clear=True):
            session = Mock()
            session.post.return_value = empty_page()
            session.delete.return_value = empty_page()
            self.assertEqual(list(soc_assistant.get_alerts(session)), [])
            query = session.post.call_args.kwargs["json"]["query"]["bool"]["filter"]
            self.assertIn({"term": {"agent.name": "azure-devops-lab"}}, query)
            self.assertIn({"term": {"rule.id": "5710"}}, query)
            self.assertIn({"range": {"rule.level": {"gte": 5}}}, query)
            self.assertIn("rule.id", session.post.call_args.kwargs["json"]["_source"])

    def test_local_default_has_no_rule_filter(self):
        with patch.dict(os.environ, {}, clear=True):
            session = Mock()
            session.post.return_value = empty_page()
            session.delete.return_value = empty_page()
            list(soc_assistant.get_alerts(session))
            filters = session.post.call_args.kwargs["json"]["query"]["bool"]["filter"]
            self.assertEqual(len(filters), 2)
            self.assertEqual(filters[0], {"term": {"agent.name": "ubuntu-soc"}})

    def test_invalid_agent_and_rule_are_rejected(self):
        for agent in ("", "*", "name with spaces", "../bad", "a" * 129):
            with self.subTest(agent=agent), patch.dict(os.environ, {"SOC_AGENT_NAME": agent}, clear=True):
                self.assertRaises(ValueError, soc_assistant.get_agent_name)
        for rule in ("foo", "*", "-1", "5710 OR 1", "１２３", "12345678901"):
            with self.subTest(rule=rule), patch.dict(os.environ, {"SOC_RULE_ID": rule}, clear=True):
                self.assertRaises(ValueError, soc_assistant.get_rule_id)


if __name__ == "__main__":
    unittest.main()
