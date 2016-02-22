#!/usr/bin/env python3

from waitress import serve
from flask.ext.script import Manager, Shell
from flask.ext.migrate import MigrateCommand

from puffin import app
from puffin import core
from puffin.core import model, db, queue, mail, security, docker

manager = Manager(app, with_default_commands=False)

@manager.command
def server():
    "Run the server"
    serve(app, host=app.config["HOST"], port=app.config["PORT"], 
            threads=app.config["THREADS"])

def make_shell_context():
    return dict(app=app, db=db.db, model=model, queue=queue, mail=mail, 
        security=security, docker=docker)
manager.add_command("shell", Shell(make_context=make_shell_context))

@MigrateCommand.command
def create():
    "Create the database"
    name = app.config["DB_NAME"]
    create_database(name)
    create_database(name + "_test")
def create_database(name):
    if db.create(name):
        print("Created {} database".format(name))

manager.add_command('db', MigrateCommand)


machine = Manager(usage="Perform hosting server operations")

manager.add_command("machine", machine)

@machine.command
def proxy():
    "Install docker proxy"
    if docker.install_proxy():
        print("Installed docker proxy on machine")


user = Manager(usage="Manage users")

manager.add_command("user", user)

@user.command
def create(login):
    "Create a user"
    user = security.get_user(login)
    if not user:
        security.create_user(login)
    else:
        print("User {} already exists".format(login))

@user.command
def activate(login):
    "Activate a user"
    if not security.activate_user(login):
        print("User {} is already active".format(login))

@user.command
def deactivate(login):
    "Deactivate a user"
    if not security.deactivate_user(login):
        print("User {} is already not active".format(login))

@user.command
def list():
    "List all users"
    users = security.get_all_users()
    line_format = "{:<14} {:<26} {:<20} {!s:<6} {!s:<9}"
    print(line_format.format("Login", "Email", "Name", "Active", "Confirmed"))
    print("-" * 79)
    for user in users:
        print(line_format.format(user.login, user.email, user.name, 
                user.active, user.confirmed))

if __name__ == "__main__":
    core.init()
    manager.run()

