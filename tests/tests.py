#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
To run the test, run this in the this of repo:
python -m unittest discover
"""
import unittest

from redisworks import Root
from fakeredis import FakeStrictRedis
import logging
logging.disable(logging.CRITICAL)


class RedisworksTestCase(unittest.TestCase):

    """RedisWorks Tests."""
    def setUp(self):
        self.root = Root(redis=FakeStrictRedis)
        self.red = FakeStrictRedis()

    def test_save_child_str(self):
        num = 10
        self.root.part = num
        result = self.red.get('root.part')
        expected_result = Root.doformat(num)
        self.assertEqual(result, expected_result)

    def test_save_grandchild_str(self):
        self.root.haha.wahaha = "for real?"
        result = self.red.get('root.haha.wahaha')
        expected_result = b'for real?'
        self.assertEqual(result, expected_result)

    def test_save_child_set(self):
        value = {1, 2, 4}
        expected_result = set(Root.doformat(value))
        self.root.part = value
        result = self.red.smembers('root.part')
        self.assertEqual(result, expected_result)
