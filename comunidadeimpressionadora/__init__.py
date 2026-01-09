from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = '\x97\xc4\xbd\xa0\xea#\xd4\x7f+)F\x1d\xaeh0\xfd\xfd\x07\x1c\xaaK9\x16\xb2'
if os.getenv("DATABASE_URL"):
  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
else:
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comunidade.db'

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'alert-info'

from comunidadeimpressionadora import routes

