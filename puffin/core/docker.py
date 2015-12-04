from .machine import get_machine
from .apps import get_app
from .queue import task, task_exists
from .model import User, App, AppStatus, PUFFIN_USER
from .db import db
from .. import app

from docker import Client

from compose import config
from compose.project import Project

from time import sleep


# Sleep after creating an app to allow it to startup
APP_CREATE_SLEEP = 5


def init():
    pass

def get_client():
    machine = get_machine()
    client = Client(base_url=machine.base_url, tls=machine.tls_config, version="auto")
    client.ping()
    return client

def create_app(client, user, app):
    if get_app_status(client, user, app) != AppStatus.DELETED:
        raise RuntimeError("App already installed or updating, user: {}, app: {}".format(user.login, app.app_id))
    name = get_container_name(user, app.app_id)
    task(name, create_app_task, client, user.user_id, app)

def create_app_task(client, user_id, app):
    user = db.session.query(User).get(user_id)
    create_app_do(client, user, app)
    sleep(APP_CREATE_SLEEP)

def create_app_do(client, user, app):
    project = get_project(client, user, app)
    project.up()
        
def delete_app(client, user, app, async=True):
    if get_app_status(client, user, app) != AppStatus.CREATED:
        raise RuntimeError("App not installed or updating, user: {}, app: {}".format(user.login, app.app_id))
    name = get_container_name(user, app.app_id)
    task(name, delete_app_task, client, user.user_id, app)

def delete_app_task(client, user_id, app):
    user = db.session.query(User).get(user_id)
    delete_app_do(client, user, app)

def delete_app_do(client, user, app):
    project = get_project(client, user, app)
    project.stop()
    project.remove_stopped()

def get_app_status(client, user, app):
    name = get_container_name(user, app.app_id)
    if task_exists(name):
        return AppStatus.UPDATING
    container = get_container(client, name)
    if container:
        return AppStatus.CREATED
    else:
        return AppStatus.DELETED

def get_app_domain(user, application):
    domain = app.config["SERVER_NAME"] or "localhost"
    return application.app_id + "." + user.login + "." + domain

def get_project(client, user, app):
    name = get_container_name(user, app.app_id)
    config_details = config.find(app.path, [app.compose])
    project_config = config.load(config_details)

    project = Project.from_dicts(name, project_config, client, False, None)

    service = project.get_service("main")
    
    ports = service.options.get("ports", [])
    
    service.options["container_name"] = name

    environment = service.options.get("environment", {})
    service.options["environment"] = environment
    environment["VIRTUAL_HOST"] = get_app_domain(user, app)
    if ports:
        environment["VIRTUAL_PORT"] = ports[0]

    return project

def get_container_name(user, app_id):
    return user.login + "_" + app_id

def get_containers(client):
    return client.containers()
 
def get_container(client, name):
    containers = get_containers(client)
    container = [c for c in containers if "/" + name in c["Names"]]
    if len(container) > 0:
        return container
    else:
        return None

def install_proxy():
    client = get_client()
    user = PUFFIN_USER
    app = get_app("_proxy")
    if is_app_running(client, user, app):
        return False
    create_app_do(client, user, app)
    return True

