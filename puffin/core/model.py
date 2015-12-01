from ..util import truncate
from flask.ext.security import UserMixin


class User(UserMixin):
    
    def __init__(self, login, name, email, password, active, roles):
        self.login = login
        self.name = name
        self.email = email
        self.password = password
        self.active = active
    
    @property
    def id(self):
        return self.user_id

    @property
    def roles(self):
        return []

    @roles.setter
    def roles(self, role):
        pass


class App:
    
    def __init__(self, app_id, name, logo, description, image):
        self.app_id = app_id
        self.name = name
        self.logo = logo
        self.description = description
        self.image = image

    @property
    def short_description(self):
        return truncate(self.description, 90)

    @property
    def logo_url(self):
        return "/static/apps/" + self.app_id + "/" + self.logo


class Machine:
    
    def __init__(self, base_url, tls_config=None):
        self.base_url = base_url
        if tls_config:
            tls_config.assert_hostname = False
        self.tls_config = tls_config

