#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dot import Dot
from redis import StrictRedis
from redisworks.helper import py3
import datetime
from decimal import Decimal
from collections import Iterable
from collections import MutableMapping
import json

sets = (set, frozenset)
if py3:  # pragma: no cover
    from builtins import int
    strings = (str, bytes)  # which are both basestring
    numbers = (int, float, complex, datetime.datetime, datetime.date, Decimal)
    items = 'items'
else:  # pragma: no cover
    strings = (str, unicode)
    numbers = (int, float, long, complex, datetime.datetime, datetime.date, Decimal)
    items = 'iteritems'


TYPE_FORMATS = {
    numbers: "__num|{type}|{value}",
    sets: "__set|{type}|{value}",
    MutableMapping: "__dict|{type}|{value}",
    Iterable: "__iterable|{type}|{value}",
    "obj": "__obj|{type}|{value}",
}


class Root(Dot):

    def __init__(self, host='localhost', port=6379, db=0, *args, **kwargs):
        redis = kwargs.pop('redis', StrictRedis)
        super(Root, self).__init__(*args, **kwargs)
        self.red = redis(host=host, port=port, db=db)
        self.setup()

    @staticmethod
    def doformat(value, the_type=None, force_serialize=False):
        new_value = None
        if the_type:
            new_value = json.dumps(value)
        elif isinstance(value, strings):
            pass
        elif isinstance(value, sets):
            if force_serialize:
                new_value = json.dumps(value)
                the_type = sets
            else:
                value = [Root.doformat(i, force_serialize=True) for i in value]
                return value
        elif isinstance(value, numbers):
            the_type = numbers
        elif isinstance(value, MutableMapping):
            if force_serialize:
                new_value = json.dumps(value)
                the_type = MutableMapping
            else:
                value = {i: Root.doformat(i, force_serialize=True) for i in value}
                return value
        elif isinstance(value, Iterable):
            if force_serialize:
                new_value = json.dumps(value)
                the_type = Iterable
            else:
                value = [Root.doformat(i, force_serialize=True) for i in value]
                return value
        new_value = new_value if new_value else value
        value = TYPE_FORMATS[the_type].format(type=value.__class__.__name__, value=new_value)
        return value.encode('utf-8')

    def load(self, paths):
        values = self.red.mget(paths)
        return dict(zip(paths, values))

    def save(self, path, value):
        if isinstance(value, strings):
            self.red.set(path, value)
        elif isinstance(value, sets):
            value = self.doformat(value)
            self.red.sadd(path, *value)
        elif isinstance(value, numbers):
            value = self.doformat(value)
            self.red.set(path, value)
        elif isinstance(value, MutableMapping):
            value = self.doformat(value)
            self.red.hmset(path, value)
        elif isinstance(value, Iterable):
            value = self.doformat(value)
            self.red.rpush(path, *value)
        else:
            value = self.doformat(value, the_type="obj")
            self.red.set(path, value)
