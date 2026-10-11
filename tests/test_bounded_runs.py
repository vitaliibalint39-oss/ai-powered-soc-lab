import os
import unittest
from unittest.mock import patch

from soc_assistant import get_run_limit


class BoundedRunTests(unittest.TestCase):
    def test_default_is_five(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_run_limit(), 5)

    def test_custom_limit(self):
        with patch.dict(os.environ, {"SOC_MAX_EVENTS": "2"}):
            self.assertEqual(get_run_limit(), 2)

    def test_invalid_limits_rejected(self):
        for value in ("0", "21", "-1", "abc", "1.2", ""):
            with self.subTest(value=value):
                with patch.dict(os.environ, {"SOC_MAX_EVENTS": value}):
                    with self.assertRaises(ValueError):
                        get_run_limit()
