Redisworks 0.4.0
================

|Python Versions| |License| |Build Status| |Coverage Status|

**The Pythonic Redis Client**

Why Redisworks?

-  Lazy Redis Queries
-  Dynamic Typing
-  Ease of use

Have you ever used PyRedis and wondered why you have to think about
types all the time? That you have to constantly convert objects to
strings and back and forth since Redis keeps most things as strings?

Redis works provides a Pythonic interface to Redis. Let Redisworks take
care of type conversions for you.

Behind the scene, Redisworks uses
`DotObject <https://github.com/seperman/dotobject>`__ to provide
beautiful dot notation objects and lazy Redis queries.

Install
=======

``pip install redisworks``

Note that RedisWorks needs Redis server 2.4+.

Setup
=====

let’s say if you want all the keys in Redis to start with the word
``root``. Then you:

.. code:: py

   root = Root()  # connects to Redis on local host by default

Or if you want to be more specific:

.. code:: py

   root = Root(host='localhost', port=6379, db=0)

password
--------

Any other parameter that you pass to Root will be passed down to
PyRedis. For example:

.. code:: py

   root = Root(host='localhost', port=6379, db=0, password='mypass')

Saving to Redis
===============

Saving to Redis is as simple as assigning objects to attributes of root
or attributes of attributes of root (you can go as deep as you want.)
Make sure you are not using any Python’s reserved words in the key’s
name.

Example:

.. code:: py

   >>> from redisworks import Root
   >>> import datetime
   >>> root = Root()
   >>> root.my.list = [1, 3, 4]
   >>> root.my.other.list = [1, [2, 2]]
   >>> 
   >>> some_date = datetime.datetime(2016, 8, 22, 10, 3, 19)
   >>> root.time = some_date
   >>> 
   >>> root.the.mapping.example = {1:1, "a": {"b": 10}}

Redis works will automatically convert your object to the proper Redis
type and immediately write it to Redis as soon as you assign an element!

The respective keys for the above items will be just like what you type:
``root.my.list``, ``root.time``, ``root.the.mapping.example``:

If you use redis-cli, you will notice that the data is saved in the
proper Redis data type:

::

   127.0.0.1:6379> scan 0
   1) "0"
   2) 1) "root.the.mapping.example"
      2) "root.time"
      3) "root.my.list"
   127.0.0.1:6379> type root.the.mapping.example
   hash
   127.0.0.1:6379> type root.time
   string
   127.0.0.1:6379> type root.my.list
   list

Reading from Redis
==================

Reading the data is as simple as if it was just saved in Python memory!

Redis works returns Lazy queries just like how Django returns lazy
queries. In fact the lazy objects code is borrowed from Django!

If you ran the example from `Saving to Redis <#saving-to-redis>`__, run
a flush ``root.flush()`` to empty Redisworks Cache. This is so it goes
and gets the objects from Redis instead of reading its own current copy
of data:

.. code:: py

   >>> from redisworks import Root
   >>> root = Root()
   >>> thetime = root.time
   >>> thelist = root.my.list
   >>> mydict = root.the.mapping.example
   >>> mydict  # is not evalurated yet!
   <Lazy object: root.the.mapping.example>
   >>> print(mydict)
   {1:1, "a": {"b": 10}}  # Now all the 3 objects are read from Redis!
   >>> mydict
   {1:1, "a": {"b": 10}}
   >>> root.my.list
   [1, 3, 4]
   >>> root.my.other.list
   [1, [2, 2]]
   >>> root.time
   2016-08-22 10:03:19

Changing root key name
======================

Every key name by default starts with the word ``root``. If you want to
use another name, you have two options:

Option 1, pass a namespace:

.. code:: py

   >>> mynamespace = Root(conn=redis_conn, namespace='mynamespace')
   >>> mynamespace.foo = 'bar'

Option 2, simply subclass ``Root``:

.. code:: py

   >>> from redisworks import Root
   >>> class Post(Root):
   ...     pass
   >>> post=Post()
   >>> post.item1 = "something"  # saves to Redis
   ...
   >>> print(post.item1)  # loads from Redis
   something

Numbers as attribute names
==========================

Let’s say you want ``root.1`` as a key name. Python does not allow
attribute names start with numbers.

All you need to do is start the number with the character ``i`` so
Redisworks takes care of it for you:

.. code:: py

   >>> root.i1 = 10
   >>> print(root.i1)
   10

The actual key in Redis will be ``root.1``

Dynamic key names
=================

.. code:: py

   >>> path1 = 'blah'
   >>> path2 = 'blah.here`'

   >>> root[path1] = 'foo'
   >>> root[path2] = 'foo bar'

   >>> root.blah
   foo
   >>> root.blah.here
   foo bar

Passing TTL to the keys
=======================

You can use the ``with_ttl`` helper.

.. code:: py

   >>> from redisworks import Root, with_ttl
   >>> self.root.myset = with_ttl([1, 2, 3], ttl=1)
   >>> self.root.flush()
   >>> self.root.myset
   [1, 2, 3]
   >>> time.sleep(1.2)
   >>> self.root.flush()
   >>> self.root.myset

Other examples
==============

Take a look at `example.py <example.py>`__

Primary Author
==============

Seperman (Sep Dehpour)

-  `Github <https://github.com/seperman>`__
-  `Linkedin <http://www.linkedin.com/in/sepehr>`__
-  `ZepWorks <https://zepworks.com>`__

.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/redisworks.svg?style=flat
.. |License| image:: https://img.shields.io/pypi/l/redisworks.svg?version=latest
.. |Build Status| image:: https://travis-ci.org/seperman/redisworks.svg?branch=master
   :target: https://travis-ci.org/seperman/redisworks
.. |Coverage Status| image:: https://coveralls.io/repos/github/seperman/redisworks/badge.svg?branch=master
   :target: https://coveralls.io/github/seperman/redisworks?branch=master
