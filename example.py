from redisworks import Root
import datetime

root = Root()

# ----- Saving to Redis -----

root.my.list = [1, 3, 4]
some_date = datetime.datetime(2016, 8, 22, 10, 3, 19)
root.time = some_date
root.the.mapping.example = {1: 1, "a": "b"}

# ----- Flushing local cache -----
root.flush()

# ----- Loading from Redis -----
thetime = root.time
thelist = root.my.list
mydict = root.the.mapping.example

print(thetime)
print(mydict)
print(thelist)
