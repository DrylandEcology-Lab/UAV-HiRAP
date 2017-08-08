import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_login import login_required, current_user
from wtforms import StringField, SubmitField, TextAreaField
from wtforms import ValidationError
from wtforms.validators import Length, DataRequired
from ..models import DTC_Project
from .. import photos


class DecisionTreeForm(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired(),
                                                          Length(1,64)])
    origin_pic_dir = FileField('Picture need to be classified (Maxsize = 1GB)',
                               validators=[FileAllowed(photos, 'Images only'),
                                           FileRequired('File was empty')])
    fore_trainingdata_dir = FileField('Foreground training picture (with alpha layer, Maxsize=1GB)',
                               validators=[FileAllowed(photos, 'Images only'),
                                           FileRequired('File was empty')])
    back_trainingdata_dir = FileField('Background training picture (with alpha layer, Maxsize=1GB)',
                               validators=[FileAllowed(photos, 'Images only'),
                                           FileRequired('File was empty')])
    comments = TextAreaField('Comments', validators=[DataRequired()])
    submit = SubmitField('Upload and Classify')

    def validate_project_name(self, field):
        if DTC_Project.query.filter_by(author_id=current_user.id).\
                filter_by(project_name=field.data).first():
            raise ValidationError('Project name already exists, please use another name')