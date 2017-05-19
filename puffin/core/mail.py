import flask
import flask_mail

from puffin import app
from . import queue


mail = flask_mail.Mail()

def init():
    mail.init_app(app)

def send(recipient=None, subject=None, template=None, message=None, async=True, **kwargs):
    if not (message or (recipient and subject and template)):
        raise ValueError("Provide recipient, subject, template or message")

    if not message:
        message = create_message(recipient, subject, template, **kwargs)

    if async:
        queue.task(None, send_message, message)
    else:
        send_message(message)

def send_message(message):
    mail.send(message)

def create_message(recipient, subject, template, **kwargs):
    message = flask_mail.Message(subject, recipients=[recipient])
    message.body = flask.render_template("mail/" + template + ".txt", **kwargs)
    return message
