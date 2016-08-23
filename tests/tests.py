#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

"""
To run the test, run this in the this of repo:
    python -m unittest discover

To run a specific test, run this from the root of repo:
    python -m unittest tests.tests.RedisworksTestCase.test_child_dict
"""
import unittest
from decimal import Decimal
import datetime

from redisworks import Root
from redisworks.redisworks import bTYPE_IDENTIFIER, bITEM_DIVIDER
from fakeredis import FakeStrictRedis
import logging
logging.disable(logging.CRITICAL)


class RedisworksTestCase(unittest.TestCase):

    """RedisWorks Tests."""
    def setUp(self):
        self.root = Root(redis=FakeStrictRedis)
        self.red = FakeStrictRedis()

    def tearDown(self):
        # Clear data in fakeredis.
        self.red.flushall()

    def test_nested_format(self):
        value = {1: 1, 2: {"a": "hello"}}
        result = Root.doformat(value)
        int_str = bTYPE_IDENTIFIER + b'num' + bITEM_DIVIDER + b'int' + bITEM_DIVIDER
        expected_result = {int_str + b'1': int_str + b'1',
                           int_str + b'2': bTYPE_IDENTIFIER +
                           b'dict' + bITEM_DIVIDER +
                           b'dict' + bITEM_DIVIDER + b'{"a": "hello"}'}
        self.assertEqual(result, expected_result)

    def test_numbers(self):
        today = datetime.date.today()
        now = datetime.datetime.utcnow()
        items = (10, 10.1, Decimal("10"), 10+1j, today, now)

        for val in items:
            self.root.part = val
            result = self.red.get('root.part')
            expected_result = Root.doformat(val)
            self.assertEqual(result, expected_result)
            # flushing dotobject local cache
            self.root.flush()
            self.assertEqual(self.root.part, val)

    def test_return_string(self):
        root2 = Root(redis=FakeStrictRedis, return_object=False)
        val = 11.1
        expected_result = b'11.1'
        root2.part = val
        # flushing dotobject local cache
        root2.flush()
        self.assertEqual(root2.part, expected_result)

    def test_grandchild(self):
        string = "for real?"
        self.root.haha.wahaha = string
        result = self.red.get('root.haha.wahaha')
        expected_result = Root.doformat(string)
        self.assertEqual(result, expected_result)
        self.root.flush()
        self.assertEqual(self.root.haha.wahaha, string)

    def test_child_set(self):
        value = {1, 2, 4}
        expected_result = set(Root.doformat(value))
        self.root.part_set = value
        result = self.red.smembers('root.part_set')
        self.assertEqual(result, expected_result)
        self.root.flush()
        self.assertEqual(self.root.part_set, value)

    def test_child_dict(self):
        value = {1: 1, 2: 2, 3: 4}
        expected_result = Root.doformat(value)
        self.root.part_dic = value
        result = self.red.hgetall('root.part_dic')
        self.assertEqual(result, expected_result)
        self.root.flush()
        self.assertEqual(self.root.part_dic, value)

    def test_child_nested_dict(self):
        value = {1: 1, 2: {"a": "hello"}, 3: 4}
        expected_result = Root.doformat(value)
        self.root.part = value
        result = self.red.hgetall('root.part')
        self.assertEqual(result, expected_result)
        self.root.flush()
        self.assertEqual(self.root.part, value)

    def test_child_iterable(self):
        value = [1, 3, "a"]
        expected_result = Root.doformat(value)
        self.root.part = value
        result = self.red.lrange("root.part", 0, -1)
        self.assertEqual(result, expected_result)
        self.root.flush()
        self.assertEqual(self.root.part, value)

    def test_child_nested_iterable(self):
        value = [1, 3, ["a", 3]]
        expected_result = Root.doformat(value)
        self.root.part = value
        result = self.red.lrange("root.part", 0, -1)
        self.assertEqual(result, expected_result)
        self.root.flush()
        self.assertEqual(self.root.part, value)
