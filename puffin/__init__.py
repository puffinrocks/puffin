from flask_bootstrap import Bootstrap
from flask import Flask

app = Flask(__name__)

Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

from . import gui


