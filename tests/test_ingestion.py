"""Mocked tests for OpenSearch scroll pagination.

Run: python -m unittest discover -s tests -v
"""
import unittest
from unittest.mock import Mock

import soc_assistant


def page(ids, scroll_id="cursor"):
    return {
        "_scroll_id": scroll_id,
        "hits": {"hits": [
            {"_index": "wazuh-alerts-test", "_id": str(i), "_source": {"rule": {"level": 5}}}
            for i in ids
        ]},
    }


def response(payload):
    result = Mock()
    result.raise_for_status.return_value = None
    result.json.return_value = payload
    return result


class ScrollPaginationTests(unittest.TestCase):
    def test_reads_more_than_twenty_without_loss(self):
        session = Mock()
        session.post.side_effect = [
            response(page(range(20), "a")),
            response(page(range(20, 45), "b")),
            response(page([], "c")),
        ]
        session.delete.return_value = response({})
        items = list(soc_assistant.get_alerts(session))
        self.assertEqual(len(items), 45)
        self.assertEqual(len({eid for eid, _ in items}), 45)
        self.assertEqual(session.post.call_count, 3)
        self.assertEqual(session.delete.call_count, 1)
        self.assertEqual(session.delete.call_args.kwargs["json"]["scroll_id"], ["c"])

    def test_empty_results_cleanup(self):
        session = Mock()
        session.post.return_value = response(page([], "first"))
        session.delete.return_value = response({})
        self.assertEqual(list(soc_assistant.get_alerts(session)), [])
        session.delete.assert_called_once()

    def test_missing_scroll_id_fails_not_silently(self):
        session = Mock()
        session.post.return_value = response({"hits": {"hits": []}})
        with self.assertRaises(RuntimeError):
            list(soc_assistant.get_alerts(session))

    def test_subsequent_page_error_propagates_and_cleans_up(self):
        session = Mock()
        failing = response({})
        failing.raise_for_status.side_effect = RuntimeError("indexer unavailable")
        session.post.side_effect = [response(page(range(20))), failing]
        session.delete.return_value = response({})
        with self.assertRaisesRegex(RuntimeError, "indexer unavailable"):
            list(soc_assistant.get_alerts(session))
        session.delete.assert_called_once()


if __name__ == "__main__":
    unittest.main()
