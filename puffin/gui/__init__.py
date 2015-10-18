from flask import Blueprint

gui = Blueprint('gui', __name__)

from . import view

