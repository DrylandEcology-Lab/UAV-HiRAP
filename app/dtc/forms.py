import re
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

class DecisionTreeForm(FlaskForm):
    projectname = StringField('Project Name', validators=[DataRequired(), 
                                                          Length(1,64)])
    origin_pic_dir = FileField('Picture need to be classified', 
                               validators=[DataRequired()])
    fore_trainingdata_dir = FileField('Foreground training picture', 
                               validators=[DataRequired()])
    back_trainingdata_dir = FileField('Background training picture', 
                               validators=[DataRequired()])
    submit = SubmitField('Upload and Classify')
    
    def validate_image(form, field):
        if field.data:
            field.data = re.sub(r'[^a-z0-9_.-]', '_', field.data)