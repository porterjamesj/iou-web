from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from sqlalchemy import event

app = Flask(__name__)

# initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# read config file
app.config.from_object('config')


# create db object
db = SQLAlchemy(app)

#turn referential integrity on if configured
if app.config.get('REF_INTEGRITY'):

    @event.listens_for(db.engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


from app import views
from app import api
from app import extras
from app import errors
