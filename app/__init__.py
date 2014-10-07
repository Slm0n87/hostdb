from flask import Flask, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask.ext.login import LoginManager, current_user
import flask.ext.restless

app = Flask(__name__)
Bootstrap(app)
app.config.from_object('config')
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)


from app import views, models

from models import Host, User
manager.create_api(Host, methods=['GET'], results_per_page=None)

@login_manager.user_loader
def load_user(id):
        return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
