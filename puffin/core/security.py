import uuid
import datetime

import flask
import flask_security
import flask_security.datastore
import flask_security.forms
import flask_security.utils
import flask_security.signals
import wtforms
from wtforms import validators

from puffin import app
from .db import db
from . import mail


class User(flask_security.UserMixin):
    
    def __init__(self, login, name, email, password, active, roles, 
            confirmed=False):
        self.login = login
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        if confirmed:
            self.confirmed_at = datetime.datetime.now()
    
    @property
    def id(self):
        return self.user_id

    @property
    def roles(self):
        return []

    @roles.setter
    def roles(self, role):
        pass

    @property
    def confirmed(self):
        return self.confirmed_at != None
 
    def __eq__(self, other):
        if other == None:
            return False
        # Need to use get_id method because AnonymousUser has it, and it's used
        # during registration email verification
        return self.get_id() == other.get_id()

    def __hash__(self):
        return hash(self.get_id())


security = None

def init():
    global security
    
    app.config['SECURITY_CONFIRMABLE'] = not app.config['MAIL_SUPPRESS_SEND']
    app.config['SECURITY_CHANGEABLE'] = True
    app.config['SECURITY_SEND_PASSWORD_CHANGE_EMAIL'] = not app.config['MAIL_SUPPRESS_SEND']
    app.config['SECURITY_POST_CHANGE_VIEW'] = "profile.html"
    app.config['SECURITY_PASSWORD_HASH'] = "bcrypt"
    app.config['SECURITY_MSG_CONFIRMATION_REQUIRED'] = (
            flask.Markup('Email requires confirmation. <a href="/confirm">Resend confirmation instructions</a>.'), 
            'error')
    # This comes from config: app.config['SECURITY_REGISTERABLE']

    # Update all salts with SECRET_KEY if they are not set
    secret_key = app.config['SECRET_KEY']
    for salt in ('SECURITY_PASSWORD_SALT', 'SECURITY_CONFIRM_SALT', 
            'SECURITY_RESET_SALT', 'SECURITY_LOGIN_SALT', 
            'SECURITY_REMEMBER_SALT'):
        app.config[salt] = app.config.get(salt, secret_key)

    app.config['SECURITY_EMAIL_SENDER'] = app.config['MAIL_DEFAULT_SENDER']

    app.config['SECURITY_POST_LOGIN_VIEW'] = "/"

    security = flask_security.Security(app, CustomUserDatastore(), 
            login_form=CustomLoginForm,
            register_form=CustomRegisterForm,
            confirm_register_form=CustomRegisterForm)

    security.send_mail_task(send_security_mail)

    if app.config['SECURITY_CONFIRMABLE'] and app.config['NEW_USER_NOTIFICATION']:
        flask_security.signals.user_confirmed.connect(new_user_notification, app)


class CustomUserDatastore(flask_security.datastore.SQLAlchemyDatastore, flask_security.datastore.UserDatastore):
    
    def __init__(self):
        flask_security.datastore.SQLAlchemyDatastore.__init__(self, db)
        flask_security.datastore.UserDatastore.__init__(self, User, None)

    def get_user(self, identifier):
        if isinstance(identifier, uuid.UUID):
            user = db.session.query(User).get(identifier)
        else:
            user = db.session.query(User).filter_by(email=identifier).first()
            if user == None:
                user = db.session.query(User).filter_by(login=identifier).first()
        return user

    def find_user(self, **kwargs):
        if "id" in kwargs:
            kwargs["user_id"] = kwargs["id"]
            del kwargs["id"]
        user = db.session.query(User).filter_by(**kwargs).first()
        return user

    def find_role(self, role):
        return None

class CustomLoginForm(flask_security.forms.LoginForm):

    email = wtforms.StringField("Email or Login")

class CustomRegisterForm(flask_security.forms.RegisterForm):
    
    login = wtforms.StringField('Login', validators=[validators.Required(), validators.Length(3, 32), 
            validators.Regexp(r'^[a-z][a-z0-9_]*$', 0, 'Login must have only lowercase letters, numbers or underscores')])

    name = wtforms.StringField('Name', validators=[validators.Required(), validators.Length(1, 64), 
            validators.Regexp(r'^[A-Za-z0-9_\- ]+$', 0, 'Name must have only letters, numbers, spaces, dots, dashes or underscores')])

def send_security_mail(message):
    mail.send(message=message)

def new_user_notification(sender, user):
    admin = get_admin()
    mail.send(recipient=admin.email, subject="New Puffin user: " + user.login, template="new_user", user=user)

def get_user(login):
    return security.datastore.get_user(login)

def create_user(login):
    user = security.datastore.create_user(login=login, name=login.capitalize(), 
        email=login + "@" + app.config["SERVER_NAME_FULL"], 
        password=flask_security.utils.encrypt_password(login),
        confirmed=True)
    update_user(user)

def get_all_users():
    return db.session.query(User).order_by(User.login).all()

def activate_user(login):
    user = db.session.query(User).filter_by(login=login).first()
    result = security.datastore.activate_user(user)
    update_user(user)
    return result

def deactivate_user(login):
    user = db.session.query(User).filter_by(login=login).first()
    result = security.datastore.deactivate_user(user)
    update_user(user)
    return result

def update_user(user):
    db.session.add(user)
    db.session.commit()

def get_admin():
    return get_user("puffin")
