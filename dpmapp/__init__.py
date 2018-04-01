from flask_wtf.csrf import CSRFProtect
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# This code initializes CSRF and the SQLAlchemy DB
app = Flask(__name__, instance_relative_config=True)
csrf = CSRFProtect(app)
app.config.from_object('config')
app.config.from_pyfile('config.py')
app.config.update(dict(
    SECRET_KEY="so secret, much wow",
    WTF_CSRF_SECRET_KEY="blah blah blah"
))

db = SQLAlchemy(app)

import dpmapp.views