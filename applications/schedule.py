# -*- coding: utf-8 -*-
import sqlite3
import random
from functools import wraps
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint


from lib import data, password
from lib.tools import logged_in
import datetime

schedule = Blueprint('schedule', __name__, template_folder = '../templates/schedule')
@schedule.route('/schedule')
def overview():
    with data.data() as db:
        cur = db.execute("SELECT s_id, title, closes FROM Schedule")
        events = cur.fetchall()
        cur.close()
        return render_template("schedule.overview.html",events=events)

@schedule.route('/schedule/new', methods=['GET','POST'])
def new():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash("Oprettelse annulleret")
            return redirect(url_for('schedule.overview'))
        with data.data() as db:
            cur = db.execute(
                "INSERT INTO Schedule(title, description, created, closes) VALUES(?,?,?,?)", (
                request.form['title'],
                request.form['description'],
                str(datetime.datetime.now()),
                request.form['deadline']))
            flash(u"Oprettelse gennemført")
            return redirect(url_for('schedule.overview'))
    else:
        return render_template("schedule.new.html")

@schedule.route('/schedule/<sid>', methods=['GET', 'POST'])
def event(sid):
    with data.data() as db:
        cur = db.execute("SELECT s_id, title, description, created, closes FROM Schedule WHERE s_id = ?", sid)
        event = cur.fetchone()
    return render_template("schedule.event.html", event=event)
