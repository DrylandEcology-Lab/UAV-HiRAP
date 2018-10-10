# -*- coding:utf-8 -*-
import re
from flask_babel import gettext
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_login import login_required, current_user
from wtforms import StringField, SubmitField, TextAreaField, FloatField
from wtforms.validators import Length, DataRequired, Regexp, NumberRange
from ..models import DTC_Project, RD_Project
from .. import photos


# DTC project forms
class DecisionTreeForm(FlaskForm):
    project_name = StringField(gettext(u'Project Name'), validators=[DataRequired(),Length(1,64)])
    origin_pic_dir = FileField(gettext(u'Image to classify'),
                               validators=[FileAllowed(photos, gettext(u'Images only')),
                                           FileRequired(gettext('File was empty'))])
    fore_trainingdata_dir = FileField(u'Foreground training image',
                               validators=[FileAllowed(photos, gettext(u'Images only')),
                                           FileRequired(gettext(u'File was empty'))])
    back_trainingdata_dir = FileField('Background training image',
                               validators=[FileAllowed(photos, gettext(u'Images only')),
                                           FileRequired(gettext(u'File was empty'))])
    comments = TextAreaField(u'Comments', validators=[DataRequired(),Length(1,128)])
    submit = SubmitField(u'Upload and Classify')


class ProjectCalculateForm(FlaskForm):
    download = SubmitField(gettext(u'Save'))
    submit_calculate = SubmitField(gettext(u'Calculate'))


class ProjectEditForm(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired(),
                                                           Length(1,64)])
    origin_pic_dir = FileField('Change classify image',
                               validators=[FileAllowed(photos, 'Images only')])
    fore_trainingdata_dir = FileField('Change Foreground training-img',
                               validators=[FileAllowed(photos, 'Images only')])
    back_trainingdata_dir = FileField('Change Background training-img',
                               validators=[FileAllowed(photos, 'Images only')])
    comments = TextAreaField(label="",validators=[DataRequired(),Length(1,128)])
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')

# Route Design forms
class RouteDesignForm(FlaskForm):
    project_name = StringField(gettext(u'Project Name'), validators=[DataRequired(), Length(1, 64)])
    x1 = FloatField(gettext(u'Longitude A (经度°)'), validators=[DataRequired(), NumberRange(min=-180.0, max=180.0)])
    y1 = FloatField(gettext(u'Latitude A (纬度°)'), validators=[DataRequired(), NumberRange(min=-90.0, max=90.0)])
    x2 = FloatField(gettext(u'Longitude B (经度°)'), validators=[DataRequired(), NumberRange(min=-180.0, max=180.0)])
    y2 = FloatField(gettext(u'Latitude B (纬度°)'), validators=[DataRequired(), NumberRange(min=-90.0, max=90.0)])
    x3 = FloatField(gettext(u'Longitude C (经度°)'), validators=[DataRequired(), NumberRange(min=-180.0, max=180.0)])
    y3 = FloatField(gettext(u'Latitude C (纬度°)'), validators=[DataRequired(), NumberRange(min=-90.0, max=90.0)])
    x4 = FloatField(gettext(u'Longitude D (经度°)'), validators=[DataRequired(), NumberRange(min=-180.0, max=180.0)])
    y4 = FloatField(gettext(u'Latitude D (纬度°)'), validators=[DataRequired(), NumberRange(min=-90.0, max=90.0)])
    h = FloatField(gettext(u'Height(m)'), validators=[DataRequired(), NumberRange(min=1.0, max=1000.0)])
    long_fov = FloatField(gettext(u'Long field of view (长边视场角°)'), validators=[DataRequired(), NumberRange(min=20.0, max=90.0)])
    short_fov = FloatField(gettext(u'Short field of view (短边视场角°)'), validators=[DataRequired(), NumberRange(min=20.0, max=90.0)])
    side_overlap = FloatField(gettext(u'Side overlap rate (旁向重叠率%)'), validators=[DataRequired(), NumberRange(min=10.0, max=99.0)])
    head_overlap = FloatField(gettext(u'Head overlap rate (航向重叠率%)'), validators=[DataRequired(), NumberRange(min=10.0, max=99.0)])
    time = FloatField(gettext(u'Photo Interval (拍照间隔s)'), validators=[DataRequired(), NumberRange(min=0.1, max=100.0)])
    comments = TextAreaField(u'Comments (备注)', validators=[DataRequired(), Length(1, 128)])
    submit = SubmitField(u'Create')

class EditRDProjectForm(FlaskForm):
    project_name = StringField(gettext(u'Project Name'), validators=[DataRequired(), Length(1, 64)])
    x1 = FloatField(gettext(u'Longitude A (经度°)'), validators=[DataRequired(), NumberRange(min=-180.0, max=180.0)])
    y1 = FloatField(gettext(u'Latitude A (纬度°)'), validators=[DataRequired(), NumberRange(min=-90.0, max=90.0)])
    x2 = FloatField(gettext(u'Longitude B (经度°)'), validators=[DataRequired(), NumberRange(min=-180.0, max=180.0)])
    y2 = FloatField(gettext(u'Latitude B (纬度°)'), validators=[DataRequired(), NumberRange(min=-90.0, max=90.0)])
    x3 = FloatField(gettext(u'Longitude C (经度°)'), validators=[DataRequired(), NumberRange(min=-180.0, max=180.0)])
    y3 = FloatField(gettext(u'Latitude C (纬度°)'), validators=[DataRequired(), NumberRange(min=-90.0, max=90.0)])
    x4 = FloatField(gettext(u'Longitude D (经度°)'), validators=[DataRequired(), NumberRange(min=-180.0, max=180.0)])
    y4 = FloatField(gettext(u'Latitude D (纬度°)'), validators=[DataRequired(), NumberRange(min=-90.0, max=90.0)])
    h = FloatField(gettext(u'Height(m)'), validators=[DataRequired(), NumberRange(min=1.0, max=1000.0)])
    long_fov = FloatField(gettext(u'Long field of view (长边视场角°)'),
                          validators=[DataRequired(), NumberRange(min=20.0, max=90.0)])
    short_fov = FloatField(gettext(u'Short field of view (短边视场角°)'),
                           validators=[DataRequired(), NumberRange(min=20.0, max=90.0)])
    side_overlap = FloatField(gettext(u'Side overlap rate (旁向重叠率%)'),
                              validators=[DataRequired(), NumberRange(min=10.0, max=99.0)])
    head_overlap = FloatField(gettext(u'Head overlap rate (航向重叠率%)'),
                              validators=[DataRequired(), NumberRange(min=10.0, max=99.0)])
    time = FloatField(gettext(u'Photo Interval (拍照间隔s)'), validators=[DataRequired(), NumberRange(min=0.1, max=100.0)])
    comments = TextAreaField(u'Comments (备注)', validators=[DataRequired(), Length(1, 128)])
    preview = SubmitField(u'Preview')
    change = SubmitField(u'Change')