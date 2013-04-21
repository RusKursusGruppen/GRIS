import sqlite3
from functools import wraps
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape

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

@app.errorhandler(401)
def error(code):
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if (request.form['username'] != app.config['USERNAME'] or
            request.form['password'] != app.config['PASSWORD']):
            error = 'Invalid username or password'
        else:
            session['logged_in'] = True
            flash('Login succesful')
            return redirect(session.pop('login_origin', url_for('front')))
            return redirect(url_for('front'))
    else:
        return render_template("login.html", error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("Logout succesful")
    return redirect(url_for('front'))
    return redirect('http://rkg.diku.dk')







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
    print type(uid)
    if request.method == "POST":
        data = [
            'navn',
            'udfyldt_af',
            'opringet',
            # 'co',
            # 'addrese',
            # 'postnummer',
            # 'by',
            # 'flyttedato',
            # 'ny_adresse',
            # 'ny_postnummer',
            # 'ny_by',
            # 'tlf',
            # 'email',
            # 'foedselsdato',
            # 'ferie',
            # 'prioritet',
            # 'gymnasie',
            # 'lavet_efter',
            # 'kodeerfaring',
            # 'saerlige_behov',
            # 'spiller_musik',
            # 'andet',
            # 'deltager_unidag',
            # 'deltager_campus',
            # 'deltager_hytte',
            # 'rustur',
            # 'tjansehold'
        ]
        # data = ['andet'
        #         ,'by']
        # with connect_db() as db:
        for field in data:
            print u'UPDATE Russer SET {0} = {1} where uid =={2}?'.format(field, request.form[field], uid)
        #         cur = db.execute('UPDATE Russer SET ? = ? where uid == ?', (field, request.form[field], uid))
        #     db.commit()
        return "Submitted"
    else:
        with connect_db() as db:
            cur = db.execute("select * from Russer where uid == ?", (uid,))
            rus = cur.fetchone()

            if not rus:
                return "Den rus findes ikke din spasser!"

            print type(rus)
            rus = {k:v if v != None else "" for k,v in zip(rus.keys(), rus)}
            return render_template("rus.html", rus=rus)

if __name__ == '__main__':
    app.run()
