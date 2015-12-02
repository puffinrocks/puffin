from docker.tls import TLSConfig

from .. import app
from .model import Machine


def init():
    pass

def get_machine():
    if app.config["MACHINE"] == "remote":
        return get_remote_machine()
    else:
        return get_local_machine()

def get_local_machine():
    return Machine('unix://var/run/docker.sock')

def get_remote_machine():
    return Machine("https://52.29.5.191:2376", 
        TLSConfig(
            client_cert=(
                '/home/loomchild/.docker/machine/machines/frankfurt/cert.pem', 
                '/home/loomchild/.docker/machine/machines/frankfurt/key.pem'),
            verify='/home/loomchild/.docker/machine/machines/frankfurt/ca.pem'
        ))

