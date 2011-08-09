import unittest2

import riak
from timak.timelines import Timeline


class TimakTest(unittest2.TestCase):
    def setUp(self):
        self.key = self.bucket = "test-timak"
        self.c1 = riak.RiakClient()
        self.c2 = riak.RiakClient()

        self.c1.bucket(self.bucket).set_allow_multiples(True)

    def tearDown(self):
        riak.RiakClient().bucket(self.bucket).get(self.key).delete()

    def test_add1(self):
        pass
