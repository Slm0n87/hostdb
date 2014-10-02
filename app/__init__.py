from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import flask.ext.restless

app = Flask(__name__)
Bootstrap(app)
app.config.from_object('config')
db = SQLAlchemy(app)

manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)


from app import views, models

from models import Host
manager.create_api(Host, methods=['GET'])
