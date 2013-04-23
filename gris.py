# -*- coding: utf-8 -*-

import sqlite3
from functools import wraps
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape
import random

app = Flask(__name__)
app.config.from_object("config")

def connect_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def logged_in(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        if not session.get('logged_in'):
            session['login_origin'] = request.path
            abort(401)
        else:
            return fn(*args, **kwargs)
    return decorator

from wtforms import Form, TextField, validators

@app.errorhandler(401)
def error(code):
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if (request.form['username'] != app.config['USERNAME'] or
            request.form['password'] != app.config['PASSWORD']):
            error = flash('Invalid username or password')
        else:
            session['logged_in'] = True
            flash('Login succesful')
            return redirect(session.pop('login_origin', url_for('front')))
            return redirect(url_for('front'))
    return render_template("login.html", error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("Logout succesful")
    return redirect(url_for('front'))
    return redirect('http://rkg.diku.dk')

textfields = [
    'navn',
    'udfyldt_af',
    'co',
    'addrese',
    'postnummer',
    'by',
    'flyttedato',
    'ny_adresse',
    'ny_postnummer',
    'ny_by',
    'tlf',
    'email',
    'foedselsdato',
    'ferie',
    'prioritet',
    'gymnasie',
    'lavet_efter',
    'kodeerfaring',
    'saerlige_behov',
    'spiller_musik',
    'andet',
]





@app.route('/')
@logged_in
def front():
    return redirect(url_for('rusmanager'))

@app.route('/rusmanager')
@logged_in
def rusmanager():
    #TODO: use "with connect_db() as db:"
    db = connect_db()
    cur = db.execute("select uid, navn from Russer")
    russer = cur.fetchall()
    db.close()
    # russer = [{'name':"A", 'uid':-1},{'name':"B", 'uid':-2}]
    return render_template("rusmanager.html", russer=russer)

@app.route('/rus/<uid>', methods=['GET', 'POST'])
@logged_in
def ruspage(uid):
    #form = RusForm(request.form)
    if request.method == "POST":# and form.validate():
        checkboxes = [
            'opringet',
            'deltager_unidag',
            'deltager_campus',
            'deltager_hytte',
        ]
        'rustur'
        'tjansehold'

        if 'anuller' in request.form:
            flash(escape(u"Ændringer anulleret"))
            return redirect(url_for('rusmanager'))

        with connect_db() as db:
            for field in textfields:
                sql = "UPDATE Russer SET {0} = ? WHERE uid == ?;".format(field)
                cur = db.execute(sql, (request.form[field], uid))

            for field in checkboxes:
                val = 1 if field in request.form else 0
                sql = "UPDATE Russer SET {0} = ? WHERE uid == ?;".format(field)
                cur = db.execute(sql, (val, uid))

        flash("Rus opdateret")
        return redirect(url_for('rusmanager'))
    else:
        with connect_db() as db:
            cur = db.execute("SELECT * FROM Russer WHERE uid == ?", (uid,))
            rus = cur.fetchone()

            if not rus:
                return "Den rus findes ikke din spasser!"

            rus = {k:v if v != None else "" for k,v in zip(rus.keys(), rus)}
            return render_template("rus.html", rus=rus)

@app.route('/ny_rus', methods=['GET', 'POST'])
@logged_in
def new_rus():
    if request.method == "POST":
        if 'anuller' in request.form:
            flash(escape(u"Rus IKKE tilføjet"))
            return redirect(url_for('rusmanager'))

        with connect_db() as db:
            cur = db.cursor()
            navn = " ".join([x.capitalize() for x in request.form['navn'].split()])
            cur = cur.execute("INSERT INTO Russer(navn, opringet) VALUES(?,?)", (navn,0))
            rus = cur.fetchone()
            flash("Rus oprettet")
            return redirect(url_for('ruspage', uid=str(cur.lastrowid)))
    else:
        return render_template("ny_rus.html")
def random_greeting():
    with connect_db() as db:
        cur = db.execute("SELECT COUNT(uid) FROM Russer")
        count = cur.fetchone()[0]

    return random.choice(
        [ "GRIS"
        , "Bacon"
        , "Velkommen"
        , "Nu med ekstra procenter!"
        , u"Over hans kamin, hænger kun platin"
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
          ,"<a href=\"http://en.wikipedia.org/wiki/Special:Random\">Learn more:</a>"
        , "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."
        , "Der er {0} russer i databasen".format(count)
        , "3% kode, 79% slam"])


app.jinja_env.globals.update(random_greeting=random_greeting)
app.jinja_env.globals.update(textfields=textfields)

if __name__ == '__main__':
    app.run()
