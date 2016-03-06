from docker.tls import TLSConfig

from .. import app
from .model import Machine


def init():
    pass

def get_machine():
    url = app.config["MACHINE_URL"]
    path = app.config["MACHINE_PATH"]

    return Machine(url, path)


def get_tls_config(machine):
    if not machine.path:
        return None

    return TLSConfig(
        client_cert=(machine.cart, machine.key),
        verify=machine.ca,
        assert_hostname = False
    )

def get_env_vars(machine):
    env = dict(DOCKER_HOST=machine.url)
    
    if machine.path:
        env.update(dict(DOCKER_TLS_VERIFY="1", DOCKER_CERT_PATH=machine.path))

    return env
