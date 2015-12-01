import time
from flask import redirect, render_template, request, url_for, flash, abort, send_file, send_from_directory
from flask_bootstrap import Bootstrap
from flask_security.core import current_user
from flask_security.decorators import login_required
from ..util import to_uuid
from ..core.db import db
from ..core.model import User
from ..core.apps import APP_HOME, get_app, get_app_list
from ..core.docker import get_client, get_container, create_container, get_container_domain
from . import gui
from .form import UpdateAppForm


@gui.record_once
def record_once(state):
    app = state.app
    Bootstrap(app)
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True

@gui.context_processor
def utility_processor():
    return dict(current_user=current_user)

@gui.route('/', methods=['GET'])
def index():
    return render_template('index.html', apps=get_app_list())

@gui.route('/app/<app_id>.html', methods=['GET', 'POST'])
def app(app_id):
    container = None
    container_domain = None
    form = None

    if current_user.is_authenticated():
        client = get_client()

        form = UpdateAppForm()
        
        if form.validate_on_submit():
            install = form.install.data

            if install:
                app = get_app(app_id)
                create_container(client, current_user, app)
        container = get_container(client, current_user, app_id)
        container_domain = get_container_domain(current_user, app_id)

    return render_template('app.html', app=get_app(app_id), 
        container=container, container_domain=container_domain, form=form)

@gui.route('/static/apps/<path:path>')
def app_static(path):
    return send_from_directory(APP_HOME, path)

