import logging
import bson.json_util
from time import time
from redis import Redis
from redis.sentinel import Sentinel
from copy import deepcopy
from expiringdict import ExpiringDict

log = logging.getLogger('entropy.caching')

# easy-cache==1.1.0
# from easy_cache import caches, ecached
# from easy_cache.contrib.redis_cache import RedisCacheInstance

# r = Redis(host=CACHE_REDIS_HOST, db=CACHE_REDIS_CHANNEL, password=REDIS_PASSWORD)
# redis_cache = RedisCacheInstance(r, serializer=bson.json_util)
# caches.set_default(redis_cache)
class DummyRedis:
    def __get__(self, *args, **kwargs):
        log.error('Use oredis.setup() first!')
        raise NotImplementedError

class ObjectRedis:
    redis = DummyRedis()
    def setup(self, redis_host, redis_db, redis_password=None, master_name=None):
        self.redis_host = redis_host
        self.redis_db = redis_db
        self.redis_password = redis_password
        password = {'password': redis_password} if redis_password else {}
        if isinstance(self.redis_host, list):
            sentinel = Sentinel(self.redis_host, socket_timeout=0.1)
            self.redis = sentinel.master_for(master_name, **dict({'db': redis_db}, **password))
        else:
            self.redis = Redis(**dict(**{'host': redis_host, 'db': redis_db}, **password))

oredis = ObjectRedis()
object_caches = {}
object_ages = {}
object_invalidates = {}
def ocached(mapping, group='default', size=256, age=30, pointer=True):
    if group not in object_caches:
        object_caches[group] = ExpiringDict(max_len=size, max_age_seconds=age)
        object_ages[group] = age
        object_invalidates[group] = {}
    object_cache = object_caches[group]
    object_invalidate = object_invalidates[group]
    def decorator(fun):
        def wrapper(*args, **kwargs):
            key = mapping.format(*args)
            invalidate = oredis.redis.get(f'{group}:{key}:invalidate')
            if invalidate:
                invalidate = float(invalidate)
                if object_invalidate.get(key, 0) < invalidate:
                    # print("key", key, "invalidated!")
                    object_invalidate[key] = invalidate
                    object_cache.pop(key, None)
            if not kwargs.get('cached', True):
                object_cache.pop(key, None)
            if key not in object_cache:
                object_cache[key] = fun(*args, **kwargs)
            # else:
            #     print("OC CACHE HIT", key)
            return object_cache[key] if pointer else deepcopy(object_cache[key])
        return wrapper
    return decorator

def ocache_invalidate(key, group='default'):
    oredis.redis.setex(f'{group}:{key}:invalidate', object_ages.get(group, 60), time())