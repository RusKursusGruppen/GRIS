# -*- coding: utf-8 -*-

import sqlite3
import random
from functools import wraps
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape

import data
import password

app = Flask(__name__)
app.config.from_object("config")


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

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if (request.form['username'] != app.config['USERNAME'] or
#             request.form['password'] != app.config['PASSWORD']):
#             error = flash('Invalid username or password')
#         else:
#             session['logged_in'] = True
#             flash('Login succesful')
#             return redirect(session.pop('login_origin', url_for('front')))
#     return render_template("login.html", error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']
        with data.vejledere() as db:
            print 'SELECT password, admin FROM Vejledere WHERE username = '+ str(username)
            cur = db.execute('SELECT password, admin FROM Vejledere WHERE username = ?', (username,))
            v = cur.fetchone()
            if empty(v) or not password.check(raw_password, v['password']):
                flash('Invalid username or password')
            else:
                session['logged_in'] = True
                session['admin'] = v['admin'] == 1
                flash("Login succesful")
                return redirect(session.pop('login_origin', url_for('front')))
    return render_template("login.html", error=error)

def new_vejleder(username, raw_password, navn="", admin=0):
    with data.vejledere() as db:
        cur = db.cursor()
        passw = password.set(raw_password)
        cur.execute("INSERT INTO Vejledere(username, password, navn, admin) VALUES(?,?,?,?)", (username, passw, navn, admin))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("Logout succesful")
    return redirect(url_for('front'))
    return redirect('http://rkg.diku.dk')

textfields = [ 'navn',
               'udfyldt_af',
               'co',
               'addrese',
               'postnummer',
               'by',
               'flytte_tidspunkt',
               'ny_adresse',
               'ny_postnummer',
               'ny_by',
               'tlf',
               'email',
               'ferie',
               'prioritet',
               'gymnasie',
               'lavet_efter',
               'kodeerfaring',
               'saerlige_behov',
               'spiller_musik',
               'andet',]

def random_greeting():
    with data.russer() as db:
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
        , "3% kode, 79% slam"])





@app.route('/')
@logged_in
def front():
    return redirect(url_for('rusmanager'))

@app.route('/rusmanager')
@logged_in
def rusmanager():
    #TODO: use "with data.russer() as db:"
    db = data.russer()
    cur = db.execute("select rid, navn from Russer")
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

        with data.russer() as db:
            for field in textfields:
                sql = "UPDATE Russer SET {0} = ? WHERE rid == ?;".format(field)
                cur = db.execute(sql, (request.form[field], rid))

            for field in checkboxes:
                val = 1 if field in request.form else 0
                sql = "UPDATE Russer SET {0} = ? WHERE rid == ?;".format(field)
                cur = db.execute(sql, (val, rid))

            sql = "UPDATE Russer SET foedselsdato = ? WHERE rid == ?;"
            cur = db.execute(sql, (request.form['foedselsdato'], rid))


        flash("Rus opdateret")
        return redirect(url_for('rusmanager'))
    else:
        with data.russer() as db:
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
        if 'anuller' in request.form:
            flash(escape(u"Rus IKKE tilføjet"))
            return redirect(url_for('rusmanager'))

        with data.russer() as db:
            cur = db.cursor()
            navn = " ".join([x.capitalize() for x in request.form['navn'].split()])
            cur = cur.execute("INSERT INTO Russer(navn, opringet) VALUES(?,?)", (navn,0))
            rus = cur.fetchone()
            flash("Rus oprettet")
            return redirect(url_for('ruspage', rid=str(cur.lastrowid)))
    else:
        return render_template("ny_rus.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")

app.jinja_env.globals.update(random_greeting=random_greeting)
app.jinja_env.globals.update(textfields=textfields)

if __name__ == '__main__':
    app.run()
