import os
import time
import hashlib
from flask import current_app, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from . import dtc
from .. import db, photos
from ..models import User, DTC_Project
from .forms import DecisionTreeForm


@dtc.route('/<username>/myprojects', methods=['GET', 'POST'])
@login_required
def decision_tree_submit(username):
    form = DecisionTreeForm()
    app = current_app._get_current_object()
    if form.validate_on_submit():
        # create project folders
        project_name = form.project_name.data
        user_dir = '/UserData/DTC/'+ current_user.email + '/'
        full_dir = app.config['UPLOADED_PHOTOS_DEST'] + user_dir + project_name
        print(full_dir)
        if not os.path.exists(full_dir):
            os.makedirs(full_dir)

        # create uploads pictures' dirs and names list for calculating
        classified_pictures_list = []
        training_pictures_list = []
        training_pic_kinds_list = []

        # uploads classify pictures
        classify_filename = photos.save(form.origin_pic_dir.data,
                                        folder=full_dir,
                                        name='classify_' + hashlib.md5(str(time.time()).encode()).hexdigest()[:10] + '.')
        time.sleep(0.1)
        classified_pictures_list.append(photos.path(classify_filename))
        # uploads fore training pictures
        fore_train_pic = photos.save(form.fore_trainingdata_dir.data,
                                     folder=full_dir,
                                     name='train_' + hashlib.md5(str(time.time()).encode()).hexdigest()[:10] + '.')
        time.sleep(0.1)
        training_pictures_list.append(photos.path(fore_train_pic))
        training_pic_kinds_list.append(0)
        #uploads back training pictures
        back_train_pic = photos.save(form.back_trainingdata_dir.data,
                                     folder=full_dir,
                                     name='train_' + hashlib.md5(str(time.time()).encode()).hexdigest()[:10] + '.')
        time.sleep(0.1)
        training_pictures_list.append(photos.path(back_train_pic))
        training_pic_kinds_list.append(1)

        # save to database
        dtc_project = DTC_Project(project_name=project_name,
                                  project_dir=full_dir,
                                  classified_pictures=str(classified_pictures_list),
                                  training_pictures=str(training_pictures_list),
                                  training_pic_kinds=str(training_pic_kinds_list))
        db.session.add(dtc_project)
        db.session.commit()
        flash('Pictures submitted successfully')
        return render_template('dtc/inproject.html')
    dtc_projects = DTC_Project.query.filter_by(author_id=current_user.id).\
                   order_by(DTC_Project.timestamp.desc()).all()
    return render_template('dtc/index.html', username=username, form=form, dtc_projects=dtc_projects)


@dtc.route('/<username>/<project_name>')
@login_required
def inproject(username, project_name):
    inproject = DTC_Project.query.filter_by(author_id=current_user.id).\
        filter_by(project_name=project_name).first_or_404()
    return render_template('dtc/inproject.html', inproject=inproject, username=username)