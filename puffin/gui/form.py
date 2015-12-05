from flask.ext.wtf import Form
from wtforms import StringField, IntegerField, PasswordField, SubmitField, SelectField
from ..core.db import db
from ..core.model import User

class ApplicationForm(Form):
    install = SubmitField('Install')
    uninstall = SubmitField('Uninstall')
