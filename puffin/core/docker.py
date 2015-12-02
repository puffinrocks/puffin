from .machine import get_machine
from .queue import task
from .. import app

from docker import Client

from compose import config
from compose.project import Project


def init():
    pass

def get_client():
    machine = get_machine()
    client = Client(base_url=machine.base_url, tls=machine.tls_config, version="auto")
    client.ping()
    return client

def create_app(client, user, app, async=True):
    if (async):
        if getattr(user, "_get_current_object", None):
            user = user._get_current_object()
        task(create_app, client, user, app, async=False)
        return
    project = get_project(client, user, app)
    project.up()
        
def delete_app(client, user, app, async=True):
    if (async):
        if getattr(user, "_get_current_object", None):
            user = user._get_current_object()
        task(delete_app, client, user, app, async=False)
        return
    project = get_project(client, user, app)
    project.stop()
    project.remove_stopped()

def is_app_running(client, user, app):
    containers = get_containers(client)
    container_name = get_container_name(user, app.app_id)
    container = [c for c in containers if "/" + container_name in c["Names"]]
    return len(container) > 0 
           
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
 
