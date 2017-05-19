import re
import os
import os.path
import cachetools
import enum

import yaml
import bleach
import flaskext.markdown
import flask_bleach

from puffin import app
from .db import db, update_model_with_json
from .. import util
from . import security


APPLICATION_HOME = os.path.join(util.HOME, "apps")

# Name separator between user and application, also check apps/_proxy
APPLICATION_SEPARATOR = "xxxx"

application_cache = cachetools.TTLCache(maxsize=1, ttl=120)


class Application:

    def __init__(self, application_id):
        self.application_id = application_id
        self.path = os.path.join(APPLICATION_HOME, self.application_id)

        readme = ""
        if os.path.isfile(os.path.join(self.path, "README.md")):
            with open(os.path.join(self.path, "README.md")) as readme_file:
                readme = readme_file.read()

        readme_lines = readme.split('\n', 2)
        self.name = re.sub(r'\s*#\s*', '', readme_lines[0]) if len(readme) > 0 else application_id
        self.subtitle = readme_lines[1].strip().strip("_") if len(readme_lines) > 1 else ""
        self.description = "\n".join(readme_lines[1:]) if len(readme_lines) > 1 else ""
        self.description = re.sub(r'([a-z0-9]+(/[a-z0-9-_]+)*\.(png|jpg))', '/media/' + application_id + r'/\1', self.description)

        self.compose = os.path.join(self.path, "docker-compose.yml")
        self.logo = os.path.join(self.application_id, "logo.png")

        compose_data = {}
        with open(self.compose) as compose_file:
            compose_data = yaml.safe_load(compose_file)

        self.main_image = util.safe_get(compose_data, "services", "main", "image")
        if not self.main_image:
            raise Exception("Missing main image in docker-compose.yml for application: " + application_id)

        # Retrieve all volumes except external ones
        self.volumes = [v[0] for v in compose_data.get("volumes", {}).items()
                if not (v[1] and "external" in v[1])]

    def __eq__(self, other):
        return self.application_id == other.application_id

    def __hash__(self):
        return hash(self.application_id)


class ApplicationStatus(enum.Enum):
    DELETED = 0
    CREATED = 10
    UPDATING = 20
    ERROR = 90


class ApplicationSettings:

    def __init__(self, user_id, application_id, settings):
        self.user_id = user_id
        self.application_id = application_id
        self.settings = settings

        self.user = security.get_user(self.user_id)
        self.application = get_application(self.application_id)

    def default(self, key):
        if key == "domain":
            return "{}.{}.{}".format(self.application.application_id,
                    self.user.login, app.config["SERVER_NAME_FULL"])
        elif key in ("https", "started"):
            return False
        else:
            return None

    def reset(self, key):
        self.settings.pop(key, None)

    def __setitem__(self, key, value):
        if value != self.default(key):
            self.settings[key] = value
        else:
            self.reset(key)

    def __getitem__(self, key):
        return self.settings.get(key, self.default(key))


def init():
    flaskext.markdown.Markdown(app)
    app.config['BLEACH_ALLOWED_TAGS'] = bleach.ALLOWED_TAGS + ["p", "h1", "h2", "h3", "h4", "h5", "h6", "img"]
    app.config['BLEACH_ALLOWED_ATTRIBUTES'] = dict(bleach.ALLOWED_ATTRIBUTES, img=["src"])
    flask_bleach.Bleach(app)

def get_application(application_id):
    applications = get_applications()
    return applications.get(application_id)

def get_application_list():
    applications = get_applications().values()

    # Filter private applications
    applications = (a for a in applications if not a.application_id.startswith("_"))

    # Sort alphabetically
    applications = sorted(applications, key=lambda a: a.name.lower())

    return applications

@cachetools.cached(application_cache)
def get_applications():
    applications = {}
    for application_id in os.listdir(APPLICATION_HOME):
        application = load_application(application_id)
        if application:
            applications[application_id] = application
    return applications

def load_application(application_id):
    if application_id.startswith("."):
        return None

    path = os.path.join(APPLICATION_HOME, application_id)
    if not os.path.isdir(path):
        return None

    application = Application(application_id)
    return application

def get_default_application_domain(user, application):
    return application.application_id + "." + user.login + "." + app.config["SERVER_NAME_FULL"]

def get_application_domain(user, application):
    default_domain = get_default_application_domain(user, application)
    application_settings = \
        get_application_settings(user.user_id, application.application_id)
    domain = application_settings.settings.get("domain", default_domain)
    return domain

def get_application_https(user, application):
    return get_application_settings(user.user_id, application.application_id)\
            .settings.get("https", False)

def get_application_started(user, application):
    application_settings = \
        get_application_settings(user.user_id, application.application_id)
    started = application_settings.settings.get("started", False)
    return started

def set_application_started(user, application, started):
    application_settings = \
        get_application_settings(user.user_id, application.application_id)
    if started:
        application_settings.settings["started"] = True
    else:
        application_settings.settings.pop("started", None)
    update_application_settings(application_settings)

def get_all_started_applications():
    applications = get_applications()
    users = {u.user_id : u for u in security.get_all_users()}

    all_application_settings = db.session.query(ApplicationSettings).all()
    started_application_settings = \
        [s for s in all_application_settings if s.settings.get("started")]

    started_applications = []
    for application_settings in started_application_settings:

        application = applications.get(application_settings.application_id)
        user = users.get(application_settings.user_id)

        if not application or not user:
            continue

        started_applications.append((user, application))

    return set(started_applications)

def get_application_name(user, application):
    name = user.login + APPLICATION_SEPARATOR
    if application:
        name += application.application_id
    # docker-compose sanitizes project name, see https://github.com/docker/compose/issues/2119
    return re.sub(r'[^a-z0-9]', '', name.lower())

def get_user_application_id(container_name):
    return container_name.split(APPLICATION_SEPARATOR, 1)

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
