from . import config
from . import db
from . import mail
from . import queue
from . import security
from . import apps
from . import docker

def init():
    config.init()
    db.init()
    queue.init()
    mail.init()
    security.init()
    apps.init()
    docker.init()

