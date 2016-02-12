from ..util import truncate
from flask.ext.security import UserMixin
from enum import Enum
from datetime import datetime


class User(UserMixin):
    
    def __init__(self, login, name, email, password, active, roles, 
            confirmed=False):
        self.login = login
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        if confirmed:
            self.confirmed_at = datetime.now()
    
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

class SystemUser:
    
    def __init__(self, login):
        self.login = login

PUFFIN_USER = SystemUser("puffin")


class Application:
    
    def __init__(self, application_id, path, name, logo, subtitle, website, description, compose):
        self.application_id = application_id
        self.path = path
        self.name = name
        self.logo = logo
        self.subtitle = subtitle
        self.website = website
        self.description = description
        self.compose = compose

    @property
    def logo_url(self):
        return "/static/applications/" + self.application_id + "/" + self.logo


class ApplicationStatus(Enum):
    DELETED = 0
    CREATED = 10
    UPDATING = 20
    ERROR = 90


class Machine:
    
    def __init__(self, base_url, tls_config=None):
        self.base_url = base_url
        if tls_config:
            tls_config.assert_hostname = False
        self.tls_config = tls_config

