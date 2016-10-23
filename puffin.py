#!/usr/bin/env python3

from waitress import serve
from reload import reload_me
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, upgrade as db_upgrade
import pytest

from puffin import app
from puffin import core
from puffin.core import db, queue, mail, security, docker, applications, machine, compose

from time import sleep

manager = Manager(app, with_default_commands=False)


@manager.command
@manager.option("-r", "--reload", action="store_true", 
        help="Reload the server if any file changes")
def server(reload=False):
    "Run the server"
    if reload:
        reload_me("server")
    else:
        serve(app, host=app.config["HOST"], port=app.config["PORT"], 
                threads=app.config["THREADS"])


def make_shell_context():
    return dict(app=app, db=db.db, queue=queue, mail=mail, 
        security=security, docker=docker, applications=applications,
        machine=machine, compose=compose)

manager.add_command("shell", Shell(make_context=make_shell_context))


@MigrateCommand.command
def create():
    "Create the database"
    db_create()

def db_create():
    name = app.config["DB_NAME"]
    create_database(name)
    create_database(name + "_test")

def create_database(name):
    if db.create(name):
        print("Created {} database".format(name))

manager.add_command('db', MigrateCommand)


machine = Manager(usage="Perform hosting server operations")

@machine.command
def network():
    "Create Docker networks"
    machine_network()

def machine_network():
    if docker.create_networks():
        print("Created Docker networks on machine")

@machine.command
def proxy():
    "Install Docker proxy"
    machine_proxy()

def machine_proxy():
    if docker.install_proxy():
        print("Installed Docker proxy on machine")

@machine.command
def mail():
    "Install Docker mail"
    machine_mail()

def machine_mail():
    if docker.install_mail():
        print("Installed Docker mail on machine")

manager.add_command("machine", machine)


user = Manager(usage="Manage users")

@user.command
def create(login):
    "Create a user"
    user_create(login)

def user_create(login):
    user = security.get_user(login)
    if not user:
        security.create_user(login)
    else:
        print("User {} already exists".format(login))

@user.command
def activate(login):
    "Activate a user"
    user_activate(login)

def user_activate(login):
    if not security.activate_user(login):
        print("User {} is already active".format(login))

@user.command
def deactivate(login):
    "Deactivate a user"
    user_deactivate(login)

def user_deactivate(login):
    if not security.deactivate_user(login):
        print("User {} is already not active".format(login))

@user.command
def list():
    "List all users"
    user_list()

def user_list():
    users = security.get_all_users()
    line_format = "{:<14} {:<26} {:<20} {!s:<6} {!s:<9}"
    print(line_format.format("Login", "Email", "Name", "Active", "Confirmed"))
    print("-" * 79)
    for user in users:
        print(line_format.format(user.login, user.email, user.name, 
                user.active, user.confirmed))

manager.add_command("user", user)


@manager.command
def test():
    pytest.main()


@manager.command
def wait():
    "Wait until dependencies are up"
    sleep(6)


def init():
    "Initialize Puffin dependencies"
    wait()
    db_create()
    db_upgrade()
    user_create("puffin")
    machine_network()
    machine_proxy()
    machine_mail()


@manager.command
@manager.option("-r", "--reload", action="store_true", 
        help="Reload the server if any file changes")
def up(reload=False):
    "Initialize Puffin dependencies and run the server"
    init()
    server(reload)


if __name__ == "__main__":
    core.init()
    manager.run()

