import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from flask import current_app
from . import login_manager
from . import db


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15))
    password_hash = db.Column(db.String(128))

    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    realname = db.Column(db.String(64))
    country = db.Column(db.String(64))
    org = db.Column(db.String(128))
    field = db.Column(db.Integer)
    major = db.Column(db.String(64))
    aim = db.Column(db.Text)

    confirmed = db.Column(db.Boolean, default=False)
    edit_required = db.Column(db.Boolean, default=False)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    dtc_projects = db.relationship('DTC_Project', backref='dtc_author', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True


    def __repr__(self):
        return '<Users %r>' % self.email



class DTC_Project(db.Model):
    __tablename__ = 'dtc_projects'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_name = db.Column(db.Text, index=True)
    comments = db.Column(db.Text)
    project_dir = db.Column(db.Text)
    classified_pictures = db.Column(db.Text)
    training_pictures = db.Column(db.Text)
    training_pic_kinds = db.Column(db.Text)
    previews = db.Column(db.Text)
    icon = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    vfc = db.Column(db.Text)   # vfc = {'0':0.236; '1':0.546; '2':0.345}

    def __repr__(self):
        return '<%r DTC_Project project_name%r\nclassified_pictures%r \ntraining_pictures%r \ntraining_kinds%r> \n\n' \
               % (self.id, self.project_name, self.classified_pictures, self.training_pictures, self.training_pic_kinds)

    @staticmethod
    def admin_remove_all_result():
        # in old version, foreground=0(black), background=1(white)
        # this is not suitable for common classification result show
        for i in DTC_Project.query.all():
            result_dir = i.project_dir + '/result.png'
            if os.path.exists(result_dir):
                os.remove(result_dir)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
