#!/usr/bin/env python3

from waitress import serve
from flask.ext.script import Manager, Shell
from flask.ext.migrate import MigrateCommand

from puffin import app
from puffin import core
from puffin.core import model, db, queue, mail

manager = Manager(app, with_default_commands=False)

@manager.command
def server():
    "Run the server"
    serve(app, host=app.config["HOST"], port=app.config["PORT"], 
            threads=app.config["THREADS"])

def make_shell_context():
    return dict(app=app, db=db.db, model=model, queue=queue, mail=mail)
manager.add_command("shell", Shell(make_context=make_shell_context))

@MigrateCommand.command
def create():
    name = app.config["DB_NAME"]
    create_database(name)
    create_database(name + "_test")
def create_database(name):
    if db.create(name):
        print("Created {} database".format(name))

manager.add_command('db', MigrateCommand)


if __name__ == "__main__":
    core.init()
    manager.run()

