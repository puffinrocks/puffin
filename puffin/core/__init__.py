from . import config
from . import db
from . import mail
from . import queue
from . import security
from . import applications
from . import machine
from . import compose
from . import docker

def init():
    config.init()
    db.init()
    queue.init()
    mail.init()
    security.init()
    applications.init()
    machine.init()
    compose.init()
    docker.init()
    stats.init()

