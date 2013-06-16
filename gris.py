# -*- coding: utf-8 -*-

import sqlite3
import random
from functools import wraps
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape

import data
import password
import datetime

app = Flask(__name__)
app.config.from_object("config")

### TOOLS ###
def empty(lst):
    return lst == None or len(lst) == 0

def logged_in(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        if not session.get('logged_in'):
            session['login_origin'] = request.path
            abort(401)
        else:
            return fn(*args, **kwargs)
    return decorator

@app.errorhandler(401)
def error(code):
    return redirect(url_for('login'))

def now():
    return str(datetime.datetime.now())

def string_to_time(str):
    format = "%Y-%m-%d %H:%M:%S.%f"
    return datetime.datetime.strptime(str, format)


### LOGIN/USERMANAGEMENT ###
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    print("start")
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']
        with data.data() as db:
            cur = db.execute('SELECT password, admin, tutor, mentor FROM Users WHERE username = ?', (username,))
            v = cur.fetchone()
            if empty(v) or not password.check(raw_password, v['password']):
                flash('Invalid username or password')
            else:
                session['logged_in'] = True
                session['admin']     = v['admin'] == 1
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
        , "Kodet med knytnæver!"
        , "3% kode, 79% slam"])



### PAGES ###

@app.route('/')
@logged_in
def front():
    vejleder = session['tutor']
    mentor = session['mentor']
    news = data.execute("SELECT * FROM News ORDER BY created DESC")# WHERE for_tutors = ? OR for_mentors = ?", tutor, mentor)
    return render_template("front.html", news=news)

@app.route('/rusmanager')
@logged_in
def rusmanager():
    #TODO: use "with data.data() as db:"
    db = data.data()
    cur = db.execute("select rid, name from Russer")
    russer = cur.fetchall()
    db.close()
    # russer = [{'name':"A", 'rid':-1},{'name':"B", 'rid':-2}]
    return render_template("rusmanager.html", russer=russer)

@app.route('/rus/<rid>', methods=['GET', 'POST'])
@logged_in
def ruspage(rid):
    #form = RusForm(request.form)
    if request.method == "POST":# and form.validate():
        checkboxes = [
            'called',
            'uniday',
            'campus',
            'tour',
        ]
        'rustour'
        'dutyteam'

        if 'cancel' in request.form:
            flash(escape(u"Ændringer anulleret"))
            return redirect(url_for('rusmanager'))

        print(request.form)
        with data.data() as db:
            for field in textfields:
                #SQL injection safe:
                sql = "UPDATE Russer SET {0} = ? WHERE rid == ?;".format(field)
                cur = db.execute(sql, (request.form[field], rid))

            for field in checkboxes:
                #SQL injection safe:
                val = 1 if field in request.form else 0
                sql = "UPDATE Russer SET {0} = ? WHERE rid == ?;".format(field)
                cur = db.execute(sql, (val, rid))

            sql = "UPDATE Russer SET birthday = ? WHERE rid == ?;"
            cur = db.execute(sql, (request.form['birthday'], rid))


        flash("Rus opdateret")
        return redirect(url_for('rusmanager'))
    else:
        with data.data() as db:
            cur = db.execute("SELECT * FROM Russer WHERE rid == ?", (rid,))
            rus = cur.fetchone()

            if not rus:
                return "Den rus findes ikke din spasser!"

            rus = {k:v if v != None else "" for k,v in zip(rus.keys(), rus)}
            return render_template("rus.html", rus=rus)

@app.route('/ny_rus', methods=['GET', 'POST'])
@logged_in
def new_rus():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape(u"Rus IKKE tilføjet"))
            return redirect(url_for('rusmanager'))

        with data.data() as db:
            cur = db.cursor()
            name = " ".join([x.capitalize() for x in request.form['name'].split()])
            cur = cur.execute("INSERT INTO Russer(name, called) VALUES(?,?)", (name,0))
            rus = cur.fetchone()
            flash("Rus oprettet")
            return redirect(url_for('ruspage', rid=str(cur.lastrowid)))
    else:
        return render_template("ny_rus.html")


@app.route('/schedule')
def schedule_overview():
    with data.data() as db:
        cur = db.execute("SELECT s_id, title, closes FROM Schedule")
        events = cur.fetchall()
        cur.close()
        return render_template("schedule_overview.html",events=events)

@app.route('/schedule/new', methods=['GET','POST'])
def new_schedule():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash("Oprettelse annulleret")
            return redirect(url_for('schedule_overview'))
        with data.data() as db:
            cur = db.execute(
                "INSERT INTO Schedule(title, description, created, closes) VALUES(?,?,?,?)", (
                request.form['title'],
                request.form['description'],
                str(datetime.datetime.now()),
                request.form['deadline']))
            flash(u"Oprettelse gennemført")
            return redirect(url_for('schedule_overview'))
    else:
        return render_template("new_schedule.html")

@app.route('/schedule/<sid>', methods=['GET', 'POST'])
def schedule_event(sid):
    with data.data() as db:
        cur = db.execute("SELECT s_id, title, description, created, closes FROM Schedule WHERE s_id = ?", sid)
        event = cur.fetchone()
    return render_template("schedule_event.html", event=event)

@app.route('/new_user', methods=['GET', 'POST'])
#adminrights
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
