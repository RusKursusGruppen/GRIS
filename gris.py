# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import atexit

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

import applications
from lib import data, tools, greetings, mail, log
from lib.tools import logged_in, now, url_front

import config

from applications.schedule import schedule
from applications.rusmanager import rusmanager
from applications.usermanager import usermanager
from applications.front import front
from applications.admin import admin
from applications.bookkeeper import bookkeeper
from applications.rustours import rustours
from applications.mentorteams import mentorteams

### APPLICATION ###
app = Flask(__name__)
app.before_request(log.request)
app.config.from_object("config")
app.register_blueprint(front)
app.register_blueprint(schedule)
app.register_blueprint(rusmanager)
app.register_blueprint(usermanager)
app.register_blueprint(admin)
app.register_blueprint(bookkeeper)
app.register_blueprint(rustours)
app.register_blueprint(mentorteams)

### ERROR HANDLER ###
@app.errorhandler(500)
def error(code):
    log.log("An error occured on \"{0}\" reason: {1}".format(request.path, repr(code)), "ERROR 500")
    try:
        username = session['username']
    except:
        username = "NO USER"
    try:
        ip = flask.request.environ["REMOTE_ADDR"]
    except:
        ip = "UNKNOWN IP"

    text = mail.error_adminmail.format(username=username, time=now(), ip=ip, url = request.path, code=repr(code))
    mail.admin("ERROR", text, type="html", mail_admins=True)
    return (render_template("error/500.html"), 500)

@app.errorhandler(403)
def error403(code):
    log.log("Tried to access: {0}".format(request.path), "ERROR 403")
    if "username" in session:
        username = session['username']
        flash("You do not have sufficient rights to access this page.")
        return (render_template("error/403.html"), 403)
    else:
        flash("You do not have sufficient rights to access this page. Please log in.")
        return (applications.usermanager.login(), 403)

@app.errorhandler(404)
def error404(code):
    log.log("Tried to access: {0}".format(request.path), "ERROR 404")
    return (render_template("error/404.html"), 404)


### JINJA ###

from lib import filters

app.jinja_env.filters['nl2br'] = filters.nl2br
app.jinja_env.filters['markdown'] = filters.markdown
app.jinja_env.filters['money'] = filters.money
app.jinja_env.globals.update(url_front=tools.url_front)
app.jinja_env.globals.update(random_greeting=greetings.random_greeting)

### APPLICATION ###
@atexit.register
def goodbye():
    if config.MAIL_ON_EXIT:
        mail.admin("GRIS shutdown", "GRIS has exited at {0}\nThis could either be caused by an error or by a restart.".format(now()))

if __name__ == '__main__':
    app.run(config.HOST, config.PORT)
