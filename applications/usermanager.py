# -*- coding: utf-8 -*-

import random, datetime, string, time

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, mail, html
from lib.tools import logged_in, empty, url_front, now, unnonify

import config

usermanager = Blueprint('usermanager', __name__, template_folder = '../templates/usermanager')

### LOGIN/USERMANAGEMENT ###
@usermanager.route('/usermanager/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']
        print(type(raw_password))
        user = data.execute('SELECT password, deleted FROM Users WHERE username = ?', username)
        if empty(user) or not password.check(raw_password, user[0]['password']):
            flash('Invalid username or password')
        elif user[0]["deleted"] == 1:
            flash('Sorry, your user has been deleted')
        else:
            session['logged_in'] = True
            session['username']  = username

            groups = data.execute('SELECT groupname FROM User_groups WHERE username = ?', username)
            groups = [group['groupname'] for group in groups]
            session['groups'] = groups

            update_password(username, raw_password)
            flash("Login succesful")
            return redirect(session.pop('login_origin', url_front()))
    return render_template("usermanager/login.html", error=error)

def create_user(username, raw_password, name="", groups=[]):
    passw = password.encode(raw_password)
    data.execute("INSERT INTO Users(username, password, name) VALUES(?,?,?)", username, passw, name)
    set_user_groups(username, groups)

def update_password(username, raw_password):
    passwd = password.encode(raw_password)
    data.execute("UPDATE Users SET password = ? WHERE username = ?", passwd, username)

def set_user_groups(username, groups):
    data.execute("DELETE FROM User_groups WHERE username = ?", username)
    for group in groups:
        user_group_add(username, group)

def user_group_add(username, group):
    data.execute("INSERT INTO User_groups(username, groupname) VALUES(?,?)", username, group)

def user_group_remove(username, group):
    data.execute("DELETE FROM User_groups WHERE username = ? and groupname = ?", username, group)

@usermanager.route('/usermanager/logout')
def logout():
    session.pop('logged_in', None)
    session.clear()
    flash("Logout succesful")
    return redirect(url_for('usermanager.login'))

@usermanager.route('/usermanager')
@logged_in
def overview():
    users = data.execute("select username, name from Users where deleted = 0 order by name")
    return render_template("usermanager/overview.html", users=users)

@usermanager.route('/usermanager/deleted_users')
@logged_in
def deleted_users():
    users = data.execute("select username, name from Users where deleted = 1 order by name")
    return render_template("usermanager/deleted_users.html", users=users)



@usermanager.route('/usermanager/settings', methods=['GET', 'POST'])
@logged_in
def settings():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape("Ændringer annulleret"))
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

        return redirect(url_for('usermanager.user', username=username))

    else:
        user = data.execute("SELECT * FROM Users WHERE username = ?", session["username"])
        user = user[0]
        user = unnonify(user)

        birthday = user["birthday"]
        if birthday == None:
            birthday = ""

        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("name", "Fulde navn")
        w.textfield("address", "Adresse")
        w.textfield("zipcode", "Postnummer")
        w.textfield("city", "By")
        w.textfield("phone", "Telefonnummer")
        w.textfield("email", "Email")
#        w.textfield("birthday", "Fødselsdag")
        w.html('<input type="text" id="usermanager.birthday" maxlength="25" size="25" name="birthday" value="'+birthday+'">' +
               html.calendar("usermanager.birthday")
               + '<span class="note">(Format: yyyy-MM-dd)</span>', description="Fødselsdag")

        w.checkbox("driverslicence", "Har du kørekort?")
        w.textfield("diku_age", "Hvornår startede du på DIKU?")
        w.textfield("earlier_tours", "Tidligere rusture (brug ; mellem de forskellige turnavne)")
        w.textarea("about_me", "Lidt om mig")

        form = w.create(user)
        return render_template("form.html", form=form)

@usermanager.route('/usermanager/user/<username>', methods=['GET', 'POST'])
@logged_in
def user(username):
    user = data.execute("SELECT * FROM Users WHERE username = ?", username)
    user = user[0]
    user = unnonify(user)

    return render_template("usermanager/user.html", user=user)


### USER INVITATION ###

def generate_key():
    min = config.USER_CREATION_KEY_MIN_LENGTH
    max = config.USER_CREATION_KEY_MAX_LENGTH
    length = random.randrange(min, max)
    alphabet = string.ascii_letters + string.digits
    while True:
        key = ''.join(random.choice(alphabet) for x in range(length))
        result = data.execute("select key from User_creation_keys where key = ?", key)
        if empty(result):
            return key

def sanitize_username(username):
    legal_characters = string.ascii_letters + "æøåÆØÅ-_0123456789"
    return all(c in legal_characters for c in username)

    #check that no such user already exists
    illegal_characters = [';" ']
    return not any(illegal in username for illegal in illegal_characters)

@usermanager.route('/usermanager/new/<key>', methods=['GET', 'POST'])
def new(key):
    time.sleep(random.randint(2,6))
    #time.sleep(3)

    # EXPLANATION: weed out old creation keys
    overtime = str(datetime.datetime.now() - datetime.timedelta(days=30))
    data.execute("DELETE FROM User_creation_keys WHERE created <= ?", overtime)

    # EXPLANATION: Check if key exists/is valid
    result = data.execute("SELECT key FROM User_creation_keys WHERE key = ?", key)
    if empty(result):
        time.sleep(random.randint(5,21))
        # TODO: Send to errorpage?
        return redirect(url_front())

    if request.method == "POST":
        data.execute("DELETE FROM User_creation_keys WHERE key = ?", key)
        if 'cancel' in request.form:
            flash("Oprettelse anulleret")
            return redirect(url_front())

        username = request.form['username']
        if not sanitize_username(username):
            raise Exception()
        name = request.form['name']
        raw_password = request.form['password']
        admin = request.form['admin']
        create_user(username, raw_password, name, admin)
        flash("Ny bruger oprettet")

        return redirect(url_for('usermanager.login'))
    else:
        return render_template("usermanager/new.html", key=key)

@usermanager.route('/usermanager/invite', methods=['GET', 'POST'])
@logged_in
def invite():
    if request.method == "POST":
        if 'cancel' in request.form:
            return redirect(url_front())
        key = generate_key()
        data.execute("INSERT INTO User_creation_keys(key, created) VALUES (?, ?)", key, now())
        print(key)

        email_address = request.form['email']
        text = invite_mail.format(key)

        mail.send(email_address, "Invitation til GRIS", text)
        flash("Invitation sendt")

        return redirect(url_front())

    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("email", "Email")
        form = w.create()
        return render_template("form.html", form=form)

invite_mail = """
Hej du er blevet inviteret til GRIS.
GRIS er RKGs intranet, hvis du skal være med i RKG skal du have en bruger her.
For at oprette en bruger skal du følge det følgende link.
Linket er unikt og virker kun en enkelt gang.

<a href="http://rkg.diku.dk/gris/usermanger/new/{0}>Opret bruger</a>
"""
