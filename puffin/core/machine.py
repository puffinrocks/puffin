import docker.tls

from puffin import app


class Machine:
    
    def __init__(self, url, path):
        self.url = url
        self.path = path

    @property
    def cert(self):
        return self.path + 'cert.pem' if self.path else None
    
    @property
    def key(self):
        return self.path + 'key.pem' if self.path else None
    
    @property
    def ca(self):
        return self.path + 'ca.pem' if self.path else None


def init():
    pass

def get_machine():
    url = app.config["MACHINE_URL"]
    path = app.config["MACHINE_PATH"]

    return Machine(url, path)


def get_tls_config(machine):
    if not machine.path:
        return None

    return docker.tls.TLSConfig(
        client_cert=(machine.cert, machine.key),
        verify=machine.ca,
        assert_hostname = False
    )

def get_env_vars(machine):
    env = dict(DOCKER_HOST=machine.url)
    
    if machine.path:
        env.update(dict(DOCKER_TLS_VERIFY="1", DOCKER_CERT_PATH=machine.path))

    return env
