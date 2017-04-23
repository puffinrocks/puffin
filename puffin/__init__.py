import flask
import flask_bootstrap

app = flask.Flask(__name__)

flask_bootstrap.Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

from . import gui


