import time

import flask
from flask_security.core import current_user
from flask_security.decorators import login_required

from puffin import app
from puffin.core import security
from puffin.core import applications
from puffin.core import docker
from puffin.core import backup
from puffin.core import stats
from . import forms


@app.context_processor
def utility_processor():
    return dict(current_user=current_user, version=app.config.get("VERSION"), 
            links=app.config.get("LINKS", []), 
            ApplicationStatus=applications.ApplicationStatus,
            stats=stats.get_stats())

@app.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html', applications=applications.get_application_list())

@app.route('/about.html', methods=['GET'])
def about():
    return flask.render_template('about.html')

@app.route('/profile.html', methods=['GET'])
@login_required
def my_profile():
    return flask.redirect(flask.url_for('profile', login=current_user.login))

@app.route('/profile/<login>.html', methods=['GET', 'POST'])
@login_required
def profile(login):
    if current_user.login != login:
        flask.abort(403, "You are not allowed to view this profile") 
    
    user = current_user
    
    form = forms.ProfileForm(obj=user)
    if form.validate_on_submit():
        user.name = form.name.data
        security.update_user(user)
        return flask.redirect(flask.url_for('profile', login=login))

    return flask.render_template('profile.html', user=current_user, form=form)

@app.route('/application/<application_id>.html', methods=['GET', 'POST'])
def application(application_id):
    client = docker.get_client()
    application = applications.get_application(application_id)
    application_status = None
    application_domain = None
    application_version = None
    application_image_version = docker.get_application_image_version(client, application)
    form = None

    if current_user.is_authenticated():

        form = forms.ApplicationForm()
        
        if form.validate_on_submit():
            if form.start.data:
                docker.create_application(client, current_user, application)
            
            if form.stop.data:
                docker.delete_application(client, current_user, application)
            return flask.redirect(flask.url_for('application', application_id=application_id))
        
        application_status = docker.get_application_status(client, current_user, application)
        application_domain = applications.get_application_domain(current_user, application)
        application_version = docker.get_application_version(client, current_user, application)

    return flask.render_template('application.html', application=application, 
        application_status=application_status, application_domain=application_domain, 
        application_version=application_version, application_image_version=application_image_version,
        form=form)

@app.route('/application/<application_id>.json', methods=['GET'])
@login_required
def application_status(application_id):
    client = docker.get_client()
    application = applications.get_application(application_id)
    status = docker.get_application_status(client, current_user, application).name
    return flask.jsonify(status=status)

@app.route('/applications', methods=['GET'], endpoint='applications')
@login_required
def apps():
    client = docker.get_client()
    app_statuses = docker.get_application_statuses(client, current_user)
    apps = [a[0] for a in app_statuses if a[1] == applications.ApplicationStatus.CREATED]
    return flask.render_template('applications.html', applications=apps)

@app.route('/media/<path:path>')
def media(path):
    if not path[-3:] in ("png", "jpg"):
        raise Exception("Unsupported media file format")
    return flask.send_from_directory(applications.APPLICATION_HOME, path)

@app.route('/application/<application_id>/settings.html', methods=['GET', 'POST'])
@login_required
def application_settings(application_id):
    user = current_user
    application = applications.get_application(application_id)
    
    application_settings = applications.get_application_settings(user.user_id, application_id)
    default_domain = applications.get_default_application_domain(user, application)

    backups = backup.list(user, application)

    form = forms.ApplicationSettingsForm()
    if form.validate_on_submit():

        if form.update.data:
            domain = form.domain.data.strip()
            if len(domain) != 0 and domain != default_domain:
                application_settings.settings["domain"] = domain
            else:
                application_settings.settings.pop("domain", None)
            https = form.https.data
            if https:
                application_settings.settings["https"] = True
            else:
                application_settings.settings.pop("https", None)
            applications.update_application_settings(application_settings)

        if form.backup.data:
            backup.backup(user, application)
            flask.flash("Backup created successfully.")

        if form.restore.data:
            backup.restore(user, application, form.restore.raw_data[0])
            flask.flash("Backup restored successfully.")

    form.domain.data = applications.get_application_domain(user, application)
    form.https.data = applications.get_application_https(user, application)

    return flask.render_template('application_settings.html', application=application, 
        application_settings=application_settings, backups=backups, form=form)
