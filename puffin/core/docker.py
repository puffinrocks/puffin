import time
import inspect

import requests
import requests.exceptions
import docker
import docker.errors

from puffin import app
from .db import db
from . import machine as machine_module
from . import compose
from . import network
from . import applications
from . import queue
from . import security
from . import backup
from .. import util


# How long to wait after creating an app, to allow dependencies startup
APPLICATION_SLEEP_AFTER_CREATE = 10

# How long wait for application startup
APPLICATION_CREATE_TIMEOUT = 120


def init():
    pass

def get_client():
    machine = machine_module.get_machine()
    client = docker.DockerClient(base_url=machine.url, tls=machine_module.get_tls_config(machine), version="auto")
    client.ping()
    return client

def create_application(client, user, application):
    if get_application_status(client, user, application) != applications.ApplicationStatus.DELETED:
        raise RuntimeError("Application already installed or updating, user: {}, application: {}".format(user.login, application.application_id))
    name = applications.get_application_name(user, application)
    queue.task(name, create_application_task, user.user_id, application)

def create_application_task(user_id, application):
    user = db.session.query(security.User).get(user_id)
    network.create_network(get_client(), applications.get_application_name(user, application) + "_default")
    compose.compose_start(machine_module.get_machine(), user, application)
    application_url = "http://" + applications.get_application_domain(user, application)
    time.sleep(APPLICATION_SLEEP_AFTER_CREATE)
    wait_until_up(application_url)
    applications.set_application_started(user, application, True)

def delete_application(client, user, application, async=True):
    if get_application_status(client, user, application) != applications.ApplicationStatus.CREATED:
        raise RuntimeError("Application not installed or updating, user: {}, application: {}".format(user.login, application.application_id))
    name = applications.get_application_name(user, application)
    queue.task(name, delete_application_task, user.user_id, application)

def delete_application_task(user_id, application):
    user = db.session.query(security.User).get(user_id)
    compose.compose_stop(machine_module.get_machine(), user, application)
    backup.backup(user, application)
    applications.set_application_started(user, application, False)

def run_service(user, application, service, *arguments, **environment):
    return compose.compose_run(machine_module.get_machine(), user, application, "run", "--rm", service, *arguments, **environment)

def get_application_status(client, user, application):
    container = get_main_container(client, user, application)
    return _get_application_status(user, application, container)

def get_application_statuses(client, user):
    apps = applications.get_applications()
    application_statuses = []
    container_name = applications.get_application_name(user, None) + ".*_main_1"
    containers = get_containers(client, container_name)
    for container in containers:
        user_application_id = _get_user_application_id(container)
        if not user_application_id:
            continue
        login, application_id = user_application_id

        application = apps.get(application_id)
        if not application:
            continue

        status = _get_application_status(user, application, container)
        application_statuses.append((application, status))
    return application_statuses

def _get_application_status(user, application, container):
    name = applications.get_application_name(user, application)
    if queue.task_exists(name):
        return applications.ApplicationStatus.UPDATING
    if container:
        return applications.ApplicationStatus.CREATED
    else:
        return applications.ApplicationStatus.DELETED
    
def get_all_running_applications():
    apps = applications.get_applications()
    users = {u.login : u for u in security.get_all_users()}
    
    client = get_client()
    containers = get_containers(client, "_main_1")
    
    running_applications = []
    for container in containers:
        user_application_id = _get_user_application_id(container)
        if not user_application_id:
            continue
        login, application_id = user_application_id
        
        application = apps.get(application_id)
        user = users.get(login)
        if not application or not user:
            continue

        running_applications.append((user, application))

    return set(running_applications)

def _get_user_application_id(container):
    if container.name.endswith("_main_1"):
        return applications.get_user_application_id(container.name[:-7])
    return None

def get_application_image_version(client, application):
    image_name = application.main_image
    try:
        image = client.images.get(image_name)
    except docker.errors.ImageNotFound:
        return None
    env_list = util.safe_get(image.attrs, "Config", "Env")
    env = util.env_dict(env_list)
    return env.get("VERSION")

def get_application_version(client, user, application):
    name = applications.get_application_name(user, application)
    container = get_main_container(client, user, application)
    if not container:
        return None
    env_list = util.safe_get(container.attrs, "Config", "Env")
    env = util.env_dict(env_list)
    return env.get("VERSION")

def get_containers(client, name=""):
    return client.containers.list(filters=dict(name=name))
 
def get_main_container(client, user, application):
    name = applications.get_application_name(user, application) + "_main_1"
    containers = get_containers(client, name)
    if len(containers) == 1:
        return containers[0]
    else:
        return None

def wait_until_up(url, timeout=APPLICATION_CREATE_TIMEOUT):
    start_time = time.time()
    while True:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass
        if start_time + timeout <= time.time():
            break
        time.sleep(1)

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
    user = security.get_user("puffin")
    application = applications.get_application(name)
    if get_application_status(client, user, application) != applications.ApplicationStatus.DELETED:
        return False
    compose.compose_start(machine_module.get_machine(), user, application, **environment)
    return True

def create_networks():
    #TODO: replace with running _network app and remove prefix once custom network names supported
    client = get_client()
    networks = client.networks.list(names=["puffin_front", "puffin_back"])
    if len(networks) == 2:
        return False
    client.networks.create("puffin_front")
    client.networks.create("puffin_back")
    return True

def create_volumes():
    client = get_client()
    volumes = client.volumes.list(filters={"name" : "puffin_backup"})
    if len(volumes) > 0:
        return False
    client.volumes.create("puffin_backup")
    return True
