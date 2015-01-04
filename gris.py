# -*- coding: utf-8 -*-

import atexit

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_mail import Mail
import flask_mail

import config

app = Flask(__name__)
app.config.from_object("config")

db = SQLAlchemy(app)
mail = Mail(app)

# import models

# import lib.mail

import server.usermanagement

@app.route("/")
def index():
    server.usermanagement.invite(["fiskomaten@gmail.com", "vpb984@alumni.ku.dk"])
    return "Hello, World!"

if __name__ == "__main__":
    app.run(config.HOST, config.PORT)
