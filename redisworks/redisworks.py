#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
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
    import builtins
else:  # pragma: no cover
    strings = (str, unicode)
    numbers = (int, float, long, complex, datetime.datetime, datetime.date, Decimal)
    items = 'iteritems'
    import __builtin__ as builtins

TYPE_IDENTIFIER = '__-'
bTYPE_IDENTIFIER = TYPE_IDENTIFIER.encode('utf-8')
ITEM_DIVIDER = '|==|'
bITEM_DIVIDER = ITEM_DIVIDER.encode('utf-8')

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DATE_FORMAT = "%Y-%m-%d"

# In addition to built in types:
OTHER_STANDARD_TYPES = {'Decimal': Decimal, 'datetime': datetime.datetime, 'date': datetime.date}

TYPE_FORMATS = {
    numbers: "num",
    sets: "set",
    MutableMapping: "dict",
    Iterable: "list",
    "obj": "obj",
    strings: "str"
}

for i in TYPE_FORMATS:
    TYPE_FORMATS[i] = TYPE_IDENTIFIER + TYPE_FORMATS[i] + ITEM_DIVIDER +\
                      '{actual_type}' + ITEM_DIVIDER + '{value}'


def str_to_class(name):
    try:
        result = getattr(builtins, name)
    except AttributeError:
        result = OTHER_STANDARD_TYPES[name]
    return result
    # return reduce(getattr, str.split("."), sys.modules[__name__])


class Root(Dot):

    def __init__(self, host='localhost', port=6379, db=0,
                 return_object=True, *args, **kwargs):
        redis = kwargs.pop('redis', StrictRedis)
        super(Root, self).__init__(*args, **kwargs)
        self.red = redis(host=host, port=port, db=db)
        self.return_object = return_object
        self.setup()

    @staticmethod
    def doformat(value, the_type=None, force_serialize=False):
        new_value = None
        if the_type:
            new_value = json.dumps(value)
        elif isinstance(value, strings):
            the_type = strings
        elif isinstance(value, sets):
            if force_serialize:
                new_value = json.dumps(value)
                the_type = sets
            else:
                value = [Root.doformat(i, force_serialize=True) for i in value]
                return value
        elif isinstance(value, numbers):
            the_type = numbers
            if isinstance(value, datetime.datetime):
                new_value = value.strftime(DATETIME_FORMAT)
            elif isinstance(value, datetime.date):
                new_value = value.strftime(DATE_FORMAT)
        elif isinstance(value, MutableMapping):
            if force_serialize:
                new_value = json.dumps(value)
                the_type = MutableMapping
            else:
                value = {Root.doformat(i, force_serialize=True): Root.doformat(value[i], force_serialize=True) for i in value}
                return value
        elif isinstance(value, Iterable):
            if force_serialize:
                new_value = json.dumps(value)
                the_type = Iterable
            else:
                value = [Root.doformat(i, force_serialize=True) for i in value]
                return value
        new_value = new_value if new_value else value
        value = TYPE_FORMATS[the_type].format(actual_type=value.__class__.__name__, value=new_value)
        return value.encode('utf-8')

    @staticmethod
    def get_obj(value, actual_type):
        actual_type = str_to_class(actual_type.decode('utf-8'))

        if py3:
            if actual_type is str:
                value = value.decode('utf-8')
            elif actual_type in {Decimal, complex}:
                value = value.decode('utf-8')
                value = actual_type(value)
            elif actual_type is datetime.datetime:
                value = value.decode('utf-8')
                value = datetime.datetime.strptime(value, DATETIME_FORMAT)
            elif actual_type is datetime.date:
                value = value.decode('utf-8')
                value = datetime.datetime.strptime(value, DATE_FORMAT).date()
            else:
                value = actual_type(value)
        else:
            if actual_type is unicode:
                value = value.decode('utf-8')
            else:
                value = actual_type(value)

        return value

    def load(self, paths):
        # import ipdb; ipdb.set_trace()
        values = self.red.mget(paths)

        result = []
        for value in values:
            if value.startswith(bTYPE_IDENTIFIER):
                value = value.strip(bTYPE_IDENTIFIER)
                global_type, actual_type, value = value.split(bITEM_DIVIDER)
                if self.return_object:
                    value = self.get_obj(value, actual_type)
            result.append(value)

        return dict(zip(paths, result))

    def save(self, path, value):
        if isinstance(value, strings):
            value = self.doformat(value)
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
