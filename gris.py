# -*- coding: utf-8 -*-

import atexit

from flask import Flask, Blueprint
from flask_mail import Mail
import flask_mail

from lib.data import BucketDatabase
import config

app = Flask(__name__)
app.config.from_object("config")

data = BucketDatabase(app)
mail = Mail(app)

from server.usermanager import blueprint as usermanager_blueprint
app.register_blueprint(usermanager_blueprint)


@app.route("/", defaults={"path":""})
@app.route("/<path:path>")
def index(path):
    print(app.url_map)
    return "Hello, World!"

if __name__ == "__main__":
    app.run(config.HOST, config.PORT)
