from flask import Blueprint

dtc = Blueprint('dtc', __name__)

from . import views