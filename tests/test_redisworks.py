#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To run the test, run this in the this of repo:
    python -m unittest discover

To run a specific test, run this from the root of repo:
    python -m unittest tests.tests.RedisworksTestCase.test_child_dict
"""

from decimal import Decimal
import datetime
from dot import LazyDot
from redisworks import Root
from redisworks.redisworks import bTYPE_IDENTIFIER, bITEM_DIVIDER
from fakeredis import FakeStrictRedis
import logging
logging.disable(logging.CRITICAL)


class TestRedisworks:

    """RedisWorks Tests."""
    def setup_method(self):
        self.red = FakeStrictRedis()
        self.root = Root(conn=self.red)

    def teardown_method(self):
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
        assert result == expected_result

    def test_dict_reassignement(self):
        value1 = {"a": "b"}
        value2 = {"c": "d"}

        self.root.body = value1
        self.root.body = value2
        self.root.flush()

        assert self.root.body == value2


    def test_numbers(self):
        today = datetime.date.today()
        now = datetime.datetime.utcnow()
        items = (10, 10.1, Decimal("10"), 10+1j, today, now)

        for val in items:
            self.root.part = val
            result = self.red.get('root.part')
            expected_result = Root.doformat(val)
            assert result == expected_result
            # flushing dotobject local cache
            self.root.flush()
            assert self.root.part == val

    def test_return_string(self):
        root2 = Root(redis=FakeStrictRedis, return_object=False)
        val = 11.1
        expected_result = b'11.1'
        root2.part = val
        # flushing dotobject local cache
        root2.flush()
        assert root2.part == expected_result

    def test_grandchild(self):
        string = "for real?"
        self.root.haha.wahaha = string
        result = self.red.get('root.haha.wahaha')
        expected_result = Root.doformat(string)
        assert result == expected_result
        self.root.flush()
        assert self.root.haha.wahaha == string
        assert self.root['haha.wahaha'] == string

    def test_child_set(self):
        value = {1, 2, 4}
        expected_result = set(Root.doformat(value))
        self.root.part_set = value
        result = self.red.smembers('root.part_set')
        assert result == expected_result
        self.root.flush()
        assert self.root.part_set == value

    def test_pattern_containing_string(self):
        value = f"{bTYPE_IDENTIFIER}some randomg string{bTYPE_IDENTIFIER}"
        self.root.value = value
        self.root.flush()
        assert self.root.value == value

    def test_child_dict(self):
        value = {1: 1, 2: 2, 3: 4}
        expected_result = Root.doformat(value)
        self.root.part_dic = value
        result = self.red.hgetall('root.part_dic')
        assert result == expected_result
        self.root.flush()
        assert self.root.part_dic == value

    def test_child_nested_dict(self):
        value = {1: 1, 2: {"a": "hello"}, 3: 4}
        expected_result = Root.doformat(value)
        self.root.part = value
        result = self.red.hgetall('root.part')
        assert result == expected_result
        self.root.flush()
        assert self.root.part == value

    def test_child_iterable(self):
        value = [1, 3, "a"]
        expected_result = Root.doformat(value)
        self.root.part = value
        result = self.red.lrange("root.part", 0, -1)
        assert result == expected_result
        self.root.flush()
        assert self.root.part == value

    def test_child_nested_iterable(self):
        value = [1, 3, ["a", 3]]
        expected_result = Root.doformat(value)
        self.root.part = value
        result = self.red.lrange("root.part", 0, -1)
        assert result == expected_result
        self.root.flush()
        assert self.root.part == value

    def test_many_different_children_types(self):
        set_value = {1, 2, 4}
        self.root.part_set = set_value
        dict_value = {1: 1, 2: {"a": 1}}
        self.root.part_dict = dict_value
        list_value = [1, ["b", 3]]
        self.root.part_list = list_value
        self.root.flush()
        assert self.root.part_set == set_value
        assert self.root.part_dict == dict_value
        assert self.root.part_list == list_value

    def test_many_different_children_types2(self):
        mylist = [1, 3, 4]
        self.root.my.list = mylist
        some_date = datetime.datetime(2016, 8, 22, 10, 3, 19)
        self.root.time = some_date
        mydict = {1: 1, "a": "b"}
        self.root.the.mapping.example = mydict
        self.root.flush()
        assert self.root.my.list == mylist
        assert self.root.time == some_date
        assert self.root.the.mapping.example == mydict

    def test_change_key_type(self):
        mylist = [1, 3, 4]
        self.root.something = mylist
        st = "string"
        self.root.something = st
        assert self.root.something == st

    def test_number_comparison(self):
        self.root.num = 10
        num = self.root.num
        assert isinstance(num, LazyDot)
        assert num > 8
        assert num < 11
        assert num <= 12
        assert num >= 10
        assert num <= 10

    def test_number_math(self):
        self.root.num = 10
        num = self.root.num
        assert isinstance(num, LazyDot)
        assert num * 2 == 20

    def test_saving_set_removed_the_old_one(self):
        self.root.myset = {1, 2, 3}
        self.root.myset = {4, 5}
        self.root.flush()
        assert self.root.myset == {4, 5}

    def test_saving_list_removed_the_old_one(self):
        self.root.myset = [1, 2, 3]
        self.root.myset = [4, 5]
        self.root.flush()
        assert self.root.myset == [4, 5]

    def test_reverse_operations(self):
        self.root.num = 10
        assert self.root.num + 1 == 11
        assert 1 + self.root.num == 11
        assert self.root.num > 9
        assert self.root.num < 12
        assert 9 < self.root.num
        assert 12 > self.root.num

    def test_boolean_storage_operations(self):
        self.root.true_variable = True
        self.root.false_variable = False

        self.root.flush()

        assert self.root.true_variable == True
        assert self.root.false_variable == False
    
    def test_redis_key_pattern_operations(self):
        VALUE = "___=random__string___"
        self.root.string = VALUE
        self.root.flush()

        assert self.root.string == VALUE
