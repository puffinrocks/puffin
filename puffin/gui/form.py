from flask_wtf import Form
from flask_security.core import current_user
from wtforms import StringField, IntegerField, BooleanField, PasswordField, SubmitField, SelectField
from wtforms.validators import Required, Length, Regexp
from ..core.db import db
from ..core.security import User
from .. import app

class ApplicationForm(Form):
    start = SubmitField('Start')
    stop = SubmitField('Stop')

class ApplicationSettingsForm(Form):
    domain = StringField('Domain', description="If you change it then make sure you also configure it with your DNS provider")
    https = BooleanField('HTTPS', description="Enable HTTPS via Let's Encrypt")
    update = SubmitField('Update')
    backup = SubmitField('Backup')
    restore = SubmitField('Restore')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.domain.data:
            server_name = app.config["SERVER_NAME_FULL"]
            if (server_name != "localhost"
                    and not self.domain.data.endswith(current_user.login + "." + server_name)
                    and self.domain.data.endswith(server_name)):
                self.domain.errors.append('Invalid domain, cannot end with ' + server_name)
                return False
        
        return True

class ProfileForm(Form):
    login = StringField('Login')
    email = StringField('Email')

    name = StringField('Name', validators=[Required(), Length(1, 64), 
            Regexp(r'^[A-Za-z0-9_\- ]+$', 0, 'Name must have only letters, numbers, spaces, dots, dashes or underscores')])
    
    submit = SubmitField('Update')

