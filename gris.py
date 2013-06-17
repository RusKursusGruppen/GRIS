# -*- coding: utf-8 -*-

import sqlite3
import random
from functools import wraps
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from applications.schedule import schedule
from applications.rusmanager import rusmanager
from applications.usermanager import usermanager
from applications.rusmanager import textfields
from applications.front import front
from applications.admin import admin

from lib import data, password, tools
from lib.tools import logged_in, now

app = Flask(__name__)
app.config.from_object("config")
app.register_blueprint(front)
app.register_blueprint(schedule)
app.register_blueprint(rusmanager)
app.register_blueprint(usermanager)
app.register_blueprint(admin)

### ERROR HANDLER ###
@app.errorhandler(401)
def error(code):
    return redirect(url_for('usermanager.login'))


def random_greeting():
    with data.data() as db:
        cur = db.execute("SELECT COUNT(rid) FROM Russer")
        count = cur.fetchone()[0]

    return random.choice(
        [ "GRIS"
        , "Bacon"
        , "Velkommen"
        , "Nu med ekstra procenter!"
        , "made in Emacs"
        , "GTs inside"
        , "Der er <i>n</i> dage til rusturen"
        , "git push -f"
        , "8"+("="*random.randint(1,17))+"D"
        , (u"_-‾-"*random.randint(1,10))+"=:>"
        , ":(){ :|:& };:"
        , "public static void main(String[] args) {"
        , u"Søren lavede denne side"
        , u"Caro har også hjulpet"
        , "Formanden er dum!"
        , "Er du bange for tyngdekraften?"
        , "Robert'); DROP TABLE Students;--"
        , "[]"
        , "<a href=\"http://en.wikipedia.org/wiki/Special:Random\">Learn more:</a>"
        , "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."
        , "Der er {0} russer i databasen".format(count)
        , "Emacs, den objektivt bedste editor"
        , u"O(n²)"
        , u"λf.(λx.f (x x)) (λx.f (x x))"
        , u"Kodet med knytnæver!"
        , "3% kode, 79% slam"])



### JINJA ###

from lib import jinja

app.jinja_env.filters['nl2br'] = jinja.nl2br
app.jinja_env.globals.update(url_front=tools.url_front)
app.jinja_env.globals.update(random_greeting=random_greeting)
app.jinja_env.globals.update(textfields=textfields)

if __name__ == '__main__':
    app.run()
