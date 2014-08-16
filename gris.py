# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import atexit

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, tools, greetings, mail
from lib.tools import logged_in, now

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
@app.errorhandler(401)
@app.errorhandler(500)
def error(code):
    flash("Error {0}".format(code))
    return redirect(url_for('usermanager.login'))

@app.errorhandler(404)
def error404(code):
	return render_template("error/404.html")


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
    mail.admin("GRIS shutdown", "GRIS has exited at {0}".format(now()))

if __name__ == '__main__':
    app.run(config.HOST)
