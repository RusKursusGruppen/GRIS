# -*- coding: utf-8 -*-

if __name__ == "__main__":
    print("""\
You probably want to run run.py instead:
    python run.py

Remember to activate the virtual environment first.
Please consult the README for details.""")
    import sys
    sys.exit()


from flask import Flask, send_file
from flask_mail import Mail

from lib.data import BucketDatabase
from lib.tools import AbortException, jsonify

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


@app.route("/", defaults={"path": ""})
# @app.route("/<path:path>")
def index(path):
    return send_file("static/html/index.html")


@app.errorhandler(AbortException)
def abort_handler(error):
    return jsonify(dict(code=error.code, message=error.description)), error.code

# for error_code in range(0, 1000):
    # app.error_handler_spec[None][error_code] = abort_handler
