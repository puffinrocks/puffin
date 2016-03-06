from . model import Application, ApplicationSettings
from ..util.homer import HOME
from .db import db, update_model_with_json
from .. import app

from cachetools import cached, TTLCache

from os import listdir
from os.path import join, exists, isdir, isfile
import yaml

APPLICATION_HOME = join(HOME, "apps")
application_cache = TTLCache(maxsize=1, ttl=120)

def init():
    pass

def get_application(application_id):
    applications = get_applications()
    return applications[application_id]

def get_application_list():
    applications = get_applications().values()
    
    # Filter private applications
    applications = (a for a in applications if not a.application_id.startswith("_"))
    
    # Sort alphabetically
    applications = sorted(applications, key=lambda a: a.name.lower())
    
    return applications

@cached(application_cache)
def get_applications():
    applications = {}
    for application_id in listdir(APPLICATION_HOME):
        application = load_application(application_id)
        applications[application_id] = application
    return applications
        
def load_application(application_id):
    path = join(APPLICATION_HOME, application_id)
    with open(join(path, "manifest.yml")) as manifest_file:    
        manifest = yaml.load(manifest_file)

        name = manifest.get("name", application_id)
        logo = join(application_id, manifest.get("logo", "logo.png"))
        subtitle = manifest.get("subtitle", "")
        website = manifest.get("website", "")
        description = manifest.get("description", "")
        compose = manifest.get("compose", "docker-compose.yml")
        screenshots = load_screenshots(application_id, 
            manifest.get("screenshots", "screenshots/"))

        application = Application(application_id, path, name, logo, subtitle, 
            website, description, compose, screenshots)
        return application

def load_screenshots(application_id, screenshot_dir):
    path = join(APPLICATION_HOME, application_id, screenshot_dir)
    if not isdir(path):
        return []
    screenshots = [join(application_id, screenshot_dir, f) for f in listdir(path) if isfile(join(path, f))]
    return screenshots

def get_default_application_domain(user, application):
    return application.application_id + "." + user.login + "." + app.config["SERVER_NAME_FULL"]

def get_application_domain(user, application):
    default_domain = get_default_application_domain(user, application)
    application_settings = \
        get_application_settings(user.user_id, application.application_id)
    domain = application_settings.settings.get("domain", default_domain)
    return domain

def get_application_name(user, application):
    # docker-compose sanitizes project name, see https://github.com/docker/compose/issues/2119
    return user.login + "x" + application.application_id

def get_application_settings(user_id, application_id):
    application_settings = db.session.query(ApplicationSettings).filter_by(
        user_id=user_id, application_id=application_id).first()
    if application_settings == None:
        application_settings = ApplicationSettings(user_id, application_id, {})
    return application_settings

def update_application_settings(application_settings):
    if application_settings.settings:
        update_model_with_json(application_settings)
        db.session.commit()
    elif application_settings.application_settings_id:
        db.session.delete(application_settings)
        db.session.commit()
