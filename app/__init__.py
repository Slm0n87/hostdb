from flask import Flask, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask.ext.login import LoginManager, current_user
from config import config
import flask.ext.restless


bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
rest_manager = flask.ext.restless.APIManager()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    rest_manager.init_app(app, flask_sqlalchemy_db=db)
 
    from app import models
    rest_manager.create_api(models.Host, methods=['GET'], results_per_page=None)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app



