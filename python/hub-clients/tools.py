from random import choice
from twisted.internet import reactor
import memcache

__HEX_STRING = "0123456789ABCDE"
__HUB_PREFIX = "71"

empty = object()


def random_lamp_sn():
    # 随机生成灯具id
    return "".join(str(int(choice(__HEX_STRING), 16)).zfill(2) for _ in range(6))


def random_hub_id():
    # 随机生成集控id
    suffix = "".join(str(int(choice(__HEX_STRING), 16)).zfill(2) for _ in range(5))
    return __HUB_PREFIX + suffix


def run(host, port, factory):
    # 加载周期任务
    factory.start_interval_tasks()
    # 建立连接
    reactor.connectTCP(host, port, factory)
    # 事件循环
    reactor.run()


class cached_property:
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.

    A cached property can be made out of an existing method:
    (e.g. ``url = cached_property(get_absolute_url)``).
    The optional ``name`` argument is obsolete as of Python 3.6 and will be
    deprecated in Django 4.0 (#30127).
    """
    name = None

    @staticmethod
    def func(instance):
        raise TypeError(
            'Cannot use cached_property instance without calling '
            '__set_name__() on it.'
        )

    def __init__(self, func, name=None):
        self.real_func = func
        self.__doc__ = getattr(func, '__doc__')

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name
            self.func = self.real_func
        elif name != self.name:
            raise TypeError(
                "Cannot assign the same cached_property to two different names "
                "(%r and %r)." % (self.name, name)
            )

    def __get__(self, instance, cls=None):
        """
        Call the function and put the return value in instance.__dict__ so that
        subsequent attribute access on the instance returns the cached value
        instead of calling cached_property.__get__().
        """
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res


class MemcachedAPI(object):
    _instance = None
    _conn = memcache.Client(["172.16.8.205:11211"], debug=False)

    def __getattr__(self, item):
        return self._conn.get(item)

    def __setattr__(self, key, value):
        self._conn.set(key, value)

    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        cls._instance = super(MemcachedAPI, cls).__new__(cls, *args, **kwargs)
        return cls._instance


api = MemcachedAPI()


def get_lamp_ids(size):
    lamps = api.lamps or {}
    ids = {}
    current_seq = len(lamps.keys())
    for i in range(size):
        while True:
            sn = random_lamp_sn()
            current_seq += (i+1)
            """
            {
                sn: seq
            }
            """
            if sn not in lamps.keys():
                lamps.update({sn: current_seq})
                ids.update({sn: current_seq})
                break
    api.lamps = lamps
    return ids
