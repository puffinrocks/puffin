from flask.ext.wtf import Form
from wtforms import StringField, IntegerField, PasswordField, SubmitField, SelectField
from wtforms.validators import Required, Length, Regexp
from ..core.db import db
from ..core.model import User
from ..core.config import get_server_name

class ApplicationForm(Form):
    start = SubmitField('Start')
    stop = SubmitField('Stop')

class ApplicationSettingsForm(Form):
    domain = StringField('Domain', description="If you change it then make sure you also configure it with your DNS provider")
    submit = SubmitField('Update')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.domain.data:
            server_name = get_server_name()
            if server_name != "localhost" and self.domain.data.endswith(server_name):
                self.domain.errors.append('Invalid domain, cannot end with ' + server_name)
                return False
        
        return True

class ProfileForm(Form):
    login = StringField('Login')
    email = StringField('Email')

    name = StringField('Name', validators=[Required(), Length(1, 64), 
            Regexp(r'^[A-Za-z0-9_\- ]+$', 0, 'Name must have only letters, numbers, spaces, dots, dashes or underscores')])
    
    submit = SubmitField('Update')

