from ..util.homer import HOME
from .db import db, update_model_with_json
from .. import app
from enum import Enum

from flaskext.markdown import Markdown
from flask_bleach import Bleach
from bleach import ALLOWED_TAGS, ALLOWED_ATTRIBUTES
from cachetools import cached, TTLCache
from os import listdir
from os.path import join, exists, isdir, isfile
import yaml
import re


APPLICATION_HOME = join(HOME, "apps")
application_cache = TTLCache(maxsize=1, ttl=120)


class Application:
    
    def __init__(self, application_id, name, subtitle, description):
        self.application_id = application_id
        self.name = name
        self.subtitle = subtitle
        self.description = description
        
        self.path = join(APPLICATION_HOME, self.application_id)
        self.compose = join(self.path, "docker-compose.yml")
        self.logo = join(self.application_id, "logo.png") 


class ApplicationStatus(Enum):
    DELETED = 0
    CREATED = 10
    UPDATING = 20
    ERROR = 90


class ApplicationSettings:
    
    def __init__(self, user_id, application_id, settings):
        self.user_id = user_id
        self.application_id = application_id
        self.settings = settings


def init():
    Markdown(app)
    app.config['BLEACH_ALLOWED_TAGS'] = ALLOWED_TAGS + ["p", "h1", "h2", "h3", "h4", "h5", "h6", "img"]
    app.config['BLEACH_ALLOWED_ATTRIBUTES'] = dict(ALLOWED_ATTRIBUTES, img=["src"])
    Bleach(app)

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
    if application_id.startswith("."):
        return None

    path = join(APPLICATION_HOME, application_id)

    readme = ""
    if isfile(join(path, "README.md")):
        with open(join(path, "README.md")) as readme_file:
            readme = readme_file.read()

    readme_lines = readme.split('\n', 2)
    name = re.sub(r'\s*#\s*', '', readme_lines[0]) if len(readme) > 0 else application_id
    subtitle = readme_lines[1].strip().strip("_") if len(readme_lines) > 1 else ""
    description = "\n".join(readme_lines[1:]) if len(readme_lines) > 1 else ""
    description = re.sub(r'([a-z0-9]+(/[a-z0-9-_]+)*\.(png|jpg))', '/media/' + application_id + r'/\1', description)
   
    application = Application(application_id, name, subtitle, description)
    return application

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
