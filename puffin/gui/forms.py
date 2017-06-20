import flask_wtf
from flask_security.core import current_user
import wtforms
from wtforms import validators

from puffin import app


class ApplicationForm(flask_wtf.Form):
    start = wtforms.SubmitField('Start')
    stop = wtforms.SubmitField('Stop')

class ApplicationSettingsForm(flask_wtf.Form):
    domain = wtforms.StringField('Domain', description="If you change it then make sure you also configure it with your DNS provider")
    https = wtforms.BooleanField('HTTPS', description="Enable HTTPS via Let's Encrypt")
    update = wtforms.SubmitField('Update')

    def validate(self):
        rv = flask_wtf.Form.validate(self)
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

class ApplicationBackupForm(flask_wtf.Form):
    name = wtforms.SelectField('Name')
    backup = wtforms.SubmitField('Backup')
    restore = wtforms.SubmitField('Restore')

class ProfileForm(flask_wtf.Form):
    login = wtforms.StringField('Login')
    email = wtforms.StringField('Email')

    name = wtforms.StringField('Name',
            validators=[
                validators.Required(),
                validators.Length(1, 64),
                validators.Regexp(r'^[A-Za-z0-9_\- ]+$', 0, 'Name must have only letters, numbers, spaces, dots, dashes or underscores')])

    submit = wtforms.SubmitField('Update')

