from .model import Machine

from docker import Client
from docker.tls import TLSConfig



REMOTE_MACHINE = Machine("https://52.29.5.191:2376", 
    TLSConfig(
        client_cert=(
            '/home/loomchild/.docker/machine/machines/frankfurt/cert.pem', 
            '/home/loomchild/.docker/machine/machines/frankfurt/key.pem'),
        verify='/home/loomchild/.docker/machine/machines/frankfurt/ca.pem'
    ))

LOCAL_MACHINE = Machine('unix://var/run/docker.sock')

def init():
    pass

def get_client(machine=LOCAL_MACHINE):
    client = Client(base_url=machine.base_url, tls=machine.tls_config, version="auto")
    client.ping()
    return client
