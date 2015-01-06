# -*- coding: utf-8 -*-

import atexit

from flask import Flask
from flask_mail import Mail
import flask_mail

import config

app = Flask(__name__)
app.config.from_object("config")

mail = Mail(app)

# import models

# import server.usermanagement

@app.route("/")
def index():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(config.HOST, config.PORT)
