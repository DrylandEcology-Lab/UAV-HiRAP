from datetime import datetime
from flask import render_template, request, session, redirect, url_for, flash, current_app
from flask_babel import gettext
from .. import db
from ..email import send_email
from . import main
from .forms import NameForm
from .. import db
from ..models import User

@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@main.route('/developing', methods=['GET'])
def developing():
    return render_template('developing.html')

@main.route('/language/<language>')
def set_language(language=None):
    session['language'] = language
    return redirect(url_for('main.index'))

@main.route('/about_us')
def about_us():
    return render_template('about_us.html')

@main.route('/plot_pano')
def plot_pano():
    return render_template('plot_pano.html')

