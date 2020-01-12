# redis has a client server architechture
# uses request-response cycle
# remote dictionary service
import redis
import datetime
import random
import logging

r = redis.Redis()
r.mset({"bd": 'dhaka', 'usa': 'washington dc'})
# output will show bytestring
print(r.get('bd'))
# so we may call like the following depending on what you want to actually do with the returned bytestring.
print(r.get('bd').decode('utf-8'))
# Allowed Key Types
today = datetime.date.today()
# You’ll need to explicitly convert the Python date object to str, which you can do with .isoformat():
visitors = {'john',
            'dan',
            'alex'
            }

stoday = today.isoformat()
print(r.smembers(stoday))
print(r.sadd(stoday, *visitors))
print(r.scard(today.isoformat()))

# Example: PyHats.com
'''
PyHats.com, that sells outrageously overpriced hats to anyone who will buy them, and hired you to build the site.

You’ll use Redis to handle some of the product catalog, 
inventorying, and bot traffic detection for PyHats.com.

It’s day one for the site, 
and we’re going to be selling three limited-edition hats. 
Each hat gets held in a Redis hash of field-value pairs, 
and the hash has a key that is a prefixed random integer , 
such as hat:56854717. Using the hat: prefix is Redis 
convention for creating a sort of namespace within a Redis database:
'''

random.seed(444)
hats = {f"hat:{random.getrandbits(32)}": i for i in (
    {
        "color": "black",
        "price": 49.9,
        "style": "fitted",
        "quantity": 1000,
        "npurchased": 0,
    },

    {"color": "maroon",
     "price": 59.9,
     "style": "hipster",
     "quantity": 100,
     "npurchased": 0,
     },

    {"color": "green",
     "price": 149.9,
     "style": "baseball",
     "quantity": 500,
     "npurchased": 0,
     }

)}
r = redis.Redis(db=1)
with r.pipeline() as pipe:
    for h_id, hat in hats.items():
        print(pipe.hmset(h_id, hat))
    print(pipe.execute())

print(r.bgsave())
print(r.keys())
print(r.hgetall('hat:1326692461'))

# Let’s introduce a big chunk of code and walk through it afterwards step by step.
# You can picture buyitem() as being called any time a user clicks on a Buy Now or Purchase button.
# Its purpose is to confirm the item is in stock and take an action based on that result,
# all in a safe manner that looks out for race conditions and retries if one is detected:
logging.basicConfig()


class OutofStockError(Exception):
    '''
    raised when pyhat.com is out of stock of today's hottest hat
    '''


def buy_item(r: redis.Redis, itemid: int) -> None:
    with r.pipeline as pipe:
        error_count = 0
        while True:
            try:
                # Get available inventory, watching for changes

                # related to this itemid before the transaction
                pipe.watch(itemid)
                nleft: bytes = r.hget(itemid, "quantity")
                if nleft > b"0":
                    pipe.multi()
                    pipe.hincrby(itemid, "quantity", -1)
                    pipe.hincrby(itemid, "npurchased", 1)
                    pipe.execute()
                    break
                else:
                    # Stop watching the itemid and raise to break out
                    pipe.unwatch()
                    raise OutofStockError(f"Sorry, {itemid} is out of stock")

            except redis.WatchError:
                # Log total num. of errors by this user to buy this item,

                # then try the same process again of WATCH/HGET/MULTI/EXEC
                error_count += 1
                logging.warning("WatchError #%d: %s; retrying",

                                error_count, itemid)

    return None
