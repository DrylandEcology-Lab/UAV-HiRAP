from flask import Blueprint

proj = Blueprint('proj', __name__)

from . import views