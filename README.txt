**Redisworks 0.2.7**

**The Pythonic Redis Client**

Why Redisworks?

- Lazy Redis Queries
- Dynamic Typing
- Ease of use

Have you ever used PyRedis and wondered why you have to think about types all the time? That you have to constantly convert objects to strings and back and forth since Redis keeps most things as strings?

That's why I wrote Redisworks. Redis works provides a Pythonic interface to Redis. Let Redisworks take care of type conversions for you.

Behind the scene, Redisworks uses [DotObject](https://github.com/seperman/dotobject) to provide beautiful dot notation objects and lazy Redis queries.

**Setup**

let's say if you want all the keys in Redis to start with the word `root`.
Then you:

setup
    >>> root = Root()  # connects to Redis on local host by default


Or if you want to be more specific:

setup
    >>> root = Root(host='localhost', port=6379, db=0)

**Saving to Redis**

Saving to Redis is as simple as assigning objects to attributes of root or attributes of attributes of root (you can go as deep as you want.)
Make sure you are not using any Python's reserved words in the key's name.

    Save to Redis
    >>> from redisworks import Root
    >>> import datetime
    >>> root = Root()
    >>> root.my.list = [1, 3, 4]
    >>> 
    >>> some_date = datetime.datetime(2016, 8, 22, 10, 3, 19)
    >>> root.time = some_date
    >>> 
    >>> root.the.mapping.example = {1:1, "a": "b"}

Redis works will automatically convert your object to the proper Redis type and immediately write it to Redis as soon as you assign an element!

The respective keys for the above items will be just like what you type: `root.my.list`, `root.time`, `root.the.mapping.example`:

In the redis-cli client:

Redis-cli
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

**Reading from Redis**

Redis works returns Lazy queries just like how Django returns lazy queries. In fact the lazy objects code is borrowed from Django!

If you ran the example from [Saving to Redis](#saving-to-redis), run a flush `root.flush()` to empty Redisworks Cache. This is so it goes and gets the objects from Redis instead of reading its own current copy of data:

Read from Redis
    >>> from redisworks import Root
    >>> import datetime
    >>> root = Root()
    >>> thetime = root.time
    >>> thelist = root.my.list
    >>> mydict = root.the.mapping.example
    >>> mydict  # is not evalurated yet!
    <Lazy object: root.the.mapping.example>
    >>> print(mydict)
    {1: 1, 'a': 'b'}  # Now all the 3 objects are read from Redis!
    >>> mydict
    {1: 1, 'a': 'b'}
    >>> root.my.list
    [1, 3, 4]
    >>> root.time
    2016-08-22 10:03:19

**Other examples**

Take a look at [example.py](example.py)

**Primary Author**
Sep Dehpour

Github:  https://github.com/seperman
Linkedin:  http://www.linkedin.com/in/sepehr
ZepWorks:   http://www.zepworks.com
