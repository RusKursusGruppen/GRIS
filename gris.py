# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random, subprocess

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, tools
from lib.tools import logged_in, now

from applications.schedule import schedule
from applications.rusmanager import rusmanager
from applications.usermanager import usermanager
from applications.front import front
from applications.admin import admin
from applications.bookkeeper import bookkeeper

app = Flask(__name__)
app.config.from_object("config")
app.register_blueprint(front)
app.register_blueprint(schedule)
app.register_blueprint(rusmanager)
app.register_blueprint(usermanager)
app.register_blueprint(admin)
app.register_blueprint(bookkeeper)

### ERROR HANDLER ###
@app.errorhandler(401)
@app.errorhandler(500)
def error(code):
    flash("Error {0}".format(code))
    return redirect(url_for('usermanager.login'))


def random_greeting():
    result = random.choice(
        [ "GRIS"
        , "Bacon"
        , "Velkommen"
        , "Nu med ekstra procenter!"
        , "made in Emacs"
        , "GTs inside"
        , "Der er <i>n</i> dage til rusturen"
        , "git push -f"
        , lambda:"8"+("="*random.randint(1,17))+"D"
        , lambda:("_-‾-"*random.randint(1,10))+"=:>"
        , ":(){ :|:& };:"
        , "public static void main(String[] args) {"
        , "Søren lavede denne side"
        , "Caro har også hjulpet"
        , "Formanden er dum!"
        , "Er du bange for tyngdekraften?"
        , "git@github.com:RusKursusGruppen/GRIS.git"
        , "Drevet af Flask, GT flask..."
        , "IT-Kalifen er en slacker!"
        , "Robert'); DROP TABLE Students;--"
        , "[]"
        , "<a href=\"http://en.wikipedia.org/wiki/Special:Random\">Learn more:</a>"
        , "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."
        , lambda : "Der er {0} russer i databasen".format(data.execute("SELECT ifnull(COUNT(r_id),0) FROM Russer")[0][0])
        , lambda: "<i>Latest commit message:</i> " + subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode('utf-8').rstrip('\n')
        , "Emacs, den objektivt bedste editor"
        , "O(n²)"
        , "λf.(λx.f (x x)) (λx.f (x x))"
        , "Kodet med knytnæver!"
        , "Søren har udviklet RKG-OS i skyen der kan ALT!"
        , "Søren snakker om kommunister og skinke!"
        , "Lund er nizzle i haven. NB og Munksgaard er nice og pooler"
        , "Nu gør RKG som vi plejer og kører en ligegyldig kommentar op til en laaaaang debat hvor alle skal sige det samme som de andre men blot med et lille twist (not)!"
        , "lalalalalala..."
        , "Vi har mange programmer til ølregnskab... alle er i BETA"
        , "3% kode, 79% slam"])

    if callable(result):
        return result()
    return result



### JINJA ###

from lib import filters

app.jinja_env.filters['nl2br'] = filters.nl2br
app.jinja_env.filters['markdown'] = filters.markdown
app.jinja_env.filters['money'] = filters.money
app.jinja_env.globals.update(url_front=tools.url_front)
app.jinja_env.globals.update(random_greeting=random_greeting)

if __name__ == '__main__':
    app.run()
