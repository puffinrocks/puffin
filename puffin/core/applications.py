from . model import Application, ApplicationSettings
from ..util.homer import HOME
from .db import db, update_model_with_json
from .. import app

from cachetools import cached, TTLCache

from os import listdir
from os.path import join, exists, isdir, isfile
import yaml
import re

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
        if application:
            applications[application_id] = application
    return applications
        
def load_application(application_id):
    path = join(APPLICATION_HOME, application_id)

    compose_path = join(path, "docker-compose.yml")
    if not isfile(compose_path):
        return None

    with open(compose_path) as compose_file:    
        compose = yaml.load(compose_file)
        labels = compose.get("labels", {})

        name = labels.get("rocks.puffin.name", application_id)
        subtitle = labels.get("rocks.puffin.subtitle", "")
        website = labels.get("rocks.puffin.website", "")
        description = labels.get("rocks.puffin.description", "")
        
        logo = join(application_id, labels.get("rocks.puffin.logo", "logo.png"))
        screenshots = load_screenshots(application_id, labels.get("rocks.puffin.screenshots", "screenshots/"))

        application = Application(application_id, path, name, logo, subtitle, 
            website, description, "docker-compose.yml", screenshots)
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
    return re.sub(r'[^a-z0-9]', '', user.login + "x" + application.application_id).lower()

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
