from flask.ext.wtf import Form
from wtforms import StringField, IntegerField, PasswordField, SubmitField, SelectField
from wtforms.validators import Required, Length, Regexp
from ..core.db import db
from ..core.model import User

class ApplicationForm(Form):
    install = SubmitField('Install')
    uninstall = SubmitField('Uninstall')

class ProfileForm(Form):
    login = StringField('Login')
    email = StringField('Email')

    name = StringField('Name', validators=[Required(), Length(1, 64), 
            Regexp(r'^[A-Za-z0-9_\- ]+$', 0, 'Name must have only letters, numbers, spaces, dots, dashes or underscores')])
    
    submit = SubmitField('Update')

