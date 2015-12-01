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
    with open(join(APP_HOME, app_id, "manifest.yml")) as manifest_file:    
        manifest = yaml.load(manifest_file)

        name = manifest["name"]
        logo = manifest["logo"]
        description = manifest["description"]
        image = manifest.get("image")

        app = App(app_id, name, logo, description, image)
        return app

