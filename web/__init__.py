import os

from flask import Flask, render_template, _app_ctx_stack
from sqlalchemy.orm import scoped_session
from database.engine import SessionLocal, SQLALCHEMY_DATABASE_URL
from database.models import RatingStep, RatingStepType, RatingStepParameter, RatingManual
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app import Rating
from repo import RatingManualRepository


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, instance_path=os.path.abspath(os.path.dirname(__file__)))
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=SQLALCHEMY_DATABASE_URL,
    )
    app.session = scoped_session(SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    admin = Admin(app, name='Flask Rater Admin', template_mode='bootstrap3')
    admin.add_view(ModelView(RatingManual, app.session))
    admin.add_view(ModelView(RatingStep, app.session))
    admin.add_view(ModelView(RatingStepType, app.session))
    admin.add_view(ModelView(RatingStepParameter, app.session))

    # a simple page that says hello
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # @app.route('/rate')
    # def rate():
    #     Rating.rate(rating_manual_id=1, rating_manual_repository=RatingManualRepository, rating_inputs=POSTDATA)
    #     # return JSONify([rate: rate])

    return app
