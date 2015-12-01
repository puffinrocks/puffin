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

def get_apps():
    apps = load_apps()
    apps = sorted(apps, key=lambda app: app.name.lower())
    return apps

@cached(app_cache)
def load_apps():
    apps = []
    for app_id in listdir(APP_HOME):
        app = load_app(app_id)
        apps.append(app)
    return apps
        
def load_app(app_id):
    with open(join(APP_HOME, app_id, "manifest.yml")) as manifest_file:    
        manifest = yaml.load(manifest_file)

        name = manifest["name"]
        logo = manifest["logo"]
        description = manifest["description"]

        app = App(app_id, name, logo, description)
        return app

