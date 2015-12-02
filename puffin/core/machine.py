from docker.tls import TLSConfig

from .. import app
from .model import Machine


def init():
    pass

def get_machine():
    url = app.config["MACHINE_URL"]
    path = app.config["MACHINE_PATH"]

    tls_config = None
    if path:
        tls_config = TLSConfig(
            client_cert=(path + 'cert.pem', path + 'key.pem'),
            verify=path + 'ca.pem'
        )

    return Machine(url, tls_config)

