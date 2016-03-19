from .machine import get_machine, get_tls_config
from .compose import compose_start, compose_stop
from .applications import get_application, get_application_domain, get_application_list, get_application_name
from .queue import task, task_exists
from .model import User, Application, ApplicationStatus
from .security import get_user
from .db import db
from .. import app

from docker import Client

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
    client = Client(base_url=machine.url, tls=get_tls_config(machine), version="auto")
    client.ping()
    return client

def create_application(client, user, application):
    if get_application_status(client, user, application) != ApplicationStatus.DELETED:
        raise RuntimeError("Application already installed or updating, user: {}, application: {}".format(user.login, application.application_id))
    name = get_application_name(user, application)
    task(name, create_application_task, user.user_id, application)

def create_application_task(user_id, application):
    user = db.session.query(User).get(user_id)
    compose_start(get_machine(), user, application)
    application_url = "http://" + get_application_domain(user, application)
    sleep(APPLICATION_SLEEP_AFTER_CREATE)
    wait_until_up(application_url)

def delete_application(client, user, application, async=True):
    if get_application_status(client, user, application) != ApplicationStatus.CREATED:
        raise RuntimeError("Application not installed or updating, user: {}, application: {}".format(user.login, application.application_id))
    name = get_application_name(user, application)
    task(name, delete_application_task, user.user_id, application)

def delete_application_task(user_id, application):
    user = db.session.query(User).get(user_id)
    compose_stop(get_machine(), user, application)

def get_application_status(client, user, application):
    name = get_application_name(user, application)
    containers = get_containers(client)
    return _get_application_status(containers, name)

def get_application_statuses(client, user):
    applications = get_application_list()
    containers = get_containers(client)
    application_statuses = []
    for application in applications:
        name = get_application_name(user, application)
        status = _get_application_status(containers, name)
        application_statuses.append((application, status))
    return application_statuses

def _get_application_status(containers, name):
    if task_exists(name):
        return ApplicationStatus.UPDATING
    container = get_container(containers, name)
    if container:
        return ApplicationStatus.CREATED
    else:
        return ApplicationStatus.DELETED
    
def get_containers(client):
    return client.containers()
 
def get_container(containers, name):
    main_name = "/" + name + "_main_1"
    container = [c for c in containers if main_name in c["Names"]]
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
    return _install("_proxy")

def install_mail():
    env = {
        'MAIL_SERVER': app.config['MAIL_SERVER'], 
        'MAIL_PORT': str(app.config['MAIL_PORT']),
        'MAIL_USERNAME': app.config['MAIL_USERNAME'] or 'username',
        'MAIL_PASSWORD': app.config['MAIL_PASSWORD'] or 'password',
    }
    
    return _install("_mail", **env)

def install_dns():
    return _install("_dns")

def _install(name, **environment):
    client = get_client()
    user = get_user("puffin")
    application = get_application(name)
    if get_application_status(client, user, application) != ApplicationStatus.DELETED:
        return False
    compose_start(get_machine(), user, application, **environment)
    return True

def create_networks():
    #TODO: replace with running _network app and remove prefix once custom network names supported
    client = get_client()
    networks = client.networks(names=("network_front", "network_back"))
    if len(networks) == 2:
        return False
    client.create_network("network_front")
    client.create_network("network_back")
    return True


