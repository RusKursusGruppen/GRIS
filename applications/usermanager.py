# -*- coding: utf-8 -*-

import random, datetime, string, time

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, mail, html
from lib.tools import logged_in, empty, url_front

import config

usermanager = Blueprint('usermanager', __name__, template_folder = '../templates/usermanager')

### LOGIN/USERMANAGEMENT ###
@usermanager.route('/usermanager/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']
        with data.data() as db:
            v = data.execute('SELECT password, admin, rkg, tutor, mentor FROM Users WHERE username = ?', username)
            v = v[0]
            if empty(v) or not password.check(raw_password, v[str('password')]):
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
                return redirect(session.pop('login_origin', url_front()))
    return render_template("usermanager/login.html", error=error)

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


@usermanager.route('/usermanager/logout')
def logout():
    session.pop('logged_in', None)
    flash("Logout succesful")
    return redirect(url_for('login'))

@usermanager.route('/usermanager')
@logged_in
def overview():
    users = data.execute("select username, name from Users")
    return render_template("usermanager/overview.html", users=users)



@usermanager.route('/usermanager/settings', methods=['GET', 'POST'])
@logged_in
def settings():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape(u"Ændringer annulleret"))
            return redirect(url_for('usermanager.overview'))

        username = session["username"]

        b = data.Bucket(request.form)
        b.name
        b.address
        b.zipcode
        b.city
        b.phone
        b.email
        b.birthday
        b.driverslicence = 1 if "driverslicence" in request.form else 0
        b.diku_age
        b.earlier_tours
        b.about_me# = request.form["about_me"]
        b >> ("UPDATE Users $ WHERE username = ?", username)

        return redirect(url_for('usermanager.overview'))
    else:
        user = data.execute("SELECT * FROM Users WHERE username = ?", session["username"])
        user = user[0]
        user = {k:v if v != None else "" for k,v in zip(user.keys(), user)}

        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("name", "Fulde navn")
        w.textfield("address", "Adresse")
        w.textfield("zipcode", "Postnummer")
        w.textfield("city", "By")
        w.textfield("phone", "Telefonnummer")
        w.textfield("email", "Email")
        w.textfield("birthday", u"Fødselsdag")
        w.checkbox("driverslicence", u"Har du kørekort?")
        w.textfield("diku_age", u"Hvornår startede du på DIKU?")
        w.textfield("earlier_tours", "Tidligere rusture (brug ; mellem de forskellige turnavne)")
        w.textarea("about_me", "Lidt om mig")

        form = w.create(user)
        return render_template("usermanager/settings.html", form=form)

@usermanager.route('/usermanager/user/<username>', methods=['GET', 'POST'])
@logged_in
def user(username):
    user = data.execute("SELECT * FROM Users WHERE username = ?", username)
    user = user[0]
    user = {k:v if v != None else "" for k,v in zip(user.keys(), user)}
    return render_template("usermanager/user.html", user=user)


### USER INVITATION ###

def generate_key():
    min = config.USER_CREATION_KEY_MIN_LENGTH
    max = config.USER_CREATION_KEY_MAX_LENGTH
    length = random.randrange(min, max)
    alphabet = string.letters + string.digits
    while True:
        key = ''.join(random.choice(alphabet) for x in range(length))
        result = data.execute("select key from User_creation_keys where key = ?", key)
        if empty(result):
            return key

@usermanager.route('/usermanager/new/<key>', methods=['GET', 'POST'])
def new(key):
    #time.sleep(3)

    result = data.execute("select key from User_creation_keys where key = ?", key)
    if empty(result):
        return redirect(url_front())

    if request.method == "POST":
        data.execute("DELETE FROM User_creation_keys WHERE key = ?", key)
        if 'cancel' in request.form:
            flash("Oprettelse anulleret")
            return redirect(url_front())

        username = request.form['username']
        name = request.form['name']
        raw_password = request.form['password']
        admin = request.form['admin']
        create_user(username, raw_password, name, admin)
        flash("Ny bruger oprettet")

        return redirect(url_for('usermanager.settings'))
    else:
        data.execute("SELECT * FROM User_creation_keys")
        return render_template("usermanager/new.html", key=key)

@usermanager.route('/usermanager/invite', methods=['GET', 'POST'])
def invite():
    if request.method == "POST":
        if 'cancel' in request.form:
            return redirect(url_front())
        key = generate_key()
        data.execute("INSERT INTO User_creation_keys VALUES (?)", key)

        email_address = request.form['email']
        text = invite_mail.format(key)

        mail.send(email_address, "Invitation til GRIS", text)
        flash("Invitation sendt")

        return redirect(url_front())
    return render_template("usermanager/invite.html")

invite_mail = u"""
Hej du er blevet inviteret til GRIS.
GRIS er RKGs intranet, hvis du skal være med i RKG skal du have en bruger her.
For at oprette en bruger skal du følge det følgende link.
Linket er unikt og virker kun en enkelt gang.

<a href="http://rkg.diku.dk/gris/usermanger/new/{0}>Opret bruger</a>
"""
