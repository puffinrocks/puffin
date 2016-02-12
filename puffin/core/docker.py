from .machine import get_machine
from .applications import get_application
from .queue import task, task_exists
from .model import User, Application, ApplicationStatus, PUFFIN_USER
from .db import db
from .. import app

from docker import Client

from compose import config
from compose.project import Project

import requests
from requests.exceptions import RequestException
from time import time, sleep

# How long to wait after creating an app, to allow dependencies startup
APPLICATION_SLEEP_AFTER_CREATE = 10

# How long wait for application startup
APPLICATION_CREATE_TIMEOUT = 60


def init():
    pass

def get_client():
    machine = get_machine()
    client = Client(base_url=machine.base_url, tls=machine.tls_config, version="auto")
    client.ping()
    return client

def create_application(client, user, application):
    if get_application_status(client, user, application) != ApplicationStatus.DELETED:
        raise RuntimeError("Application already installed or updating, user: {}, application: {}".format(user.login, application.application_id))
    name = get_container_name(user, application.application_id)
    task(name, create_application_task, client, user.user_id, application)

def create_application_task(client, user_id, application):
    user = db.session.query(User).get(user_id)
    create_application_do(client, user, application)
    application_url = "http://" + get_application_domain(user, application)
    sleep(APPLICATION_SLEEP_AFTER_CREATE)
    wait_until_up(application_url)

def create_application_do(client, user, application):
    project = get_project(client, user, application)
    # This creates new image, but doesn't cost much because it uses cache
    project.build()
    project.up()
        
def delete_application(client, user, application, async=True):
    if get_application_status(client, user, application) != ApplicationStatus.CREATED:
        raise RuntimeError("Application not installed or updating, user: {}, application: {}".format(user.login, application.application_id))
    name = get_container_name(user, application.application_id)
    task(name, delete_application_task, client, user.user_id, application)

def delete_application_task(client, user_id, application):
    user = db.session.query(User).get(user_id)
    delete_application_do(client, user, application)

def delete_application_do(client, user, application):
    project = get_project(client, user, application)
    project.stop()
    # Do not remove to avoid losing the data
    # project.remove_stopped()

def get_application_status(client, user, application):
    name = get_container_name(user, application.application_id)
    if task_exists(name):
        return ApplicationStatus.UPDATING
    container = get_container(client, name)
    if container:
        return ApplicationStatus.CREATED
    else:
        return ApplicationStatus.DELETED

def get_application_domain(user, application):
    domain = app.config["SERVER_NAME"] or "localhost"
    return application.application_id + "." + user.login + "." + domain

def get_project(client, user, application):
    name = get_container_name(user, application.application_id)
    config_details = config.find(application.path, [application.compose])
    project_config = config.load(config_details)

    project = Project.from_dicts(name, project_config, client, False, None)

    service = project.get_service("main")
    
    ports = service.options.get("ports", [])
    
    service.options["container_name"] = name

    environment = service.options.get("environment", {})
    service.options["environment"] = environment
    environment["VIRTUAL_HOST"] = get_application_domain(user, application)
    if ports:
        environment["VIRTUAL_PORT"] = ports[0]

    return project

def get_container_name(user, application_id):
    return user.login + "_" + application_id

def get_containers(client):
    return client.containers()
 
def get_container(client, name):
    containers = get_containers(client)
    container = [c for c in containers if "/" + name in c["Names"]]
    if len(container) > 0:
        return container
    else:
        return None

def wait_until_up(url, timeout=APPLICATION_CREATE_TIMEOUT):
    start_time = time()
    while True:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                break
        except RequestException:
            pass
        if start_time + timeout <= time():
            break
        sleep(1)

def install_proxy():
    client = get_client()
    user = PUFFIN_USER
    application = get_application("_proxy")
    if get_application_status(client, user, application) != ApplicationStatus.DELETED:
        return False
    create_application_do(client, user, application)
    return True

