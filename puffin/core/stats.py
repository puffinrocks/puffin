import cachetools

from . import security
from . import docker


stats_cache = cachetools.TTLCache(maxsize=1, ttl=300)


class Stats:
    pass


def init():
    pass

@cachetools.cached(stats_cache)
def get_stats():
    stats = Stats()
    stats.users = get_users()
    stats.apps = get_apps()
    stats.containers = get_containers()
    return stats    

def get_users():
    return len([u for u in security.get_all_users() if u.confirmed])

def get_apps():
    return len(docker.get_all_running_applications())

def get_containers():
    return len(docker.get_containers(docker.get_client()))

