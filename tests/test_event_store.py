"""SQLite state regression tests. Run: python -m unittest discover -s tests -v"""
import json
import tempfile
import unittest
from pathlib import Path

from event_store import EventStore


class SQLiteEventStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / "state.sqlite3"
        self.legacy = self.root / "processed_events.json"
        self.reports = self.root / "reports"

    def open_store(self):
        store = EventStore(self.db, self.legacy)
        self.addCleanup(store.close)
        return store

    def test_legacy_migration_preserves_completed_ids(self):
        self.legacy.write_text(json.dumps(["idx:a", "idx:b", "idx:a"]), encoding="utf-8")
        s = self.open_store()
        self.assertEqual(s.completed_ids(), {"idx:a", "idx:b"})
        s.migrate_legacy()
        self.assertEqual(s.completed_ids(), {"idx:a", "idx:b"})
        self.assertTrue(self.legacy.exists())

    def test_completed_report_survives_restart_and_is_restored(self):
        s = self.open_store()
        s.save_report("idx:3", "incident_3.md", "# Report\n")
        s.close()
        s2 = self.open_store()
        self.assertEqual(s2.completed_ids(), {"idx:3"})
        self.assertEqual(s2.export_reports(self.reports), 1)
        self.assertEqual((self.reports / "incident_3.md").read_text(encoding="utf-8"), "# Report\n")
        self.assertEqual(s2.export_reports(self.reports), 0)

    def test_failed_event_can_be_retried(self):
        s = self.open_store()
        s.record_failure("idx:4", "temporary outage")
        self.assertNotIn("idx:4", s.completed_ids())
        s.save_report("idx:4", "incident_4.md", "Recovered")
        self.assertIn("idx:4", s.completed_ids())
        s.record_failure("idx:4", "later error")
        self.assertIn("idx:4", s.completed_ids())

    def test_corrupt_legacy_json_is_not_silently_ignored(self):
        self.legacy.write_text('{"not": "a list"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            EventStore(self.db, self.legacy)


if __name__ == "__main__":
    unittest.main()
