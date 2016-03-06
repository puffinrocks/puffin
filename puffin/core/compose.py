from .applications import get_application_domain, get_application_name
from .machine import get_env_vars
from .. import app

from subprocess import Popen, STDOUT, PIPE
from os import environ
from os.path import join


def init():
    pass

def compose_start(machine, user, application):
    compose_run(machine, user, application, "up", "-d")

def compose_stop(machine, user, application):
    compose_run(machine, user, application, "stop")

def compose_run(machine, user, application, *commands):
    name = get_application_name(user, application)
    path = join(application.path, application.compose)
    args = ["docker-compose", "-f", path, "-p", name]
    args += commands

    domain = get_application_domain(user, application)
    env = dict(PATH=environ['PATH'], VIRTUAL_HOST=domain)
    env.update(get_env_vars(machine))

    process = Popen(args, stderr=STDOUT, stdout=PIPE, universal_newlines=True, env=env)
    process.wait()
    out, err = process.communicate()
    print(out)
    #app.logger.info("Compose:", out)

