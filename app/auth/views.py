from flask import render_template, current_app, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ProfileEditForm

@auth.before_app_request
def before_requests():
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.endpoint \
        and request.endpoint[:5] != 'auth.' \
        and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('proj.index', username=current_user.username))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('proj.index', username=current_user.username))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.submit.data and form.validate_on_submit():
        user = User(ip= request.remote_addr,
                    email=form.email.data,
                    username=form.email.data.split('@')[0],
                    realname=form.realname.data,
                    password=form.password.data,
                    country=form.country.data,
                    org=form.org.data,
                    field=int(form.field.data),
                    major=form.major.data,
                    aim=form.aim.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your UAV-HiRAP Account', 'auth/email/confirm', user=user, token=token)
        flash('Registration successful! Please login.')
        app = current_app._get_current_object()
        send_email(app.config['MAIL_ADMIN'], '[' + user.username + '] Joined in', 'auth/email/userinfo', user=user)
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('proj.index', username=current_user.username))
    if current_user.confirm(token):
        flash('You have confirmed your account, thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your UAV-HiRAP Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to your by email. Please wait for a moment and check your INBOX or SAMP Box again')
    return redirect(url_for('proj.index', username=current_user.username))

@auth.route('/<username>/profile', methods=['GET','POST'])
@login_required
def my_profile(username):
    user = User.query.filter_by(username=username).first()
    form = ProfileEditForm()
    if form.cancel.data and form.is_submitted():
        return redirect(url_for('proj.index', username=current_user.username))
    if form.submit.data and form.validate_on_submit():
        user.realname = form.realname.data
        user.country = form.country.data
        user.org = form.org.data
        user.field = form.field.data
        user.major = form.major.data
        user.aim = form.aim.data
        if not user.edit_required:
            flash('Your profile has been updated!')
        if user.edit_required:
            flash('Your profile changes have been sent to administrator, he will check your profile soon')
            app = current_app._get_current_object()
            send_email(app.config['MAIL_ADMIN'], '[' + user.username + '] Changed profile', 'auth/email/userinfo', user=user)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('proj.index', username=current_user.username))
    form.realname.data = user.realname
    form.country.data =user.country
    form.org.data = user.org
    form.field.data = user.field
    form.major.data = user.major
    form.aim.data = user.aim
    return render_template('auth/profile.html', form=form, user=user)