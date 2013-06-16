# -*- coding: utf-8 -*-

import sqlite3
import random
from functools import wraps
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from applications.schedule import schedule
from applications.rusmanager import rusmanager
from applications.usermanager import usermanager

from lib import data, password, tools
from lib.tools import logged_in

app = Flask(__name__)
app.config.from_object("config")
app.register_blueprint(schedule)
app.register_blueprint(rusmanager)
app.register_blueprint(usermanager)

### ERROR HANDLER ###
@app.errorhandler(401)
def error(code):
    return redirect(url_for('usermanager.login'))

textfields = [ 'name',
               'filled_by',
               'co',
               'address',
               'zipcode',
               'city',
               'move_time',
               'new_address',
               'new_zipcode',
               'new_city',
               'phone',
               'email',
               'vacation',
               'priority',
               'gymnasium',
               'since_gymnasium',
               'code_experience',
               'special_needs',
               'plays_instrument',
               'other',]

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



### PAGES ###

@app.route('/')
@logged_in
def front():
    rkg      = session['rkg']
    vejleder = session['tutor']
    mentor   = session['mentor']
    news = data.execute("SELECT * FROM News ORDER BY created DESC")# WHERE for_tutors = ? OR for_mentors = ?", tutor, mentor)
    return render_template("front.html", news=news)

@app.route('/add_news', methods=['GET', 'POST'])
@logged_in
def add_news():
    if request.method == 'POST':
        creator = session['username']
        created = now()
        title = request.form['title']
        text = request.form['text']
        data.execute("INSERT INTO News(creator, created, title, text) VALUES(?,?,?,?)", creator, created, title, text)
        return redirect(url_for('front'))
    else:
        return render_template('add_news.html')





@app.route('/admin', methods=['GET', 'POST'])
#adminrights
def admin():
    return render_template("admin.html")

app.jinja_env.globals.update(random_greeting=random_greeting)
app.jinja_env.globals.update(textfields=textfields)

if __name__ == '__main__':
    app.run()
