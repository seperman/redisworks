#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import builtins
import datetime
from dot import Dot
from redis import StrictRedis
from redis.exceptions import ResponseError
from decimal import Decimal
from collections import Iterable
from collections import MutableMapping
from builtins import int
strings = (str, bytes)  # which are both basestring
numbers = (int, float, complex, datetime.datetime, datetime.date, Decimal)
items = 'items'

logger = logging.getLogger(__name__)
sets = (set, frozenset)


TYPE_IDENTIFIER = '!__'
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


class Root(Dot):

    def __init__(self, host='localhost', port=6379, db=0,
                 return_object=True, conn=None, password=None, *args, **kwargs):
        redis = kwargs.pop('redis', StrictRedis)
        super(Root, self).__init__()
        self.red = conn or redis(host=host, port=port, db=db, *args, **kwargs)
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

        if actual_type is not bytes:
            value = value.decode('utf-8')

        if actual_type in {Decimal, complex}:
            value = actual_type(value)
        elif actual_type is datetime.datetime:
            value = datetime.datetime.strptime(value, DATETIME_FORMAT)
        elif actual_type is datetime.date:
            value = datetime.datetime.strptime(value, DATE_FORMAT).date()
        elif actual_type in {dict, list} or isinstance(actual_type, (MutableMapping, Iterable)):
            value = json.loads(value)
        elif actual_type is bool:
            if value == "True":
                value = True
            elif value == "False":
                value = False
        else:
            value = actual_type(value)

        return value

    def get_str(self, value):
        if value.startswith(bTYPE_IDENTIFIER):
            # Doing lstrip to clear out the pattern from left side of the string
            # e.g., b'!__str|==|{actual_type}|==|{value}'
            # becomes b'{actual_type}|==|{value}'
            value = value.lstrip(bTYPE_IDENTIFIER)
            global_type, actual_type, value = value.split(bITEM_DIVIDER)
            if self.return_object:
                value = self.get_obj(value, actual_type)
        return value

    def load(self, paths):
        # majority of keys are strings so we first try to get the string ones.
        # Note that fakeredis loads all keys by mget but redis does ONLY if they
        # are strings.
        result = {}
        values = self.red.mget(paths)

        for i, value in enumerate(values):
            key = paths[i]
            if value is None:
                redis_type = self.red.type(key)
                if redis_type in (None, b'none'):
                    logger.error("Unable to get item: %s", key)
                elif redis_type == b"string":
                    value = self.get_str(value)
                elif redis_type == b"list":
                    value = self.red.lrange(key, 0, -1)
                    value = [self.get_str(i) for i in value]
                elif redis_type == b"set":
                    value = self.red.smembers(key)
                    value = {self.get_str(i) for i in value}
                elif redis_type == b"hash":
                    value = self.red.hgetall(key)
                    value = {self.get_str(i): self.get_str(value[i]) for i in value}
                else:
                    value = "NOT SUPPORTED BY REDISWORKS."
            else:
                if isinstance(value, strings):
                    value = self.get_str(value)
                elif isinstance(value, sets):
                    value = {self.get_str(i) for i in value}
                elif isinstance(value, MutableMapping):
                    value = {self.get_str(i): self.get_str(value[i]) for i in value}
                elif isinstance(value, Iterable):
                    value = [self.get_str(i) for i in value]
            result[key] = value

        return result

    def __save_in_redis(self, path, value):
        if isinstance(value, strings):
            value = self.doformat(value)
            self.red.set(path, value)
        elif isinstance(value, sets):
            value = self.doformat(value)
            self.red.delete(path)
            self.red.sadd(path, *value)
        elif isinstance(value, numbers):
            value = self.doformat(value)
            self.red.set(path, value)
        elif isinstance(value, MutableMapping):
            value = self.doformat(value)
            self.red.delete(path)
            self.red.hset(path, mapping=value)
        elif isinstance(value, Iterable):
            value = self.doformat(value)
            self.red.delete(path)
            self.red.rpush(path, *value)
        else:
            value = self.doformat(value, the_type="obj")
            self.red.set(path, value)

    def save(self, path, value):
        try:
            self.__save_in_redis(path, value)
        except ResponseError as e:
            if str(e) == 'WRONGTYPE Operation against a key holding the wrong kind of value':
                self.red.delete(path)
                self.__save_in_redis(path, value)
            else:
                raise

    # def __add__(self, other):
    #     return 
