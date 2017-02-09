from ..util import to_uuid
from ..core.security import User, update_user
from ..core.applications import ApplicationStatus, ApplicationSettings, APPLICATION_HOME, \
    get_application, get_application_list, get_application_settings, \
    update_application_settings, get_application_domain, get_default_application_domain
from ..core.docker import get_client, create_application, delete_application, \
    get_application_status, get_application_statuses, get_application_version, \
    get_application_image_version
from ..core.config import get_links
from ..core.stats import get_stats
from .. import app
from .form import ApplicationForm, ApplicationSettingsForm, ProfileForm

from flask import redirect, render_template, request, url_for, flash, abort, send_file, send_from_directory, jsonify
from flask_security.core import current_user
from flask_security.decorators import login_required
import time


@app.context_processor
def utility_processor():
    return dict(current_user=current_user, version=app.config.get("VERSION"), 
            links=app.config.get("LINKS", []), ApplicationStatus=ApplicationStatus,
        stats=get_stats())

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', applications=get_application_list())

@app.route('/about.html', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/profile.html', methods=['GET'])
@login_required
def my_profile():
    return redirect(url_for('profile', login=current_user.login))

@app.route('/profile/<login>.html', methods=['GET', 'POST'])
@login_required
def profile(login):
    if current_user.login != login:
        abort(403, "You are not allowed to view this profile") 
    
    user = current_user
    
    form = ProfileForm(obj=user)
    if form.validate_on_submit():
        user.name = form.name.data
        update_user(user)
        return redirect(url_for('profile', login=login))

    return render_template('profile.html', user=current_user, form=form)

@app.route('/application/<application_id>.html', methods=['GET', 'POST'])
def application(application_id):
    application_status = None
    application_domain = None
    application_version = None
    application_image_version = None
    form = None

    if current_user.is_authenticated():
        application = get_application(application_id)
        client = get_client()

        form = ApplicationForm()
        
        if form.validate_on_submit():
            if form.start.data:
                create_application(client, current_user, application)
            
            if form.stop.data:
                delete_application(client, current_user, application)
            return redirect(url_for('application', application_id=application_id))
        
        application_status = get_application_status(client, current_user, application)
        application_domain = get_application_domain(current_user, application)
        application_version = get_application_version(client, current_user, application)
        application_image_version = get_application_image_version(client, application)

    return render_template('application.html', application=get_application(application_id), 
        application_status=application_status, application_domain=application_domain, 
        application_version=application_version, application_image_version=application_image_version,
        form=form)

@app.route('/application/<application_id>.json', methods=['GET'])
@login_required
def application_status(application_id):
    client = get_client()
    application = get_application(application_id)
    client = get_client()
    status = get_application_status(client, current_user, application).name
    return jsonify(status=status)

@app.route('/applications', methods=['GET'])
@login_required
def applications():
    client = get_client()
    application_statuses = get_application_statuses(client, current_user)
    applications = [a[0] for a in application_statuses if a[1] == ApplicationStatus.CREATED]
    return render_template('applications.html', applications=applications)

@app.route('/media/<path:path>')
def media(path):
    if not path[-3:] in ("png", "jpg"):
        raise Exception("Unsupported media file format")
    return send_from_directory(APPLICATION_HOME, path)

@app.route('/application/<application_id>/settings.html', methods=['GET', 'POST'])
@login_required
def application_settings(application_id):
    user = current_user
    application = get_application(application_id)
    
    application_settings = get_application_settings(user.user_id, application_id)
    default_domain = get_default_application_domain(user, application)

    form = ApplicationSettingsForm()
    if form.validate_on_submit():
        domain = form.domain.data.strip()
        if len(domain) != 0 and domain != default_domain:
            application_settings.settings["domain"] = domain
        else:
            application_settings.settings.pop("domain", None)
        update_application_settings(application_settings)
        flash("Settings have been updated, but the changes will take effect once you restart the application")
        return redirect(url_for('application', application_id=application_id))

    form.domain.data = get_application_domain(user, application)

    return render_template('application_settings.html', application=application, 
        application_settings=application_settings, form=form)
