from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, current_app
from .. import db
from ..email import send_email
from . import main
from .forms import NameForm
from .. import db
from ..models import User

@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')