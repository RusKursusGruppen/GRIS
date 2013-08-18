# -*- coding: utf-8 -*-

import random, datetime

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, html
from lib.tools import logged_in

import pprint

schedule = Blueprint('schedule', __name__, template_folder = '../templates/schedule')
@schedule.route('/schedule')
@logged_in
def overview():
    with data.data() as db:
        cur = db.execute("SELECT s_id, title, closes FROM Schedule")
        events = cur.fetchall()
        cur.close()
        return render_template("schedule/overview.html",events=events)

@schedule.route('/schedule/new', methods=['GET','POST'])
@logged_in
def new():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash("Oprettelse annulleret")
            return redirect(url_for('schedule.overview'))

        s_id = data.execute_lastrowid(
            "INSERT INTO Schedule(title, description, created, closes) VALUES(?,?,?,?)",
             request.form['title'],
             request.form['description'],
             str(datetime.datetime.now()),
             request.form['deadline'])

        choices = [(s_id, x, 0) for x in request.form.getlist('choices') if x]
        flash(str(choices))
        cur2 = data.executemany(
            "INSERT INTO Schedule_cols(s_id, label, type, parent) VALUES (?,?,?, NULL)",
             choices)

        flash(u"Oprettelse gennemført")
        return redirect(url_for('schedule.overview'))
    else:
        deadline_calendar = html.calendar('schedule.deadline', 'yyyyMMdd', 'arrow', True, 24, False, 'future')
        time_calendar = html.calendar('schedule.time', 'yyyyMMdd', 'arrow', True, 24, False, 'future')

        return render_template("schedule/new.html", deadline_calendar=deadline_calendar, time_calendar=time_calendar)

@schedule.route('/schedule/<sid>', methods=['GET', 'POST'])
@logged_in
def event(sid):
    with data.data() as db:
        cur = db.execute("SELECT s_id, title, description, created, closes FROM Schedule WHERE s_id = ?", sid)
        event = cur.fetchone()
    return render_template("schedule/event.html", event=event)
