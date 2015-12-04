from .machine import get_machine
from .apps import get_app
from .queue import task
from .model import User, App, AppStatus, AppInstallation, PUFFIN_USER
from .db import db
from .. import app

from docker import Client

from compose import config
from compose.project import Project

from time import sleep


# Sleep after creating an app to allow it to startup
APP_CREATE_SLEEP = 5


def init():
    install_proxy()

def install_proxy():
    client = get_client()
    user = PUFFIN_USER
    app = get_app("_proxy")
    if not is_app_running(client, user, app):
        create_app_do(client, user, app)

def get_client():
    machine = get_machine()
    client = Client(base_url=machine.base_url, tls=machine.tls_config, version="auto")
    client.ping()
    return client

def create_app(client, user, app):
    app_installation = get_app_installation(user, app)
    if app_installation:
        raise RuntimeError("App already installed or updating, user: {}, app: {}".format(user.login, app.app_id))
    
    app_installation = AppInstallation(user, app.app_id, AppStatus.CREATING)
    db.session.add(app_installation)
    db.session.commit()
        
    task(create_app_task, client, user.user_id, app)

def create_app_task(client, user_id, app):
    user = db.session.query(User).get(user_id)
    app_installation = get_app_installation(user, app)
    try:
        create_app_do(client, user, app)
        app_installation.status = AppStatus.CREATED
        sleep(APP_CREATE_SLEEP)
    except:
        app_installation.status = AppStatus.ERROR
        raise
    finally:
        db.session.add(app_installation)
        db.session.commit()

def create_app_do(client, user, app):
    project = get_project(client, user, app)
    project.up()
        
def delete_app(client, user, app, async=True):
    app_installation = get_app_installation(user, app)
    if not app_installation or app_installation.status != AppStatus.CREATED:
        raise RuntimeError("App not installed or updating, user: {}, app: {}".format(user.login, app.app_id))
    
    app_installation.status = AppStatus.DELETING
    db.session.add(app_installation)
    db.session.commit()
        
    task(delete_app_task, client, user.user_id, app)

def delete_app_task(client, user_id, app):
    user = db.session.query(User).get(user_id)
    app_installation = get_app_installation(user, app)
    try:
        delete_app_do(client, user, app)
        db.session.delete(app_installation)
    except:
        app_installation.status = AppStatus.ERROR
        db.session.add(app_installation)
        raise
    finally:
        db.session.commit()

def delete_app_do(client, user, app):
    project = get_project(client, user, app)
    project.stop()
    project.remove_stopped()

def get_app_installation(user, app):
    return db.session.query(AppInstallation).filter_by(user_id=user.user_id, app_id=app.app_id).first()

def get_app_status(user, app):
    app_installation = get_app_installation(user, app)
    if app_installation:
        return app_installation.status
    else:
        return AppStatus.DELETED

def is_app_running(client, user, app):
    name = get_container_name(user, app.app_id)
    container = get_container(client, name)
    return container != None
           
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
