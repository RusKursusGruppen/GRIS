# -*- coding: utf-8 -*-

import datetime, string, time, subprocess, itertools

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, mail, html
from lib.tools import logged_in, empty, url_front, get

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
        b.deleted = 1
        b >> ("UPDATE Users SET $ WHERE username = ?", request.form["user"])

        data.execute("DELETE FROM User_groups WHERE username = ?", request.form["user"])

        flash("Bruger slettet")

        return redirect(url_for('admin.delete_user'))

    else:
        users = data.execute("SELECT * FROM Users WHERE deleted = 0")
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
    groups = data.execute('SELECT * FROM User_groups ORDER BY groupname, username')
    groups = itertools.groupby(groups, key=get('groupname'))
    return render_template("group_overview.html", groups=groups)
