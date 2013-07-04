from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

app = Flask(__name__)

# initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# read config file
app.config.from_object('config')

# create db object
db = SQLAlchemy(app)

from app import views
from app import api
