# -*- coding: utf-8 -*-

import datetime, string, time, subprocess, itertools
import psycopg2

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, mail, html
from lib.tools import logged_in, empty, url_front, get

from applications import usermanager

import config




admin = Blueprint('admin', __name__, template_folder = '../templates/admin')

@admin.route('/admin', methods=['GET', 'POST'])
@logged_in('admin')
def overview():
    #adminrights
    return render_template("admin/admin.html")

@admin.route('/admin/git_pull', methods=["GET", "POST"])
@logged_in('admin')
def git_pull():
    if request.method == "POST":
        response = subprocess.check_output(["git", "pull"])
        #response = subprocess.check_output(["ls", "-l"])
    else:
        response = ""
    return render_template("admin/git_pull.html",response=response)

@admin.route('/admin/delete_user', methods=["GET", "POST"])
@logged_in('admin')
def delete_user():
#    return render_template("admin/delete_user.html")
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape("Ændringer anulleret"))
            return redirect(url_for('admin.overview'))

        b = data.Bucket(request.form)
        b.deleted = True
        b >> ("UPDATE Users SET $ WHERE username = ?", request.form["user"])

        data.execute("DELETE FROM Group_users WHERE username = ?", request.form["user"])

        flash("Bruger slettet")

        return redirect(url_for('admin.delete_user'))

    else:
        users = data.execute("SELECT * FROM Users WHERE deleted = ?", False)
        users = [(user['username'], "{0}: {1}".format(user['username'], user['name'])) for user in users]

        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.select("user", "Brugere:", users)
        form = w.create()

        return render_template("admin/delete_user.html", form=form)

@admin.route('/admin/groups/overview')
@logged_in('admin')
def groups_overview():
    groups = data.execute('SELECT * FROM Group_users INNER JOIN Users USING (username) ORDER BY groupname, username')
    groups = itertools.groupby(groups, key=get('groupname'))
    groups = [(x[0], list(x[1])) for x in groups]

    all_groups = data.execute("SELECT groupname FROM Groups ORDER BY groupname")
    all_groups = [group['groupname'] for group in all_groups]

    result = []
    for group in all_groups:
        if len(groups) > 0 and groups[0][0] == group:
            result.append(groups.pop(0))
        else:
            result.append((group, []))
    groups = result

    return render_template("admin/group_overview.html", groups=groups)

@admin.route('/admin/groups/<groupname>', methods=["GET", "POST"])
@logged_in('admin')
def group(groupname):
    if request.method == "POST":
        if 'cancel' in request.form:
            flash("Ændringer anulleret")
            return redirect(url_for('admin.groups_overview'))

        users = data.execute('SELECT username FROM Users WHERE deleted = ?', False)


        for user in users:
            username = user['username']
            try:
                if username in request.form:
                    usermanager.group_add_user(groupname, username)
                else:
                    usermanager.group_remove_user(groupname, username)
            except psycopg2.IntegrityError as e:
                pass
        return redirect(url_for('admin.groups_overview'))
    else:
        users = data.execute('SELECT username, name FROM Users WHERE deleted = ? ORDER BY name ASC', False)
        group = data.execute('SELECT username FROM Group_users WHERE groupname = ?', groupname)
        group = set(user['username'] for user in group)


        usernames = (user['username'] for user in users)
        kv = {user:(user in group) for user in usernames}

        w = html.WebBuilder()
        w.form()
        w.formtable()
        for user in users:
            w.checkbox(user['username'], '"{0}" {1}'.format(user['username'], user['name']))
        form = w.create(kv)
        return render_template("form.html", form=form)

@admin.route('/admin/invitations')
def invitations():
    usermanager.delete_old_keys()
    emails = data.execute("SELECT email FROM User_creation_keys ORDER BY email ASC")
    emails = [x['email'] for x in emails if x['email'] is not None]
    return render_template("admin/invitations.html", invitations=emails)

@admin.route('/admin/quit')
def quit():
    import sys
    sys.exit()
