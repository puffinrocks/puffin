from docker import Client
from .machine import get_machine

DOMAIN = "stinky"

def init():
    pass

def get_client():
    machine = get_machine()
    client = Client(base_url=machine.base_url, tls=machine.tls_config, version="auto")
    client.ping()
    return client

def get_container(client, user, app_id):
    containers = get_containers(client)
    container_name = get_container_name(user, app_id)
    container = [c for c in containers if "/" + container_name in c["Names"]]
    if len(container) > 0:
        return container[0]
    else:
        return None

def get_container_name(user, app_id):
    return user.login + "_" + app_id

def get_container_domain(user, app_id):
    return app_id + "." + user.login + "." + DOMAIN

def get_containers(client):
    return client.containers()
 
def create_container(client, user, app):
    name = get_container_name(user, app.app_id)
    client.pull(app.image)
    container = client.create_container(
        image=app.image,
        name=name,
        ports=[app.port],
        environment={
            "VIRTUAL_HOST": get_container_domain(user, app.app_id),
            "VIRTUAL_PORT": app.port,
        }
    )
    client.start(container)

