from wtforms.validators import ValidationError
from flask_login import current_user

class UniqueProjectName(object):
    def __init__(self, model, field, message=u'Project name already exists, please use another name'):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        check = self.model.query.filter_by(author_id=current_user.id).filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)