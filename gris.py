# -*- coding: utf-8 -*-

import sqlite3
import random
from functools import wraps
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from applications.schedule import schedule
from applications.rusmanager import rusmanager

from lib import data, password, tools
from lib.tools import logged_in

app = Flask(__name__)
app.config.from_object("config")
app.register_blueprint(schedule)
app.register_blueprint(rusmanager)

### ERROR HANDLER ###
@app.errorhandler(401)
def error(code):
    return redirect(url_for('login'))

### LOGIN/USERMANAGEMENT ###
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    print("start")
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']
        with data.data() as db:
            cur = db.execute('SELECT password, admin, rkg, tutor, mentor FROM Users WHERE username = ?', (username,))
            v = cur.fetchone()
            if empty(v) or not password.check(raw_password, v['password']):
                flash('Invalid username or password')
            else:
                session['logged_in'] = True
                session['username']  = username
                session['admin']     = v['admin'] == 1
                session['rkg']       = v['rkg']
                session['tutor']     = v['tutor']
                session['mentor']    = v['mentor']
                update_password(username, raw_password)
                flash("Login succesful")
                return redirect(session.pop('login_origin', url_for('front')))
    return render_template("login.html", error=error)

def create_user(username, raw_password, name="", admin=0):
    with data.data() as db:
        cur = db.cursor()
        passw = password.encode(raw_password)
        cur.execute("INSERT INTO Users(username, password, name, admin) VALUES(?,?,?,?)", (username, passw, name, admin))

def update_password(username, raw_password):
    with data.data() as db:
        cur = db.cursor()
        passwd = password.encode(raw_password)
        cur.execute("UPDATE Users SET password = ? WHERE username = ?", (passwd, username))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("Logout succesful")
    return redirect(url_for('front'))
    return redirect('http://rkg.diku.dk')

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




@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    print("start")
    if request.method == "POST":
        if 'cancel' in request.form:
            flash("Oprettelse anulleret")
            return redirect(url_for('front'))

        username = request.form['username']
        name = request.form['name']
        raw_password = request.form['password']
        admin = request.form['admin']
        create_user(username, raw_password, name, admin)
        flash("Ny bruger oprettet")
        return redirect(url_for('settings'))
    else:
        return render_template("new_user.html")


@app.route('/settings', methods=['GET', 'POST'])
@logged_in
def settings():
    return "bla"

@app.route('/admin', methods=['GET', 'POST'])
#adminrights
def admin():
    return render_template("admin.html")

app.jinja_env.globals.update(random_greeting=random_greeting)
app.jinja_env.globals.update(textfields=textfields)

if __name__ == '__main__':
    app.run()
