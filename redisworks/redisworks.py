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

NUM_IDEN = "__num|{type}|{number}"
DIC_IDEN = "__dict|{blob}"


class Root(Dot):

    def __init__(self, host='localhost', port=6379, db=0, *args, **kwargs):
        redis = kwargs.pop('redis', StrictRedis)
        super(Root, self).__init__(*args, **kwargs)
        self.red = redis(host=host, port=port, db=db)
        self.setup()

    @staticmethod
    def format_num(value):
        value = NUM_IDEN.format(type=value.__class__.__name__, number=value)
        return value.encode('utf-8')

    def load(self, paths):
        values = self.red.mget(paths)
        return dict(zip(paths, values))

    def save(self, path, value):
        if isinstance(value, strings):
            self.red.set(path, value)
        elif isinstance(value, sets):
            self.red.sadd(path, value)
        elif isinstance(value, numbers):
            value = self.format_num(value)
            self.red.set(path, value)
        elif isinstance(value, MutableMapping):
            value = json.dumps(value)
            value = DIC_IDEN.format(value)
            self.red.set(path, value)
        elif isinstance(value, Iterable):
            self.red.rpush(path, *value)
        else:
            value = json.dumps(value)
            value = DIC_IDEN.format(value)
            self.red.set(path, value)
