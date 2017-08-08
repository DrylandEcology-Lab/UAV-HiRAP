import os
import time
import hashlib
import PIL
import shutil
from PIL import Image
from flask import current_app, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import dtc
from .. import db, photos
from ..models import User, DTC_Project
from .forms import DecisionTreeForm


def create_thumbnail(photopath, thumbnail_folder, thumbnail_name, base_width=40):
    img = Image.open(photopath)
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
    img.save(thumbnail_folder + '/' + thumbnail_name + 'jpg')


@dtc.route('/<username>/myprojects', methods=['GET', 'POST'])
@login_required
def decision_tree_submit(username):
    form = DecisionTreeForm()
    app = current_app._get_current_object()
    if form.validate_on_submit():
        # create project folders
        project_name = form.project_name.data
        user_dir = '/app/static/UserData/DTC/'+ current_user.email + '/'
        full_dir = app.config['UPLOADED_PHOTOS_DEST'] + user_dir + project_name
        if not os.path.exists(full_dir):
            os.makedirs(full_dir)
        else:
            shutil.rmtree(full_dir)
            os.mkdir(full_dir)

        # create uploads pictures' dirs and names list for calculating
        classified_pictures_list = []
        training_pictures_list = []
        training_pic_kinds_list = []

        # uploads classify pictures
        classify_hash = 'classify_' + hashlib.md5(str(time.time()).encode()).hexdigest()[:10] + '.'
        classify_filename = photos.save(form.origin_pic_dir.data,
                                        folder=full_dir,
                                        name=classify_hash)
        classified_pictures_list.append(photos.path(classify_filename))
        create_thumbnail(photos.path(classify_filename), full_dir, 'preview.')
        create_thumbnail(photos.path(classify_filename), full_dir, 'preview200.', 200)
        # uploads fore training pictures
        fore_train_hash = 'train_' + hashlib.md5(str(time.time()).encode()).hexdigest()[:10] + '.'
        fore_train_pic = photos.save(form.fore_trainingdata_dir.data,
                                     folder=full_dir,
                                     name=fore_train_hash)
        training_pictures_list.append(photos.path(fore_train_pic))
        training_pic_kinds_list.append(0)
        create_thumbnail(photos.path(fore_train_pic), full_dir, 'preview_fore.', 200)

        #uploads back training pictures
        back_train_hash = 'train_' + hashlib.md5(str(time.time()).encode()).hexdigest()[:10] + '.'
        back_train_pic = photos.save(form.back_trainingdata_dir.data,
                                     folder=full_dir,
                                     name=back_train_hash)
        training_pictures_list.append(photos.path(back_train_pic))
        training_pic_kinds_list.append(1)
        create_thumbnail(photos.path(back_train_pic), full_dir, 'preview_back.', 200)

        # save to database
        dtc_project = DTC_Project(project_name=project_name,
                                  project_dir=full_dir,
                                  classified_pictures=str(classified_pictures_list),
                                  training_pictures=str(training_pictures_list),
                                  training_pic_kinds=str(training_pic_kinds_list),
                                  comments=form.comments.data,
                                  author_id=current_user.id)
        db.session.add(dtc_project)
        db.session.commit()
        flash('Pictures submitted successfully')
        return redirect(url_for('dtc.inproject', username=current_user.username, project_name=project_name))
    dtc_projects = DTC_Project.query.filter_by(author_id=current_user.id).\
                   order_by(DTC_Project.timestamp.desc()).all()
    return render_template('dtc/index.html', username=current_user.username, form=form, dtc_projects=dtc_projects)


@dtc.route('/<username>/<project_name>', methods=['GET','POST'])
@login_required
def inproject(username, project_name):

    inproject = DTC_Project.query.filter_by(author_id=current_user.id).\
        filter_by(project_name=project_name).first_or_404()
    return render_template('dtc/inproject.html', inproject=inproject, username=current_user.username)