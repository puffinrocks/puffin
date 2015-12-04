from flask import render_template
from flask.ext.mail import Mail, Message
from .. import app
from .queue import task


mail = Mail()

def init():
    mail.init_app(app)

def send(recipient=None, subject=None, template=None, message=None, async=True, **kwargs):
    if not (message or (recipient and subject and template)):
        raise ValueError("Provide recipient, subject, template or message")

    if not message:
        message = create_message(recipient, subject, template, **kwargs)
    
    if async:
        task(None, send_message, app, message)
    else:
        send_message(app, message)

def send_message(app, message):
    with app.app_context():
        mail.send(message)

def create_message(recipient, subject, template, **kwargs):
    message = Message(subject, recipients=[recipient])
    message.body = render_template("mail/" + template + ".txt", **kwargs)
    return message
