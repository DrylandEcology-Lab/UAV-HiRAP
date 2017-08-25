# -*- coding:utf-8 -*-
import re
from flask_babel import gettext
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_login import login_required, current_user
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Length, DataRequired, Regexp
from ..models import DTC_Project
from .. import photos


class DecisionTreeForm(FlaskForm):
    project_name = StringField(gettext(u'Project Name'), validators=[DataRequired(),
                                                           Length(1,64),
                                                           # UniqueProjectName(DTC_Project,DTC_Project.project_name)
                                                           ])
    origin_pic_dir = FileField(gettext(u'Picture need to be classified (Maxsize = 1GB)'),
                               validators=[FileAllowed(photos, gettext(u'Images only')),
                                           FileRequired(gettext('File was empty'))])
    fore_trainingdata_dir = FileField(u'Foreground training picture',
                               validators=[FileAllowed(photos, gettext(u'Images only')),
                                           FileRequired(gettext(u'File was empty'))])
    back_trainingdata_dir = FileField('Background training picture',
                               validators=[FileAllowed(photos, gettext(u'Images only')),
                                           FileRequired(gettext(u'File was empty'))])
    comments = TextAreaField(u'Comments', validators=[DataRequired()])
    submit = SubmitField(u'Upload and Classify')


class ProjectCalculateForm(FlaskForm):
    back = SubmitField(gettext(u'Back'))
    download = SubmitField(gettext(u'Download result'))
    submit_calculate = SubmitField(gettext(u'Calculate'))


class ProjectEditForm(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired(),
                                                           Length(1,64)])
    origin_pic_dir = FileField('Change picture need to be classified (Maxsize = 1GB)',
                               validators=[FileAllowed(photos, 'Images only')])
    fore_trainingdata_dir = FileField('Change Foreground training picture',
                               validators=[FileAllowed(photos, 'Images only')])
    back_trainingdata_dir = FileField('Change Background training picture',
                               validators=[FileAllowed(photos, 'Images only')])
    comments = TextAreaField('Comments', validators=[DataRequired()])
    submit = SubmitField('Save changes')
    cancel = SubmitField('Cancel')