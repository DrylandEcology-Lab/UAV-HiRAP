import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_login import login_required, current_user
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Length, DataRequired, Regexp
from ..models import DTC_Project
from .validators import UniqueProjectName
from .. import photos


class DecisionTreeForm(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired(),
                                                           Length(1,64),
                                                           # UniqueProjectName(DTC_Project,DTC_Project.project_name)
                                                           ])
    origin_pic_dir = FileField('Picture need to be classified (Maxsize = 1GB)',
                               validators=[FileAllowed(photos, 'Images only'),
                                           FileRequired('File was empty')])
    fore_trainingdata_dir = FileField('Foreground training picture',
                               validators=[FileAllowed(photos, 'Images only'),
                                           FileRequired('File was empty')])
    back_trainingdata_dir = FileField('Background training picture',
                               validators=[FileAllowed(photos, 'Images only'),
                                           FileRequired('File was empty')])
    comments = TextAreaField('Comments', validators=[DataRequired()])
    submit = SubmitField('Upload and Classify')


class ProjectCalculateForm(FlaskForm):
    back = SubmitField('Back')
    download = SubmitField('Download result')
    submit_calculate = SubmitField('Calculate')


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