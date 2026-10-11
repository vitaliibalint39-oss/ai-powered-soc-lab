import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import soc_assistant as s
from run_journal import RunJournal


class RunLoggingTests(unittest.TestCase):
    def test_success_record_has_no_event_details(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "runs.jsonl"
            journal = RunJournal(path)
            journal.set_counts(fetched=152, pending=132, selected=5, completed=5)
            result = journal.finish("success")
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["completed"], 5)
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("password", content)
            self.assertEqual(json.loads(content)["selected"], 5)

    def test_bad_count_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            journal = RunJournal(Path(td) / "runs.jsonl")
            with self.assertRaises(ValueError):
                journal.set_counts(fetched=-1)
            with self.assertRaises(ValueError):
                journal.set_counts(other=1)

    def test_partial_failure_nonzero(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(s, "RUN_LOG", Path(td) / "runs.jsonl"):
                def fake_run(journal):
                    journal.set_counts(fetched=4, selected=2, completed=1, failed=1)
                with patch.object(s, "run_soc", side_effect=fake_run):
                    with self.assertRaisesRegex(RuntimeError, "selected events failed"):
                        s.main()
                record=json.loads((Path(td) / "runs.jsonl").read_text(encoding="utf-8"))
                self.assertEqual(record["status"], "partial_failure")

    def test_unhandled_exception_records_failed(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(s, "RUN_LOG", Path(td) / "runs.jsonl"):
                with patch.object(s, "run_soc", side_effect=RuntimeError("simulated")):
                    with self.assertRaisesRegex(RuntimeError, "simulated"):
                        s.main()
                record=json.loads((Path(td) / "runs.jsonl").read_text(encoding="utf-8"))
                self.assertEqual(record["status"], "failed")

if __name__ == "__main__":
    unittest.main()
