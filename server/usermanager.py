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
    b.name = name
    b.email = email
    user = (b >= "Users")

    pb = data.Bucket()
    pb.user_id = user.user_id
    pb.password = password.encode(raw_password)
    pb >= "Passwords"

    set_user_groups(user.user_id, groups)

    mail.new_user_adminmail.format(b).to_admins()


def update_password(user_id, raw_password):
    passwd = password.encode(raw_password)
    data.execute("UPDATE Passwords SET password = ? WHERE user_id = ?", passwd, user_id)


def set_user_groups(user_id, groups):
    with data.transaction():
        data.execute("DELETE FROM Group_users WHERE user_id = ?", user_id)
        for group in groups:
            add_user_to_group(user_id, group)


def add_user_to_group(user_id, group):
    with data.transaction():
        if group == "admin":
            add_user_to_group(user_id, "trusted")
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
@blueprint.route("/usermanager/logged_in", methods=["GET", "POST"])
def is_logged_in():
    logged_in = "logged_in" in session and session["logged_in"]
    if logged_in:
        with data.transaction():
            user = data.execute("SELECT * FROM Users WHERE user_id = ?", session["user_id"]).one()
            groups = data.execute("SELECT groupname FROM Groups INNER JOIN Group_users USING (group_id) WHERE user_id = ?", session["user_id"]).scalars()
            user.groups = groups
            user.is_admin = "admin" in groups
            user.is_trusted = "admin" in groups
    else:
        user = None
    return jsonify(logged_in=logged_in, user=user)

@blueprint.route("/usermanager/login", methods=["POST"])
def login():
    b = data.request()
    name = loginname(b.username)
    users = data.execute("SELECT user_id, username, password, deleted FROM Users INNER JOIN Passwords Using (user_id) WHERE loginname = ?", name)

    sleep(config.SLEEP_ATTEMPT)
    if empty(users) or not password.check(b.raw_password, users.one()["password"]):
        sleep(config.SLEEP_FAIL)
        abort("invalid username or password")

    user = users.one()
    if user.deleted:
        abort("user deleted")

    update_password(user.user_id, b.raw_password)

    authenticate(user.user_id, user.username)

    return is_logged_in()

@blueprint.route("/usermanager/logout", methods=["GET", "POST"])
def logout():
    unauthenticate()
    return success()

def authenticate(user_id, username):
    session["logged_in"] = True
    session["user_id"] = user_id
    session["username"] = username

def unauthenticate():
    session.clear()

### USERS ###
@blueprint.route("/usermanager/users")
@logged_in
def users():
    with data.transaction():
        users = data.execute("SELECT * FROM Users WHERE deleted = ?", false)
        deleted = data.execute("SELECT * FROM Users WHERE deleted = ?", true)
    return jsonify(users=users, deleted=deleted)

@blueprint.route("/usermanager/user", methods=["GET"])
@logged_in
def user():
    user_id = request.args.get("user_id", None)
    if user_id is None:
        abort("unspecified user")
    users = data.execute("SELECT * FROM Users WHERE user_id = ?", user_id).one(404, "No such user")

    #TODO: tour information and mentor information
    return users

@blueprint.route("usermanager/settings", methods=["POST"])
@logged_in
def settings():
    user_id = session["user_id"]
    b = data.request()
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
    current_password = data.execute("SELECT password FROM Passwords WHERE user_id = ?", user_id).scalar()
    b = data.request()
    if not password.check(b.current_password, current_password):
        logout()
        abort(304, "incorrect password")

    if b.new_password1 != b.new_password2:
        abort("unequal passwords")

    if not validate_password(b.new_password2):
        abort("illegal password")

    update_password(username, b.new1)
    return success()


@blueprint.route("/usermanager/password/forgot", methods=["POST"])
def forgot_password():
    #TODO: Should the current password be deleted in the database? or would that be anoying as other people could delete your password if they know your username."
    username = data.request().username
    if username is None:
        abort("unspecified username")
    user = data.execute("SELECT user_id, username, name, email, phone FROM Users WHERE loginname = ?",
                        loginname(username)).one(400, "No such user")

    if user.email is None:
        mail.forgot_password_no_email_adminmail.format(user).to_admins()
        abort("no email")

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

        b = data.request()

        if b.new_password1 != b.new_password2:
            abort("unequal passwords")

        if not validate_password(b.new_password1):
            abort("invalid password")

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
        b = data.request()
        if not validate_username(b.username):
            abort("invalid username")

        if b.new_password1 != b.new_password2:
            abort("unequal passwords")

        if not validate_password(b.new_password1):
            abort("invalid password")

        data.execute("DELETE FROM User_creation_keys WHERE key = ?", key)
        create_user(b.username, b.password1, b.name, b.email)

        login(b.user_id, b.username)
