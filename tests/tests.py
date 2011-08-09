from datetime import datetime
import unittest2

import riak
from timak.timelines import Timeline


class TimakTest(unittest2.TestCase):
    def setUp(self):
        self.key = self.bucket = "test-timak"
        self.c1 = riak.RiakClient()
        self.c2 = riak.RiakClient()

        self.b1 = self.c1.bucket(self.bucket)
        self.b2 = self.c2.bucket(self.bucket)

        self.c1.bucket(self.bucket).set_allow_multiples(True)

    def tearDown(self):
        # resolve conflicts / clear data between tests
        riak.RiakClient().bucket(self.bucket).get(self.key).delete()

    def test_allow_multiples(self):
        """
        Verify that sibling objects are created on a conflict.
        """
        o1 = self.b1.get(self.key)
        o2 = self.b2.get(self.key)

        o1.set_data("object-1")
        o1.store()
        o2.set_data("object-2")
        o2.store()

        conflicted = self.b1.get(self.key)
        self.assertEqual(conflicted.get_sibling_count(), 2)

    def test_max_items(self):
        """
        Verify items > max_items are removed.
        """
        timeline = Timeline(connection=self.c1, max_items=3)
        now = datetime.utcnow()

        timeline.add(self.key, 1, now)
        timeline.add(self.key, 2, now)
        timeline.add(self.key, 3, now)
        self.assertEqual(len(timeline.get(self.key)), 3)

        timeline.add(self.key, 4, now)
        self.assertEqual(len(timeline.get(self.key)), 3)
