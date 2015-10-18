from flask.ext.security import UserMixin


class User(UserMixin):
    
    def __init__(self, name, email, password, active, roles):
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

