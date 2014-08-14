# -*- coding: utf-8 -*-

import random, datetime, string, time
import psycopg2

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

        if 'forgot' in request.form:
            try:
                forgot_password(username)
            except Exception as e:
                if str(e) != "No such user/No valid email":
                    raise
                flash("Kunne ikke sende en mail til denne bruger")
                return redirect(url_for('usermanager.login'))

            return render_template("usermanager/forgot.html", username=username)

        print(type(raw_password))
        user = data.execute('SELECT password, deleted FROM Users WHERE username = ?', username)
        if empty(user) or not password.check(raw_password, user[0]['password']):
            flash('Invalid username or password')
        elif user[0]["deleted"]:
            flash('Sorry, your user has been deleted')
        else:
            session['logged_in'] = True
            session['username']  = username

            groups = data.execute('SELECT groupname FROM Group_users WHERE username = ?', username)
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
    data.execute("DELETE FROM Group_users WHERE username = ?", username)
    for group in groups:
        group_add_user(group, username)

def group_add_user(groupname, username):
    data.execute("INSERT INTO Group_users(groupname, username) VALUES(?,?)", groupname, username)

def group_remove_user(groupname, username):
    data.execute("DELETE FROM Group_users WHERE groupname = ? AND username = ?", groupname, username)

@usermanager.route('/usermanager/logout')
def logout():
    session.pop('logged_in', None)
    session.clear()
    flash("Logout succesful")
    return redirect(url_for('usermanager.login'))

@usermanager.route('/usermanager')
@logged_in
def overview():
    users = data.execute("select username, name from Users where deleted = ? order by name", False)
    return render_template("usermanager/overview.html", users=users)

@usermanager.route('/usermanager/deleted_users')
@logged_in
def deleted_users():
    users = data.execute("select username, name from Users where deleted = ? order by name", True)
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
        b.email
        b.phone
        b.address
        b.zipcode
        b.city
        b.birthday
        b.driverslicence = "driverslicence" in request.form
        b.diku_age
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
        elif isinstance(birthday, datetime.date):
            birthday = birthday.isoformat()

        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("name", "Fulde navn")
        w.textfield("email", "Email")
        w.textfield("phone", "Telefonnummer")
        w.textfield("address", "Adresse")
        w.textfield("zipcode", "Postnummer")
        w.textfield("city", "By")
        w.calendar("birthday", "Fødselsdag")
        w.checkbox("driverslicence", "Har du kørekort?")
        w.textfield("diku_age", "Hvornår startede du på DIKU?")
        w.textarea("about_me", "Lidt om mig")

        form = w.create(user)
        return render_template("form.html", form=form)

@usermanager.route('/usermanager/settings/password', methods=['GET', 'POST'])
@logged_in
def change_password():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape("Ændringer annulleret"))
            return redirect(url_for('usermanager.settings'))

        username = session["username"]
        current_password = data.execute("SELECT password FROM Users WHERE username = ?", username)[0]['password']
        print(current_password)

        b = data.Bucket(request.form)
        if not password.check(b.current, current_password):
            return logout()

        if b.new1 != b.new2:
            flash("De to løsner er ikke ens")
            return redirect(url_for('usermanager.change_password'))

        if b.new1 == "":
            flash("Du specificerede ikke et nyt løsen")
            return redirect(url_for('usermanager.change_password'))

        update_password(username, b.new1)

        return redirect(url_for('usermanager.settings'))

    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.password("current", "Nuværende løsen")
        w.password("new1", "Nyt løsen")
        w.password("new2", "Gentag nyt løsen")
        form = w.create()
        return render_template("form.html", form=form)

@usermanager.route("/usermanager/settings/password/renew/<key>", methods=['GET', 'POST'])
def renew_password(key):
    # EXPLANATION: weed out old creation keys
    overtime = now() - datetime.timedelta(minutes=20)
    data.execute("DELETE FROM User_forgotten_password_keys WHERE created <= ?", overtime)

    result = data.execute("SELECT * FROM User_forgotten_password_keys WHERE key = ?", key)
    if len(result) != 1:
        flash("Linket du fulgte er desvære udløbet, prøv igen")
        return redirect(url_front())
    result = result[0]

    if request.method == "POST":
        data.execute("DELETE FROM User_forgotten_password_keys WHERE key = ?", key)

        b = data.Bucket(request.form)

        if b.new1 != b.new2:
            flash("De to løsner er ikke ens")
            return redirect(url_for('usermanager.renew_password', key=key))
            print("kat")

        if b.new1 == "":
            flash("Du specificerede ikke et nyt løsen")
            return redirect(url_for('usermanager.renew_password', key=key))

        update_password(result['username'], b.new1)

        session['logged_in'] = True
        session['username']  = result['username']

        return redirect(url_front())

    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.password("new1", "Nyt løsen")
        w.password("new2", "Gentag nyt løsen")
        form = w.create()
        return render_template("form.html", form=form)


def forgot_password(username):
    user = data.execute("SELECT name, email from Users WHERE username = ?", username)
    if len(user) != 1:
        raise Exception("No such user/No valid email")

    min = config.USER_CREATION_KEY_MIN_LENGTH
    max = config.USER_CREATION_KEY_MAX_LENGTH
    length = random.randrange(min, max)
    alphabet = string.ascii_letters + string.digits

    finished = False
    while not finished:
        key = ''.join(random.choice(alphabet) for x in range(length))
        try:
            b = data.Bucket()
            b.username = username
            b.key = key
            b.created = now()
            b >= "User_forgotten_password_keys"
            finished = True
            break
        except psycopg2.IntegrityError as e:
            if str(e).startswith('duplicate key value violates unique constraint "user_forgotten_password_keys_pkey"'):
                finished = False
                continue
            else:
                raise
    user = user[0]
    email = user['email']

    if email == None or email == '':
        raise Exception("No such user/No valid email")

    url = config.URL + url_for("usermanager.renew_password", key=key)
    text = forgot_password_mail.format(name=user['name'], url=url)
    mail.send(email, "Glemt løsen", text)

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
        try:
            b = data.Bucket()
            b.key = key
            b.created = now()
            b >= "User_creation_keys"
            return key
        except psycopg2.IntegrityError as e:
            if str(e).startswith('duplicate key value violates unique constraint "user_creation_keys_pkey"'):
                continue
            else:
                raise

def sanitize_username(username):
    if len(username) <= 0:
        return False
    legal_characters = string.ascii_letters + "æøåÆØÅ-_0123456789"
    return all(c in legal_characters for c in username)

    #check that no such user already exists
    illegal_characters = [';" ']
    return not any(illegal in username for illegal in illegal_characters)

@usermanager.route('/usermanager/new/<key>', methods=['GET', 'POST'])
def new(key):
    time.sleep(random.randint(2,6))

    # EXPLANATION: weed out old creation keys
    overtime = now() - datetime.timedelta(days=30)
    data.execute("DELETE FROM User_creation_keys WHERE created <= ?", overtime)

    # EXPLANATION: Check if key exists/is valid
    result = data.execute("SELECT key, email FROM User_creation_keys WHERE key = ?", key)
    if empty(result):
        time.sleep(random.randint(5,21))
        # TODO: Send to errorpage?
        return redirect(url_front())

    if request.method == "POST":
        data.execute("DELETE FROM User_creation_keys WHERE key = ?", key)
        if 'cancel' in request.form:
            flash("Oprettelse anulleret")
            return redirect(url_front())

        b = data.Bucket(request.form)
        if not sanitize_username(b.username):
            raise Exception()

        if b.password1 != b.password2:
            flash("Du gav to forskellige løsener, prøv igen")
            return html.back()
        if b.password1 == "":
            flash("Du skal vælge et løsen")
            return html.back()

        create_user(b.username, b.password1, b.name)
        flash("Ny bruger oprettet")

        return redirect(url_for('usermanager.login'))
    else:

        wb = html.WebBuilder()
        wb.form()
        wb.formtable()
        wb.textfield("username", "Brugernavn (Hvad du bliver kaldt på DIKU):")
        wb.textfield("name", "Fulde navn:")
        wb.textfield("email", "Email:", value=result[0]["email"])
        wb.password("password1", "Løsen")
        wb.password("password2", "Gentag løsen")
        form = wb.create()
        return render_template("form.html", form=form)

@usermanager.route('/usermanager/invite', methods=['GET', 'POST'])
@logged_in
def invite():
    if request.method == "POST":
        if 'cancel' in request.form:
            return redirect(url_front())

        key = generate_key()

        email_address = request.form['email']
        url = config.URL + url_for("usermanager.new", key=key)
        text = invite_mail.format(url=url)

        data.execute("UPDATE User_creation_keys SET email = ? WHERE key = ?", email_address, key)

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

<a href="{url}">Opret bruger</a>
"""


forgot_password_mail = """
Hej {name}, du har glemt dit løsen.
Vi har derfor sendt dig dette link hvor du kan vælge et nyt.
Linket virker kun de næste 20 minutter.

<a href="{url}">Vælg nyt løsen</a>

Hvis du ikke har glemt dit løsen kan du se bort fra denne mail.
"""
