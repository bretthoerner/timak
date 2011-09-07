from datetime import datetime, timedelta
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
        siblings = filter(bool, (s.get_data() for s in conflicted.get_siblings()))
        self.assertEqual(len(siblings), 2)

    def test_max_items(self):
        """
        Verify items > max_items are removed.
        """
        timeline = Timeline(connection=self.c1, bucket=self.bucket, max_items=3)
        now = datetime.utcnow()

        timeline.add(self.key, 1, now)
        timeline.add(self.key, 2, now)
        timeline.add(self.key, 3, now)
        self.assertEqual(len(timeline.get(self.key)), 3)

        timeline.add(self.key, 4, now)
        self.assertEqual(len(timeline.get(self.key)), 3)

    def test_delete(self):
        timeline = Timeline(connection=self.c1, bucket=self.bucket, max_items=3)
        now = datetime.utcnow()

        timeline.add(self.key, 1, now)
        self.assertEqual(len(timeline.get(self.key)), 1)

        timeline.delete(self.key, 1, now)
        self.assertEqual(len(timeline.get(self.key)), 0)

    def test_multi_writers(self):
        now = datetime.utcnow()

        t1 = Timeline(connection=self.c1, bucket=self.bucket, max_items=10)
        t2 = Timeline(connection=self.c2, bucket=self.bucket, max_items=10)

        t1.add(self.key, 1, now)
        t2.add(self.key, 2, now + timedelta(minutes=1))

        self.assertEqual(t1.get(self.key), [2, 1])

    def test_timestamp_scores(self):
        timeline = Timeline(connection=self.c1, bucket=self.bucket, max_items=3)
        now = datetime.utcnow()
        
        timeline.add(self.key, 1, now)
        timeline.add(self.key, 2, now + timedelta(seconds=1))
        timeline.add(self.key, 3, now + timedelta(seconds=2))
        results = timeline.get(self.key)
        self.assertEqual(len(results), 3)
        self.assertEquals(results[0], 3)
        self.assertEquals(results[1], 2)
        self.assertEquals(results[2], 1)

    def test_non_timestamp_scores(self):
        timeline = Timeline(connection=self.c1, bucket=self.bucket, max_items=3)

        timeline.add(self.key, 1, 3)
        timeline.add(self.key, 2, 2)
        timeline.add(self.key, 3, 1)
        results = timeline.get(self.key)
        self.assertEqual(len(results), 3)
        self.assertEquals(results[0], 1)
        self.assertEquals(results[1], 2)
        self.assertEquals(results[2], 3)

    def test_score_scoping(self):
        timeline = Timeline(connection=self.c1, bucket=self.bucket, max_items=3)

        timeline.add(self.key, 1, 3)
        timeline.add(self.key, 2, 2)
        timeline.add(self.key, 3, 1)
        results = timeline.get(self.key)
        self.assertEqual(len(results), 3)
        self.assertEquals(results[0], 1)
        self.assertEquals(results[1], 2)
        self.assertEquals(results[2], 3)
        
        timeline.add(self.key, 4, 0)
        results = timeline.get(self.key)
        self.assertEqual(len(results), 3)
        self.assertEquals(results[0], 1)
        self.assertEquals(results[1], 2)
        self.assertEquals(results[2], 3)

        timeline.add(self.key, 5, 5)
        results = timeline.get(self.key)
        self.assertEqual(len(results), 3)
        self.assertEquals(results[0], 5)
        self.assertEquals(results[1], 1)
        self.assertEquals(results[2], 2)
