from .security import get_all_users
from . import docker

from cachetools import cached, TTLCache


stats_cache = TTLCache(maxsize=1, ttl=60)


class Stats:
    pass


def init():
    pass

@cached(stats_cache)
def get_stats():
    stats = Stats()
    stats.users = get_users()
    stats.containers = get_containers()
    return stats    

def get_users():
    return len(get_all_users())

def get_containers():
    return len(docker.get_containers(docker.get_client()))

