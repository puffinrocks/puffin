#!/usr/bin/env python3

import time
import sys

import waitress
import reload as reload_module
import flask_script
import flask_migrate
import pytest

from puffin import app
from puffin import core
from puffin.core import db
from puffin.core import queue
from puffin.core import mail
from puffin.core import security
from puffin.core import docker
from puffin.core import applications
from puffin.core import machine
from puffin.core import compose
from puffin.core import network
from puffin.core import backup as backup_module


manager = flask_script.Manager(app, with_default_commands=False)


@manager.command
@manager.option("-r", "--reload", action="store_true", 
        help="Reload the server if any file changes")
def server(reload=False):
    "Run the server"
    if reload:
        reload_module.reload_me("server")
    else:
        waitress.serve(app, host=app.config["HOST"], port=app.config["PORT"], 
                threads=app.config["THREADS"])


def make_shell_context():
    return dict(app=app, db=db.db, queue=queue, mail=mail, 
        security=security, docker=docker, applications=applications,
        machine=machine, compose=compose, network=network)

manager.add_command("shell", flask_script.Shell(make_context=make_shell_context))


@flask_migrate.MigrateCommand.command
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

manager.add_command('db', flask_migrate.MigrateCommand)


machine = flask_script.Manager(usage="Perform hosting server operations")

@machine.command
def network():
    "Create Docker networks"
    machine_network()

def machine_network():
    if docker.create_networks():
        print("Created Docker networks on machine")

@machine.command
def volume():
    "Create Docker volumes"
    machine_volume()

def machine_volume():
    if docker.create_volumes():
        print("Created Docker volumes on machine")


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


user = flask_script.Manager(usage="Manage users")

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


application = flask_script.Manager(usage="Manage apps")

@application.command
def list():
    "List all apps"
    app_list()

def app_list():
    started_applications = applications.get_all_started_applications()
    running_applications = docker.get_all_running_applications()
    all_applications = sorted(started_applications.union(running_applications),
            key=lambda a: (a[0].login, a[1].application_id))

    line_format = "{:<14} {:<20} {:<3} {:<30}"
    print(line_format.format("User", "Application", "Run", "Domain"))
    print("-" * 79)
    for application in all_applications:

        running = "Y" if application in running_applications else "N"

        user = application[0]
        app = application[1]
        domain = applications.get_application_domain(user, app)
        if domain:
            domain = "http://" + domain

        print(line_format.format(user.login, app.application_id, running, domain))

@application.command
def init_running():
    "Initialize currently running applications"
    app_init_running()

def app_init_running():
    running_applications = docker.get_all_running_applications()
    for (user, application) in running_applications:
        if not applications.get_application_started(user, application):
            print("Marking user: {}, application: {} as started"
                    .format(user.login, application.application_id))
            applications.set_application_started(user, application, True)

@application.command
def backup(user, application):
    "Backup application"
    app_backup(user, application)

def app_backup(user_login, application_id):
    user = get_existing_user(user_login)
    application = get_existing_application(application_id)
    backup_module.backup(user, application)

@application.command
def restore(user, application, name):
    "Restore application from backup with given name"
    app_restore(user, application, name)

def app_restore(user_login, application_id, backup_name):
    user = get_existing_user(user_login)
    application = get_existing_application(application_id)
    backups = backup_module.restore(user, application, backup_name)

@application.command
def backups(user, application):
    "List application backups"
    app_backups(user, application)

def app_backups(user_login, application_id):
    user = get_existing_user(user_login)
    application = get_existing_application(application_id)
    backups = backup_module.list(user, application)
    for backup in backups:
        print(backup)

manager.add_command("app", application)


@manager.command
@manager.option("-c", "--coverage", action="store_true", 
        help="Report test code coverage")
def test(coverage=False):
    "Run automated tests"
    args = []

    if coverage:
        args.append("--cov=.")

    pytest.main(args)


@manager.command
def wait():
    "Wait until dependencies are up"
    time.sleep(6)


def init():
    "Initialize Puffin dependencies"
    wait()
    db_create()
    flask_migrate.upgrade()
    user_create("puffin")
    machine_network()
    machine_volume()
    machine_proxy()
    machine_mail()


@manager.command
@manager.option("-r", "--reload", action="store_true", 
        help="Reload the server if any file changes")
def up(reload=False):
    "Initialize Puffin dependencies and run the server"
    init()
    server(reload)


def get_existing_user(user_login):
    user = security.get_user(user_login)
    if not user:
        raise Exception("User {} does not exist".format(user_login))
    return user

def get_existing_application(application_id):
    application = applications.get_application(application_id)
    if not application:
        raise Exception("Application {} does not exist".format(application_id))
    return application


if __name__ == "__main__":
    core.init()
    manager.run()

