# -*- coding: utf-8 -*-

import atexit

from flask import Flask, Blueprint, send_file, session
from flask_mail import Mail
import flask_mail

from lib.data import BucketDatabase
# from lib import data as data_module
from lib.tools import AbortException, jsonify

import config

app = Flask(__name__)
app.config.from_object("config")

data = BucketDatabase(app)
mail = Mail(app)

from server.usermanager import blueprint
app.register_blueprint(blueprint)

from server.news import blueprint
app.register_blueprint(blueprint)

from server.rustours import blueprint
app.register_blueprint(blueprint)

from server.mentorteams import blueprint
app.register_blueprint(blueprint)

from server.rusmanager import blueprint
app.register_blueprint(blueprint)


@app.route("/", defaults={"path":""})
# @app.route("/<path:path>")
def index(path):
    return send_file("static/html/index.html")

@app.route("/test", methods=["GET", "POST"])
def test():
    b = data.request()
    print(b)
    return "yay"

@app.errorhandler(AbortException)
def abort_handler(error):
    return jsonify(dict(code=error.code, message=error.description)), error.code

# for error_code in range(0, 1000):
    # app.error_handler_spec[None][error_code] = abort_handler
