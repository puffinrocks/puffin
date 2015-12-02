from .machine import get_machine
from .queue import task
from .. import app

from docker import Client

from compose import config
from compose.project import Project

updating_apps = set()


def init():
    pass

def get_client():
    machine = get_machine()
    client = Client(base_url=machine.base_url, tls=machine.tls_config, version="auto")
    client.ping()
    return client

def create_app(client, user, app, async=True):
    name = get_container_name(user, app.app_id)
    if (async):
        if name in updating_apps:
            raise RuntimeError("Already updating " + name)
        updating_apps.add(name)
        if getattr(user, "_get_current_object", None):
            user = user._get_current_object()
        task(create_app, client, user, app, async=False)
        return
    
    try:
        project = get_project(client, user, app)
        project.up()
    finally:
        updating_apps.remove(name)
        
def delete_app(client, user, app, async=True):
    name = get_container_name(user, app.app_id)
    if (async):
        if name in updating_apps:
            raise RuntimeError("Already updating " + name)
        updating_apps.add(name)
        if getattr(user, "_get_current_object", None):
            user = user._get_current_object()
        task(delete_app, client, user, app, async=False)
        return
    
    try:
        project = get_project(client, user, app)
        project.stop()
        project.remove_stopped()
    finally:
        updating_apps.remove(name)

def get_app_status(client, user, app):
    name = get_container_name(user, app.app_id)
    if name in updating_apps:
        return "updating"
    containers = get_containers(client)
    container = [c for c in containers if "/" + name in c["Names"]]
    if len(container) > 0:
        return "running"
    else:
        return "stopped"
           
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
 
