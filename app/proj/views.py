import os
import copy
import time
import hashlib
import shutil
import matplotlib.pyplot as plt
from PIL import Image
from flask import current_app, render_template, redirect, url_for, flash, send_file, request
from flask_login import login_required, current_user
#from . import dtc
from . import proj
from .. import db, photos
from ..models import DTC_Project, RD_Project
from .forms import DecisionTreeForm, ProjectCalculateForm, ProjectEditForm, RouteDesignForm, EditRDProjectForm
from .decisiontree import decision_tree_classifier
from .route_design import route_design


#########################
####                 ####
#### User Guide Part ####
####                 ####
#########################
@proj.route('/<username>', methods=['GET', 'POST'])
@login_required
def index(username):
    return render_template('proj/guide.html')

#########################
###                   ###
### dtc projects Part ###
###                   ###
#########################
def create_project_folder(app, project, kind='dtc'):
    # create new folder
    #user_dir = '/app/static/UserData/' + current_user.email + '/'
    user_dir = '/app/static/UserData/' + kind + '/'
    full_dir = app.config['UPLOADED_PHOTOS_DEST'] + user_dir + str(project.id)
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
    img = img.resize((base_width, h_size), Image.ANTIALIAS)
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

##########################
# dtc project url direct #
##########################
@proj.route('/<username>/dtc', methods=['GET', 'POST'])
@login_required
def dtc(username):
    form = DecisionTreeForm()
    app = current_app._get_current_object()
    if form.validate_on_submit():
        # first commit to database to get id as folder name
        dtc_project = DTC_Project(project_name=form.project_name.data, comments=form.comments.data, author_id=current_user.id)
        db.session.add(dtc_project)
        db.session.commit()
        # refresh dtc_project from database
        dtc_project = DTC_Project.query.order_by(DTC_Project.id.desc()).first()
        previews = {'classify':'', 'fore':'', 'back':'', 'result':''}

        # create project folders
        dtc_full_dir = create_project_folder(app, dtc_project)

        # uploads classify pictures
        classified_pictures_list, _, dtc_project.icon = upload_pictures(prefix='classify',
                                                      saved_dir=dtc_full_dir,
                                                      previews=previews,
                                                      form_data=form.origin_pic_dir.data,
                                                      form_kind='',
                                                      thumbnail_size=200,
                                                      create_icon='on', pic_name_list=[], pic_kind_list=[])
        # uploads fore training pictures
        training_pictures_list, training_pic_kinds_list, _ = upload_pictures(prefix='fore',
                                                                          saved_dir=dtc_full_dir,
                                                                          previews=previews,
                                                                          form_data=form.fore_trainingdata_dir.data,
                                                                          form_kind=1,
                                                                          thumbnail_size=200,
                                                                          pic_name_list=[],
                                                                          pic_kind_list=[])
        # uploads back training pictures
        training_pictures_list, training_pic_kinds_list, _ = upload_pictures(prefix='back',
                                                                          saved_dir=dtc_full_dir,
                                                                          previews=previews,
                                                                          form_data=form.back_trainingdata_dir.data,
                                                                          form_kind=0,
                                                                          thumbnail_size=200,
                                                                          pic_name_list=training_pictures_list,
                                                                          pic_kind_list=training_pic_kinds_list)
        # save to database
        dtc_project.previews=str(previews)
        dtc_project.project_dir=dtc_full_dir
        dtc_project.classified_pictures=str(classified_pictures_list)
        dtc_project.training_pictures=str(training_pictures_list)
        dtc_project.training_pic_kinds=str(training_pic_kinds_list)
        db.session.add(dtc_project)
        db.session.commit()
        flash('Pictures submitted successfully')
        return redirect(url_for('proj.inproject_dtc', username=current_user.username, project_id=dtc_project.id))
    dtc_projects = DTC_Project.query.filter_by(author_id=current_user.id).order_by(DTC_Project.timestamp.desc()).all()
    return render_template('proj/dtc.html', form=form, dtc_projects=dtc_projects, DTC_Project=DTC_Project)


@proj.route('/<username>/dtc/<int:project_id>', methods=['GET', 'POST'])
@login_required
def inproject_dtc(username, project_id):
    form = ProjectCalculateForm()
    dtc_project = DTC_Project.query.get_or_404(project_id)
    previews = eval(dtc_project.previews)
    # calculate pictures
    if form.submit_calculate.data and form.is_submitted():
        # Delete old result preview
        try:
            delete_old_preview_pictures(dtc_project.project_dir, previews['result'])
        except:
            pass
        vfc = decision_tree_classifier(dtc_project.classified_pictures,
                                 dtc_project.training_pictures,
                                 dtc_project.training_pic_kinds,
                                 dtc_project.project_dir)
        # make result new preview
        hash = '_' + hashlib.md5(str(time.time()).encode()).hexdigest()[:10]
        previews['result'] = create_thumbnail(dtc_project.project_dir + '/result.png',
                                              dtc_project.project_dir, 'pre_result'+hash, 200)
        dtc_project.previews = str(previews)
        dtc_project.vfc = str(vfc)
        db.session.add(dtc_project)
        db.session.commit()
        flash("Calculate finished")
        return redirect(url_for('proj.inproject_dtc', username=current_user.username, project_id=dtc_project.id))
    # download result
    if form.download.data and form.is_submitted():
        return send_file(dtc_project.project_dir+'/result.png', as_attachment=True)
    # judge whether result.png exist
    if os.path.exists(dtc_project.project_dir+'/result.png'):
        exist = True
        try:
            vfc = eval(dtc_project.vfc)   # if user old data vfc empty, raise eval(not string) error
            vfc_temp = vfc[1]
        except:
            vfc_temp = 'NaN'
    else:
        exist = False
        vfc_temp = 'NaN'

    return render_template('proj/dtc_in_project.html', form=form, exist=exist, dtc_project=dtc_project, previews=previews, vfc_temp=vfc_temp)


@proj.route('/<username>/dtc/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_dtc(username, project_id):
    dtc_project = DTC_Project.query.get_or_404(project_id)
    previews = eval(dtc_project.previews)
    form = ProjectEditForm()

    if form.cancel.data and form.is_submitted():
        return redirect(url_for('proj.inproject_dtc', username=current_user.username, project_id=dtc_project.id))

    if form.submit.data and form.validate_on_submit():
        # validate changes:
        # 1) Nothing changed % Just change project_name and comments => commit directly
        # 2) Change some pictures => delete old pictures, upload new pictures, refresh exist picture dir info
        dtc_full_dir = dtc_project.project_dir
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
                                                          saved_dir=dtc_full_dir,
                                                          previews=previews,
                                                          form_data=form.origin_pic_dir.data,
                                                          form_kind='',
                                                          thumbnail_size=200,
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
                                                                              saved_dir=dtc_full_dir,
                                                                              previews=previews,
                                                                              form_data=form.fore_trainingdata_dir.data,
                                                                              form_kind=0,
                                                                              thumbnail_size=200,
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
                                                                              saved_dir=dtc_full_dir,
                                                                              previews=previews,
                                                                              form_data=form.back_trainingdata_dir.data,
                                                                              form_kind=1,
                                                                              thumbnail_size=200,
                                                                              pic_name_list=pic_name_list,
                                                                              pic_kind_list=pic_kind_list)
            # update database
            dtc_project.training_pictures=str(training_pictures_list)
            dtc_project.training_pic_kinds=str(training_pic_kinds_list)
            pic_change = True

        if pic_change:
            if os.path.exists(dtc_full_dir + '/result.png'):
                os.remove(dtc_full_dir + '/result.png')
                delete_old_preview_pictures(dtc_project.project_dir, previews['result'])

        dtc_project.previews = str(previews)
        dtc_project.project_name = form.project_name.data
        dtc_project.comments = form.comments.data
        db.session.add(dtc_project)
        flash('The project has been updated.')
        db.session.commit()
        return redirect(url_for('proj.inproject_dtc', username=current_user.username, project_id=dtc_project.id))
    form.project_name.data = dtc_project.project_name
    form.comments.data = dtc_project.comments
    return render_template('proj/dtc_edit_project.html', form=form, dtc_project=dtc_project, previews=previews)

@proj.route('/<username>/dtc/<int:project_id>/delete', methods=['GET'])
@login_required
def delete_dtc(username, project_id):
    dtc_project = DTC_Project.query.get_or_404(project_id)
    dtc_rm_dir = dtc_project.project_dir
    if isinstance(dtc_rm_dir, str) and os.path.exists(dtc_rm_dir):
        shutil.rmtree(dtc_rm_dir)
    db.session.delete(dtc_project)
    db.session.commit()
    return redirect(url_for('proj.dtc', username=current_user.username))


########################
###                  ###
### rd projects Part ###
###                  ###
########################
def make_route_figure(rd_project, litchi, preview_name='no_preview.png'):
    plt.style.use('seaborn-whitegrid')
    fig, axes = plt.subplots(nrows=1, ncols=1)
    fig.set_figheight(8)
    fig.set_figwidth(8)

    # boundary calculate
    litchi_xmin = litchi['longitude'].min()
    litchi_xmax = litchi['longitude'].max()
    litchi_ymin = litchi['latitude'].min()
    litchi_ymax = litchi['latitude'].max()

    xmin = min([rd_project.x1, rd_project.x2, rd_project.x3, rd_project.x4, litchi_xmin])
    xmax = max([rd_project.x1, rd_project.x2, rd_project.x3, rd_project.x4, litchi_xmax])
    x_div = (xmax - xmin) * 0.1

    ymin = min([rd_project.y1, rd_project.y2, rd_project.y3, rd_project.y4, litchi_ymin])
    ymax = max([rd_project.y1, rd_project.y2, rd_project.y3, rd_project.y4, litchi_ymax])
    y_div = (ymax - ymin) * 0.1

    # figure plot
    if type(litchi) != bool:
        axes.plot(litchi['longitude'], litchi['latitude'], color='orange', alpha=0.5)
        axes.scatter(litchi['longitude'], litchi['latitude'], color='orange')
    axes.scatter([rd_project.x1, rd_project.x2, rd_project.x3, rd_project.x4],
                 [rd_project.y1, rd_project.y2, rd_project.y3, rd_project.y4], color='blue')

    axes.plot([rd_project.x1, rd_project.x2, rd_project.x4, rd_project.x3, rd_project.x1],
              [rd_project.y1, rd_project.y2, rd_project.y4, rd_project.y3, rd_project.y1], color='blue', alpha=0.5)

    axes.text(rd_project.x1, rd_project.y1, 'A', fontsize=24)
    axes.text(rd_project.x2, rd_project.y2, 'B', fontsize=24)
    axes.text(rd_project.x3, rd_project.y3, 'C', fontsize=24)
    axes.text(rd_project.x4, rd_project.y4, 'D', fontsize=24)

    axes.get_xaxis().get_major_formatter().set_useOffset(False)
    axes.get_yaxis().get_major_formatter().set_useOffset(False)
    axes.set_xlim([xmin - x_div, xmax + x_div])
    axes.set_ylim([ymin - y_div, ymax + y_div])

    plt.xticks(rotation=45)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.tight_layout()
    if preview_name=='no_preview.png':
        plt.savefig(rd_project.project_dir + '/' + rd_project.route_picture_name)
    else:
        plt.savefig(rd_project.project_dir + '/' + preview_name)

def remove_old_file(rd_project, var_name):
    file_list = os.listdir(rd_project.project_dir)
    for file_name in file_list:
        if var_name in file_name:
            os.remove(os.path.join(rd_project.project_dir, file_name))

def calculate_route(rd_project):

    location = [[rd_project.x1, rd_project.y1],
                [rd_project.x2, rd_project.y2],
                [rd_project.x3, rd_project.y3],
                [rd_project.x4, rd_project.y4]]

    litchi = route_design(location, H=rd_project.h, time=rd_project.time,
                          long_fov=rd_project.long_fov, short_fov=rd_project.short_fov,
                          side_overlap=rd_project.side_overlap, head_overlap=rd_project.head_overlap)

    hash = '_' + hashlib.md5(str(time.time()).encode()).hexdigest()[:10]

    rd_project.csv_name = 'litchi_' + hash + '.csv'
    rd_project.route_picture_name = 'route_' + hash + '.png'

    return rd_project, litchi

#########################
# rd project url direct #
#########################
@proj.route('/<username>/rd', methods=['GET', 'POST'])
@login_required
def rd(username):
    form = RouteDesignForm()
    # These default value is set in route.html wtf.form(value="")
    #form.h.data = 30.0
    #form.long_fov.data = 61.9
    #form.short_fov.data = 46.4
    #form.side_overlap.data = 80.0
    #form.head_overlap.data = 85.0
    #form.time.data = 2.0
    app = current_app._get_current_object()
    if form.validate_on_submit():
        rd_project = RD_Project(project_name=form.project_name.data, comments=form.comments.data, author_id=current_user.id)
        db.session.add(rd_project)
        db.session.commit()
        # refresh dtc_project from database
        rd_project = RD_Project.query.order_by(RD_Project.id.desc()).first()

        # create project folders
        rd_full_dir = create_project_folder(app, rd_project, 'rd')

        # save to database
        rd_project.x1 = form.x1.data
        rd_project.y1 = form.y1.data
        rd_project.x2 = form.x2.data
        rd_project.y2 = form.y2.data
        rd_project.x3 = form.x3.data
        rd_project.y3 = form.y3.data
        rd_project.x4 = form.x4.data
        rd_project.y4 = form.y4.data

        rd_project.h= form.h.data
        rd_project.long_fov = form.long_fov.data
        rd_project.short_fov = form.short_fov.data
        rd_project.side_overlap = form.side_overlap.data
        rd_project.head_overlap = form.head_overlap.data
        rd_project.time = form.time.data

        hash = '_' + hashlib.md5(str(time.time()).encode()).hexdigest()[:10]

        rd_project.project_dir = rd_full_dir
        rd_project.route_picture_name = 'route' + hash + '.png'

        rd_project, litchi = calculate_route(rd_project)
        litchi.to_csv(rd_project.project_dir + '/' + rd_project.csv_name, index=False)
        make_route_figure(rd_project, litchi)

        db.session.add(rd_project)
        db.session.commit()
        return redirect(url_for('proj.inproject_rd', username=current_user.username, project_id=rd_project.id))

    rd_projects = RD_Project.query.filter_by(author_id=current_user.id).order_by(RD_Project.timestamp.desc()).all()
    return render_template('proj/rd.html', form=form, rd_projects=rd_projects, RD_Project=RD_Project)

@proj.route('/<username>/rd/<int:project_id>', methods=['GET', 'POST'])
@login_required
def inproject_rd(username, project_id):
    rd_project = RD_Project.query.get_or_404(project_id)
    return render_template('proj/rd_in_project.html', rd_project=rd_project)#, form=form)

@proj.route('/<username>/rd/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_rd(username, project_id):
    rd_project = RD_Project.query.get_or_404(project_id)
    form = EditRDProjectForm()
    if form.validate_on_submit():
        if form.preview.data:
            rd_project_pre = copy.deepcopy(rd_project)

            rd_project_pre.x1 = form.x1.data
            rd_project_pre.y1 = form.y1.data
            rd_project_pre.x2 = form.x2.data
            rd_project_pre.y2 = form.y2.data
            rd_project_pre.x3 = form.x3.data
            rd_project_pre.y3 = form.y3.data
            rd_project_pre.x4 = form.x4.data
            rd_project_pre.y4 = form.y4.data
            rd_project_pre.h = form.h.data
            rd_project_pre.long_fov = form.long_fov.data
            rd_project_pre.short_fov = form.short_fov.data
            rd_project_pre.side_overlap = form.side_overlap.data
            rd_project_pre.head_overlap = form.head_overlap.data
            rd_project_pre.time = form.time.data

            rd_project_pre, litchi = calculate_route(rd_project_pre)

            hash = '_' + hashlib.md5(str(time.time()).encode()).hexdigest()[:10]
            preview_name = 'preview' + hash + '.png'

            remove_old_file(rd_project, var_name='preview_')
            make_route_figure(rd_project_pre, litchi, preview_name=preview_name)

            form.project_name.data = rd_project_pre.project_name
            form.comments.data = rd_project_pre.comments
            form.x1.data = rd_project_pre.x1
            form.y1.data = rd_project_pre.y1
            form.x2.data = rd_project_pre.x2
            form.y2.data = rd_project_pre.y2
            form.x3.data = rd_project_pre.x3
            form.y3.data = rd_project_pre.y3
            form.x4.data = rd_project_pre.x4
            form.y4.data = rd_project_pre.y4
            form.h.data = rd_project_pre.h
            form.long_fov.data = rd_project_pre.long_fov
            form.short_fov.data = rd_project_pre.short_fov
            form.side_overlap.data = rd_project_pre.side_overlap
            form.head_overlap.data = rd_project_pre.head_overlap
            form.time.data = rd_project_pre.time

            return render_template('proj/rd_edit_project.html', form=form, rd_project=rd_project_pre,
                                   preview_img_name=preview_name)

        if form.change.data:
            rd_project.x1 = form.x1.data
            rd_project.y1 = form.y1.data
            rd_project.x2 = form.x2.data
            rd_project.y2 = form.y2.data
            rd_project.x3 = form.x3.data
            rd_project.y3 = form.y3.data
            rd_project.x4 = form.x4.data
            rd_project.y4 = form.y4.data

            rd_project.h = form.h.data
            rd_project.long_fov = form.long_fov.data
            rd_project.short_fov = form.short_fov.data
            rd_project.side_overlap = form.side_overlap.data
            rd_project.head_overlap = form.head_overlap.data
            rd_project.time = form.time.data

            rd_project, litchi = calculate_route(rd_project)

            remove_old_file(rd_project, var_name='route_')
            remove_old_file(rd_project, var_name='litchi_')

            litchi.to_csv(rd_project.project_dir + '/' + rd_project.csv_name, index=False)
            make_route_figure(rd_project, litchi)

            db.session.add(rd_project)
            db.session.commit()

            return redirect(url_for('proj.inproject_rd', username=current_user.username, project_id=rd_project.id))

    form.project_name.data = rd_project.project_name
    form.comments.data = rd_project.comments
    form.x1.data = rd_project.x1
    form.y1.data = rd_project.y1
    form.x2.data = rd_project.x2
    form.y2.data = rd_project.y2
    form.x3.data = rd_project.x3
    form.y3.data = rd_project.y3
    form.x4.data = rd_project.x4
    form.y4.data = rd_project.y4
    form.h.data = rd_project.h
    form.long_fov.data = rd_project.long_fov
    form.short_fov.data = rd_project.short_fov
    form.side_overlap.data = rd_project.side_overlap
    form.head_overlap.data = rd_project.head_overlap
    form.time.data = rd_project.time

    return render_template('proj/rd_edit_project.html', form=form, rd_project=rd_project, preview_img_name=rd_project.route_picture_name)

@proj.route('/<username>/rd/<int:project_id>/delete', methods=['GET'])
@login_required
def delete_rd(username, project_id):
    rd_project = RD_Project.query.get_or_404(project_id)
    rd_rm_dir = rd_project.project_dir
    if isinstance(rd_rm_dir, str) and os.path.exists(rd_rm_dir):
        shutil.rmtree(rd_rm_dir)
    db.session.delete(rd_project)
    db.session.commit()
    return redirect(url_for('proj.rd', username=current_user.username))

########################
###                  ###
### rd projects Part ###
###                  ###
########################
@proj.route('/<username>/seg', methods=['GET', 'POST'])
@login_required
def seg(username):
    return render_template('proj/seg.html')