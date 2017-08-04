from flask import render_template, redirect, url_for, flash
from . import dtc
#from .. import db
#from ..models import User
from .forms import DecisionTreeForm

@dtc.route('/addnew', methods=['GET', 'POST'])
def decision_tree_submit():
    form = DecisionTreeForm()
    if form.validate_on_submit():
        flash('Submitted successfully, calculation function under construction')
        return render_template('bdd/index.html')
    return render_template('dtc/index.html', form=form)