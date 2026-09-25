import sys
import os
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from finance_tracker.id_generator import get_next_id


class TestIdGenerator(unittest.TestCase):

    def test_ids_increment_each_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "next_id.txt")
            self.assertEqual(get_next_id(path), 1)
            self.assertEqual(get_next_id(path), 2)
            self.assertEqual(get_next_id(path), 3)

    def test_ids_are_not_reused_after_a_simulated_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "next_id.txt")
            get_next_id(path)  # 1
            get_next_id(path)  # 2
            # A "restart" just means a fresh call reads the same file again.
            # It should continue from 3, not start over from 1.
            self.assertEqual(get_next_id(path), 3)


if __name__ == "__main__":
    unittest.main()