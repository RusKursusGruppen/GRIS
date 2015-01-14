# -*- coding: utf-8 -*-

import random, string, time

from flask import Blueprint, jsonify, request
from lib.tools import abort, now


blueprint = Blueprint("usermanager", __name__, url_prefix="/api")


@blueprint.route("/usermanager/login", methods=['POST'])
def login():
    b = data.Bucket(request.form)
    loginname = loginname(b.username)
    users = data.execute("SELECT user_id, username, password, deleted FROM Users WHERE loginname = ?", loginname)

    sleep(config.SLEEP_ATTEMPT)
    if empty(users) or not password.check(b.raw_password, users.one()["password"]):
        sleep(config.SLEEP_FAIL)
        abort(400, "Invalid username or password")

    user = users.one()
    if user.deleted:
        abort(400, "Sorry, your user has been deleted")

    session["logged_in"] = True
    session["user_id"] = user["user_id"]
    session["username"] = user["username"]

    password.update_password(user["user_id"], b.raw_password)
    return True


def create_user(username, raw_password, name="", email="", groups=[]):
    b = data.Bucket()
    b.username = username
    b.loginname = loginname(username)
    b.password = password.encode(raw_password)
    b.name = name
    b.email = email
    user = (b >= "Users")
    set_user_groups(user["user_id"], groups)

    mail.new_user_adminmail.format(b).to_admins()

def set_user_groups(user_id, group):
    pass

def update_password(user_id, raw_password):
    passwd = password.encode(raw_password)
    data.execute("UPDATE Users SET password = ? WHERE user_id = ?", passwd, user_id)

def loginname(username):
    return username.lower()

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
            if e.pgerror.startswith('ERROR:  duplicate key value violates unique constraint "user_forgotten_password_keys_pkey"'):
                continue
            else:
                raise

### PASSWORD RENEWAL ###
def forgot_password(username):
    #TODO: Should the current password be deleted in the database? or would that be anoying as other people could delete your password if they know your username."

    user = data.execute("SELECT user_id, username, name, email, phone FROM Users WHERE loginname = ?",
                        loginname(username)).one(400, "No such user")

    if user["email"] is None:
        mail.forgot_password_no_email_adminmail.format(user).to_admins()
        abort("User has no email, please contact an admin.")

    already_forgotten = data.execute("SELECT count(*) FROM User_forgotten_password_keys WHERE user_id = ?", user["user_id"]).scalar()
    if already_forgotten > 0:
        mail.forgot_password_multiple_adminmail.format(username=username, times=already_forgotten).to_admins()

    b = data.Bucket()
    b.username = user["username"]
    b.created = now()
    key = generate_key(b, "User_forgotten_password_keys")
    # url = config.URL + url_for("???", key=key)
    url = config.URL + "/TODO-find-out-how-to-set-up-link/" + key #TODO: find out where to link to
    failed = mail.forgot_password.format(name=user["name"], url=url).send(user["email"])
    if len(failed) == 0:
        mail.forgot_password_no_email_adminmail.format(user).to_admins()

### USER INVITATION ###
def invite(emails):
    failed = []
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
