# -*- coding: utf-8 -*-

import random, string, time

from flask import Blueprint, request, session

from lib import mail, password
from lib.tools import abort, empty, jsonify, logged_in, now, sleep, success

import config

blueprint = Blueprint("usermanager", __name__, url_prefix="/api")
from gris import data


### HELPERS ###
def loginname(username):
    return username.lower()


def create_user(username, raw_password, name=None, email=None, groups=[]):
    b = data.Bucket()
    b.username = username
    b.loginname = loginname(username)
    b.password = password.encode(raw_password)
    b.name = name
    b.email = email
    user = (b >= "Users")
    set_user_groups(user.user_id, groups)

    mail.new_user_adminmail.format(b).to_admins()


def update_password(user_id, raw_password):
    passwd = password.encode(raw_password)
    data.execute("UPDATE Users SET password = ? WHERE user_id = ?", passwd, user_id)


def set_user_groups(user_id, groups):
    with data.transaction() as t:
        t.execute("DELETE FROM Group_users WHERE user_id = ?", user_id)
        for group in groups:
            add_user_to_group(user_id, group)


def add_user_to_group(user_id, group):
    group_id = data.execute("SELECT group_id FROM Groups WHERE groupname = ?", group).scalar()
    data.execute("INSERT INTO Group_users(user_id, group_id) VALUES(?,?)", user_id, group_id)


def remove_user_from_group(user_id, group):
    data.execute("DELETE FROM Group_users WHERE user_id = ? AND groupname = ?", user_id, group)


def validate_username(username):
    if len(username) <= 0:
        return False
    legal_characters = string.ascii_letters + "æøåÆØÅ-_,.!0123456789"
    return all(c in legal_characters for c in username)

def validate_password(password):
    return len(password) > 0

### SESSIONS ###
@blueprint.route("/usermanager/authenticated", methods=["GET", "POST"])
def authenticated():
    logged_in = "logged_in" in session and session["logged_in"]
    return jsonify(authenticated=logged_in)

@blueprint.route("/usermanager/authenticate", methods=["POST"])
def authenticate():
    b = data.Bucket(request.form)
    name = loginname(b.username)
    users = data.execute("SELECT user_id, username, password, deleted FROM Users WHERE loginname = ?", name)

    sleep(config.SLEEP_ATTEMPT)
    if empty(users) or not password.check(b.raw_password, users.one()["password"]):
        sleep(config.SLEEP_FAIL)
        abort(400, "invalid username or password")

    user = users.one()
    if user.deleted:
        abort(400, "user deleted")

    update_password(user.user_id, b.raw_password)

    login(user.user_id, user.username)
    return success()

@blueprint.route("/usermanager/unauthenticate", methods=["GET", "POST"])
def unauthenticate():
    logout()
    return success()

def login(user_id, username):
    session["logged_in"] = True
    session["user_id"] = user_id
    session["username"] = username

def logout():
    session.clear()

### USERS ###
@blueprint.route("/usermanager/users", methods=["GET"])
@logged_in
def users():
    deleted = request.args.get("deleted", False)
    users = data.execute("""SELECT
    user_id,
    username,
    loginname
    created,
    name,
    email,
    phone,
    driverslicence,
    address,
    zipcode,
    city,
    birthday,
    diku_age,
    about_me
    FROM Users WHERE deleted = ?""", deleted)
    return users

@blueprint.route("/usermanager/user", methods=["GET"])
@logged_in
def user():
    user_id = request.args.get("user_id", None)
    if user_id is None:
        abort(400, "unspecified user")
    users = data.execute("""SELECT
    user_id,
    username,
    loginname,
    created,
    name,
    email,
    phone,
    driverslicence,
    address,
    zipcode,
    city,
    birthday,
    diku_age,
    about_me,
    deleted
    FROM Users WHERE user_id = ?""", user_id).one(404, "No such user")

    #TODO: tour information and mentor information
    return users

@blueprint.route("usermanager/settings", methods=["POST"])
@logged_in
def settings():
    user_id = session["user_id"]
    b = data.Bucket(request.form)
    b.name
    b.email
    b.phone
    b.driverslicence
    b.address
    b.zipcode
    b.city
    # b.diku_age
    b.about_me
    b >> ("UPDATE Users $ WHERE user_id = ?", user_id)

    return success()





### KEY HANDLING ###
def delete_old_keys():
    """Delete all old keys"""

    # Weed out old creation keys
    overtime = now() - datetime.timedelta(days=30)
    data.execute("DELETE FROM User_creation_keys WHERE created <= ?", overtime)

    # Weed out old password keys
    overtime = now() - datetime.timedelta(minutes=20)
    data.execute("DELETE FROM User_forgotten_password_keys WHERE created <= ?", overtime)


def generate_key(bucket, table, keyname=None):
    length = config.USER_KEY_LINK_LENGTH
    alphabet = string.ascii_letters + string.digits

    while True:
        key = "".join(random.choice(alphabet) for x in range(length))
        existing = data.execute("SELECT key FROM User_creation_keys WHERE key = ?", key)
        if len(existing) > 0:
            continue
        try:
            if keyname is not None:
                bucket[keyname] = key
            else:
                bucket.key = key

            bucket >= "User_creation_keys"
            return key
        except psycopg2.IntegrityError as e:
            if e.pgerror.startswith("ERROR:  duplicate key value violates unique constraint \"user_forgotten_password_keys_pkey\""):
                continue
            else:
                raise

### PASSWORDS ###
@blueprint.route("/usermanager/password/change", methods=["POST"])
@logged_in
def change_password():
    user_id = session["user_id"]
    current_password = data.execute("SELECT password FROM Users WHERE user_id = ?", user_id).scalar()
    b = data.Bucket(request.form)
    if not password.check(b.current_password, current_password):
        logout()
        abort(304, "incorrect password")

    if b.new_password1 != b.new_password2:
        abort(400, "unequal passwords")

    if not validate_password(b.new_password2):
        abort(400, "illegal password")

    update_password(username, b.new1)
    return success()


@blueprint.route("/usermanager/password/forgot", methods=["POST"])
def forgot_password():
    #TODO: Should the current password be deleted in the database? or would that be anoying as other people could delete your password if they know your username."
    username = request.form.get("username", None)
    if username is None:
        abort(400, "unspecified username")
    user = data.execute("SELECT user_id, username, name, email, phone FROM Users WHERE loginname = ?",
                        loginname(username)).one(400, "No such user")

    if user.email is None:
        mail.forgot_password_no_email_adminmail.format(user).to_admins()
        abort("User has no email, please contact an admin.")

    already_forgotten = data.execute("SELECT count(*) FROM User_forgotten_password_keys WHERE user_id = ?", user.user_id).scalar()
    if already_forgotten > 0:
        mail.forgot_password_multiple_adminmail.format(username=username, times=already_forgotten).to_admins()

    b = data.Bucket()
    b.username = user.username
    b.created = now()
    key = generate_key(b, "User_forgotten_password_keys")
    # url = config.URL + url_for("???", key=key)
    url = config.URL + "/TODO-find-out-how-to-set-up-link/" + key #TODO: find out where to link to
    failed = mail.forgot_password.format(name=user.name, url=url).send(user.email)
    if len(failed) == 0:
        mail.forgot_password_no_email_adminmail.format(user).to_admins()

@blueprint.route("/usermanager/password/renew", methods=["GET", "POST"])
def renew_forgotten_password():
    #TODO: integrate with angularjs, there needs to be a GET page or something
    #TODO: sleep fail
    if request.method == "POST":
        delete_old_keys()
        sleep(config.SLEEP_ATTEMPT)
        key = request.args.get("key", None)
        forgotten = data.execute("SELECT * FROM User_forgotten_password_keys WHERE key = ?", key).one("The link you used expired/does not exist")

        b = data.Bucket(request.form)

        if b.new_password1 != b.new_password2:
            abort(400, "unequal passwords")

        if not validate_password(b.new_password1):
            abort(400, "invalid password")

        data.execute("DELETE FROM User_forgotten_password_keys WHERE key = ?", key)
        update_password(username, b.new1)

        login(user.user_id, user.username)

        return success()


### USER INVITATION ###
@blueprint.route('/usermanager/invite', methods=["GET","POST"])
@logged_in
def invite():
    emails = request.form["emails"].split()
    for email in emails:
        b = data.Bucket()
        b.created = now()
        key = generate_creation_key(b, "User_creation_keys")
        # url = config.URL + url_for("???", key=key)
        url = config.URL + "/TODO-find-out-how-to-set-up-link/" + key #TODO: find out where to link to
        result = mail.invitation.format(url=url).send(email)
        failed.extend(result)

    for fail in failed:
        emails.remvove(fail)

    # Notify admins
    mail.invitation_adminmail.format(emails="\n".join(emails),
                                      failed="\n".join(failed)).to_admins()

@blueprint.route('/usermanager/new', methods=["GET","POST"])
def new_user():
    #TODO: integrate with angularjs, there needs to be a GET page or something
    #TODO: sleep fail
    delete_old_keys()
    sleep(config.SLEEP_ATTEMPT)

    key = request.values.get("key", None)
    result = data.execute("SELECT key, email FROM User_creation_keys WHERE key = ?", key).one("The link you used expired/does not exist")

    if request.method == "POST":
        b = data.Bucket(request.form)
        if not validate_username(b.username):
            abort(400, "invalid username")

        if b.new_password1 != b.new_password2:
            abort(400, "unequal passwords")

        if not validate_password(b.new_password1):
            abort(400, "invalid password")

        data.execute("DELETE FROM User_creation_keys WHERE key = ?", key)
        create_user(b.username, b.password1, b.name, b.email)

        login(b.user_id, b.username)
