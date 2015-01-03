# -*- coding: utf-8 -*-

import atexit

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import config

app = Flask(__name__)
app.config.from_object("config")
db = SQLAlchemy(app)

import models
@app.route("/")
def index():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(config.HOST, config.PORT)
