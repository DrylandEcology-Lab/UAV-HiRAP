import os
import time
import hashlib
import PIL
import shutil
from PIL import Image
from flask import current_app, render_template, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from . import dtc
from .. import db, photos
from ..models import DTC_Project
from .forms import DecisionTreeForm, ProjectCalculateForm, ProjectEditForm
from .decisiontree import decision_tree_classifier


def create_project_folder(app, dtc_project):
    # create new folder
    user_dir = '/app/static/UserData/' + current_user.email + '/'
    full_dir = app.config['UPLOADED_PHOTOS_DEST'] + user_dir + str(dtc_project.id)
    if not os.path.exists(full_dir):
        os.makedirs(full_dir)
    else:
        shutil.rmtree(full_dir)
        os.makedirs(full_dir)
    return full_dir


def create_thumbnail(photopath, thumbnail_folder, thumbnail_name, base_width):
    img = Image.open(photopath)
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
    img.save(thumbnail_folder + '/' + thumbnail_name + '.png')
    return '/' + thumbnail_name + '.png'


def upload_pictures(prefix, saved_dir, previews, form_data, form_kind, thumbnail_size,
                    create_icon='off', pic_name_list=[], pic_kind_list=[]):
    icon_name = ''
    hash = '_' + hashlib.md5(str(time.time()).encode()).hexdigest()[:10]
    hash_name = prefix + hash + '.'
    filename = photos.save(form_data, folder=saved_dir, name=hash_name)
    pic_name_list.append(photos.path(filename))
    pic_kind_list.append(form_kind)
    previews[prefix] = create_thumbnail(photos.path(filename), saved_dir, 'pre_' + prefix + hash, thumbnail_size)
    if create_icon == 'on':
        icon_name = create_thumbnail(photos.path(filename), saved_dir, 'icon'+hash, 40)

    return pic_name_list, pic_kind_list, icon_name

def delete_old_train_pictures(dtc_project, kinds):
    pic_kind_list = eval(dtc_project.training_pic_kinds)
    pic_name_list = eval(dtc_project.training_pictures)
    i = pic_kind_list.index(kinds)
    rm = pic_name_list[i]
    if os.path.exists(rm):
        os.remove(rm)
    pic_kind_list.remove(pic_kind_list[i])
    pic_name_list.remove(pic_name_list[i])
    return pic_name_list, pic_kind_list

def delete_old_preview_pictures(path, preview_key):
    rm = path + preview_key
    if os.path.exists(rm):
        os.remove(rm)


@dtc.route('/<username>', methods=['GET', 'POST'])
@login_required
def decision_tree_submit(username):
    form = DecisionTreeForm()
    app = current_app._get_current_object()
    if form.validate_on_submit():
        # first commit to database to get id as folder name
        dtc_project = DTC_Project(project_name=form.project_name.data, comments=form.comments.data, author_id=current_user.id)
        db.session.add(dtc_project)
        db.session.commit()
        # refresh dtc_project from database
        dtc_project = DTC_Project.query.order_by(DTC_Project.id.desc()).first()
        print('in here')
        previews = {'classify':'', 'fore':'', 'back':'', 'result':''}

        # create project folders
        full_dir = create_project_folder(app, dtc_project)

        # uploads classify pictures
        classified_pictures_list, _, dtc_project.icon = upload_pictures(prefix='classify',
                                                      saved_dir=full_dir,
                                                      previews=previews,
                                                      form_data=form.origin_pic_dir.data,
                                                      form_kind='',
                                                      thumbnail_size=100,
                                                      create_icon='on', pic_name_list=[], pic_kind_list=[])
        # uploads fore training pictures
        training_pictures_list, training_pic_kinds_list, _ = upload_pictures(prefix='fore',
                                                                          saved_dir=full_dir,
                                                                          previews=previews,
                                                                          form_data=form.fore_trainingdata_dir.data,
                                                                          form_kind=0,
                                                                          thumbnail_size=100,
                                                                          pic_name_list=[],
                                                                          pic_kind_list=[])
        # uploads back training pictures
        training_pictures_list, training_pic_kinds_list, _ = upload_pictures(prefix='back',
                                                                          saved_dir=full_dir,
                                                                          previews=previews,
                                                                          form_data=form.back_trainingdata_dir.data,
                                                                          form_kind=1,
                                                                          thumbnail_size=100,
                                                                          pic_name_list=training_pictures_list,
                                                                          pic_kind_list=training_pic_kinds_list)
        # save to database
        dtc_project.previews=str(previews)
        dtc_project.project_dir=full_dir
        dtc_project.classified_pictures=str(classified_pictures_list)
        dtc_project.training_pictures=str(training_pictures_list)
        dtc_project.training_pic_kinds=str(training_pic_kinds_list)
        db.session.add(dtc_project)
        db.session.commit()
        flash('Pictures submitted successfully')
        return redirect(url_for('dtc.inproject', username=current_user.username, project_id=dtc_project.id))
    dtc_projects = DTC_Project.query.filter_by(author_id=current_user.id).order_by(DTC_Project.timestamp.desc()).all()
    return render_template('dtc/index.html', form=form, dtc_projects=dtc_projects, DTC_Project=DTC_Project)


@dtc.route('/<username>/<int:project_id>', methods=['GET', 'POST'])
@login_required
def inproject(username, project_id):
    form = ProjectCalculateForm()
    dtc_project = DTC_Project.query.get_or_404(project_id)
    previews = eval(dtc_project.previews)
    # back to list
    if form.back.data and form.is_submitted():
        return redirect(url_for('dtc.decision_tree_submit', username=current_user.username))
    # calculate pictures
    if form.submit_calculate.data and form.is_submitted():
        vfc = decision_tree_classifier(dtc_project.classified_pictures,
                                 dtc_project.training_pictures,
                                 dtc_project.training_pic_kinds,
                                 dtc_project.project_dir)
        # make result preview
        hash = '_' + hashlib.md5(str(time.time()).encode()).hexdigest()[:10]
        previews['result'] = create_thumbnail(dtc_project.project_dir + '/result.png',
                                              dtc_project.project_dir, 'pre_result'+hash, 100)
        dtc_project.previews = str(previews)
        dtc_project.vfc = str(vfc)
        db.session.add(dtc_project)
        db.session.commit()
        flash("Calculate finished")
        return redirect(url_for('dtc.inproject', username=current_user.username, project_id=dtc_project.id))
    # download result
    if form.download.data and form.is_submitted():
        return send_file(dtc_project.project_dir+'/result.png', as_attachment=True)
    # judge whether result.png exist
    if os.path.exists(dtc_project.project_dir+'/result.png'):
        exist = True
        try:
            vfc = eval(dtc_project.vfc)
            vfc_temp = vfc[0]
        except:
            vfc_temp = 'NaN'
    else:
        exist = False
        vfc_temp = 'NaN'

    return render_template('dtc/inproject.html', form=form, exist=exist, dtc_project=dtc_project, previews=previews, vfc_temp=vfc_temp)


@dtc.route('/<username>/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(username, project_id):
    dtc_project = DTC_Project.query.get_or_404(project_id)
    previews = eval(dtc_project.previews)
    form = ProjectEditForm()

    if form.cancel.data and form.is_submitted():
        return redirect(url_for('dtc.decision_tree_submit', username=current_user.username))

    if form.submit.data and form.validate_on_submit():
        # validate changes:
        # 1) Nothing changed % Just change project_name and comments => commit directly
        # 2) Change some pictures => delete old pictures, upload new pictures, refresh exist picture dir info
        full_dir = dtc_project.project_dir
        pic_change = False

        if form.origin_pic_dir.data:
            # delete old picture !! use delete_preview function
            rm = eval(dtc_project.classified_pictures)[0]
            if os.path.exists(rm):
                os.remove(rm)
            # delete old previews
            delete_old_preview_pictures(dtc_project.project_dir, dtc_project.icon)
            delete_old_preview_pictures(dtc_project.project_dir, previews['classify'])
            # upload new data
            classified_pictures_list, _, dtc_project.icon = upload_pictures(prefix='classify',
                                                          saved_dir=full_dir,
                                                          previews=previews,
                                                          form_data=form.origin_pic_dir.data,
                                                          form_kind='',
                                                          thumbnail_size=100,
                                                          create_icon='on', pic_name_list=[], pic_kind_list=[])
            # refresh database
            dtc_project.classified_pictures=str(classified_pictures_list)
            pic_change = True

        if form.fore_trainingdata_dir.data:
            # delete old pictures
            pic_name_list, pic_kind_list = delete_old_train_pictures(dtc_project, 0)
            delete_old_preview_pictures(dtc_project.project_dir, previews['fore'])
            # uploads
            training_pictures_list, training_pic_kinds_list, _ = upload_pictures(prefix='fore',
                                                                              saved_dir=full_dir,
                                                                              previews=previews,
                                                                              form_data=form.fore_trainingdata_dir.data,
                                                                              form_kind=0,
                                                                              thumbnail_size=100,
                                                                              pic_name_list=pic_name_list,
                                                                              pic_kind_list=pic_kind_list)
            # update database
            dtc_project.training_pictures=str(training_pictures_list)
            dtc_project.training_pic_kinds=str(training_pic_kinds_list)
            pic_change = True

        if form.back_trainingdata_dir.data:
            # delete old pictures
            pic_name_list, pic_kind_list = delete_old_train_pictures(dtc_project, 1)
            delete_old_preview_pictures(dtc_project.project_dir, previews['back'])
            # uploads
            training_pictures_list, training_pic_kinds_list, _ = upload_pictures(prefix='back',
                                                                              saved_dir=full_dir,
                                                                              previews=previews,
                                                                              form_data=form.back_trainingdata_dir.data,
                                                                              form_kind=1,
                                                                              thumbnail_size=100,
                                                                              pic_name_list=pic_name_list,
                                                                              pic_kind_list=pic_kind_list)
            # update database
            dtc_project.training_pictures=str(training_pictures_list)
            dtc_project.training_pic_kinds=str(training_pic_kinds_list)
            pic_change = True

        if pic_change:
            if os.path.exists(full_dir + '/result.png'):
                os.remove(full_dir + '/result.png')
                delete_old_preview_pictures(dtc_project.project_dir, previews['result'])

        dtc_project.previews = str(previews)
        dtc_project.project_name = form.project_name.data
        dtc_project.comments = form.comments.data
        db.session.add(dtc_project)
        flash('The project has been updated.')
        db.session.commit()
        return redirect(url_for('dtc.inproject', username=current_user.username, project_id=dtc_project.id))
    form.project_name.data = dtc_project.project_name
    form.comments.data = dtc_project.comments
    return render_template('dtc/edit_dtc_project.html', form=form, dtc_project=dtc_project, previews=previews)

@dtc.route('/<username>/<int:project_id>/delete', methods=['GET'])
@login_required
def delete(username, project_id):
    dtc_project = DTC_Project.query.get_or_404(project_id)
    rm = dtc_project.project_dir
    if os.path.exists(rm):
        shutil.rmtree(rm)
    db.session.delete(dtc_project)
    db.session.commit()
    return redirect(url_for('dtc.decision_tree_submit', username=current_user.username))