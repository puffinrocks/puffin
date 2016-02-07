from uuid import UUID
from flask_security import Security
from flask_security.datastore import SQLAlchemyDatastore, UserDatastore
from flask_security.forms import LoginForm, RegisterForm
from flask_security.utils import encrypt_password
from flask import Markup
from wtforms import StringField
from wtforms.validators import Required, Length, Regexp
from .. import app
from .model import User
from .db import db
from .config import DefaultConfig
from .mail import send
 

security = None

def init():
    global security

    app.config['SECURITY_REGISTERABLE'] = True
    app.config['SECURITY_CONFIRMABLE'] = True
    app.config['SECURITY_CHANGEABLE'] = True
    app.config['SECURITY_SEND_PASSWORD_CHANGE_EMAIL'] = True
    app.config['SECURITY_POST_CHANGE_VIEW'] = "profile.html"
    app.config['SECURITY_PASSWORD_HASH'] = "bcrypt"
    app.config['SECURITY_MSG_CONFIRMATION_REQUIRED'] = (
            Markup('Email requires confirmation. <a href="/confirm">Resend confirmation instructions</a>.'), 
            'error')

    # Update all salts with SECRET_KEY if they are not set
    secret_key = app.config['SECRET_KEY']
    for salt in ('SECURITY_PASSWORD_SALT', 'SECURITY_CONFIRM_SALT', 
            'SECURITY_RESET_SALT', 'SECURITY_LOGIN_SALT', 
            'SECURITY_REMEMBER_SALT'):
        app.config[salt] = app.config.get(salt, secret_key)

    app.config['SECURITY_EMAIL_SENDER'] = app.config['MAIL_DEFAULT_SENDER']

    app.config['SECURITY_POST_LOGIN_VIEW'] = "/"

    security = Security(app, CustomUserDatastore(), 
            login_form=CustomLoginForm,
            confirm_register_form=CustomRegisterForm)

    security.send_mail_task(send_security_mail)


class CustomUserDatastore(SQLAlchemyDatastore, UserDatastore):
    
    def __init__(self):
        SQLAlchemyDatastore.__init__(self, db)
        UserDatastore.__init__(self, User, None)

    def get_user(self, identifier):
        if isinstance(identifier, UUID):
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

class CustomLoginForm(LoginForm):

    email = StringField("Email or Login")

class CustomRegisterForm(RegisterForm):
    
    login = StringField('Login', validators=[Required(), Length(3, 32), 
            Regexp(r'^[a-z][a-z0-9_]*$', 0, 'Login must have only lowercase letters, numbers or underscores')])

    name = StringField('Name', validators=[Required(), Length(1, 64), 
            Regexp(r'^[A-Za-z0-9_\- ]+$', 0, 'Name must have only letters, numbers, spaces, dots, dashes or underscores')])

def send_security_mail(message):
    send(message=message)

def create_user(login):
    server_name = app.config["SERVER_NAME"] or "localhost"
    user = security.datastore.create_user(login=login, name=login.capitalize(), 
        email=login + "@" + server_name, password=encrypt_password(login),
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

