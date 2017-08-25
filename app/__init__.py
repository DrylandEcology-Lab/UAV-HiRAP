from flask import Flask, render_template, request, session
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel, gettext
from config import config
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
photos = UploadSet('photos', ['jpg', 'jpeg', 'png', 'tif', 'tiff'])   # create photos limit set

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

babel = Babel()

# multiple-language setting
# ++ main/views.py def set_language def inject conf var
# ++ def create_app()
@babel.localeselector
def get_locale():
    # if the user has set up the language manually it will be stored in the session,
    # so we use the locale from the user settings
    try:
        language = session['language']
    except KeyError:
        language = None
    if language is not None:
        return language
    return request.accept_languages.best_match((['zh', 'en']))

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # multiple-language setting 2
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)

    configure_uploads(app, photos)   # initialize upload photos
    patch_request_class(app, 1024 * 1024 * 1024) # maximize 1GB images

    # append route(LuYou) and error page
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .dtc import dtc as dtc_blueprint
    app.register_blueprint(dtc_blueprint, url_prefix='/myprojects')

    return app