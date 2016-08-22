#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dot import Dot


class Root(Dot):

    def __init__(self, *args, **kwargs):
        super(Root, self).__init__(*args, **kwargs)
        self.counter = 0
        self.items = {}
        self.setup()

    def load(self, paths):
        # imagine counter as being a hit counter to the external resource
        # to get the object.
        self.counter += 1
        return {i: self.items[i] if i in self.items else "value %s" % i for i in paths}

    def save(self, path, value):
        self.items[path] = value

