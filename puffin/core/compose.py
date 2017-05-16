import os 
import subprocess

from puffin import app
from . import applications
from . import machine as machine_module
from . import security


def init():
    pass

def compose_start(machine, user, application, **environment):
    return compose_run(machine, user, application, "up", "-d", **environment)

def compose_stop(machine, user, application):
    return compose_run(machine, user, application, "down")

def compose_run(machine, user, application, *arguments, **environment):
    name = applications.get_application_name(user, application)
    args = ["docker-compose", "-f", application.compose, "-p", name]
    args += arguments

    domain = applications.get_application_domain(user, application)
    env = dict(PATH=os.environ['PATH'], VIRTUAL_HOST=domain)

    if app.config["LETSENCRYPT"] and applications.get_application_https(user, application):
        admin = security.get_admin()
        env.update(LETSENCRYPT_HOST=domain, LETSENCRYPT_EMAIL=admin.email,
                LETSENCRYPT_TEST="true" if app.config["LETSENCRYPT_TEST"] else "")

    env.update(machine_module.get_env_vars(machine))
    env.update(**environment)

    process = subprocess.Popen(args, 
            stderr=subprocess.STDOUT, stdout=subprocess.PIPE, 
            universal_newlines=True, env=env)
    process.wait()
    out, err = process.communicate()
    out = out.strip()
    return out

