from . model import App
from ..util.homer import HOME

from cachetools import cached, TTLCache

from os import listdir
from os.path import join
import yaml

APP_HOME = join(HOME, "apps")
app_cache = TTLCache(maxsize=1, ttl=120)

def init():
    pass

def get_app(app_id):
    apps = get_apps()
    return apps[app_id]

def get_app_list():
    apps = get_apps().values()
    
    # Filter private apps
    apps = (a for a in apps if not a.app_id.startswith("_"))
    
    # Sort alphabetically
    apps = sorted(apps, key=lambda app: app.name.lower())
    
    return apps

@cached(app_cache)
def get_apps():
    apps = {}
    for app_id in listdir(APP_HOME):
        app = load_app(app_id)
        apps[app_id] = app
    return apps
        
def load_app(app_id):
    path = join(APP_HOME, app_id)
    with open(join(path, "manifest.yml")) as manifest_file:    
        manifest = yaml.load(manifest_file)

        name = manifest["name"]
        logo = manifest.get("logo", "")
        description = manifest.get("description", "")
        compose = manifest.get("compose")

        app = App(app_id, path, name, logo, description, compose)
        return app

