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
    events = data.execute("SELECT s_id, title, closes FROM Schedule")
    return render_template("overview.html",events=events)

@schedule.route('/schedule/new', methods=['GET','POST'])
@logged_in
def new():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash("Oprettelse annulleret")
            return redirect(url_for('schedule.overview'))

        s_id = data.execute(
            "INSERT INTO Schedule(title, description, created, closes) VALUES(?,?,?,?) RETURNING s_id",
             request.form['title'],
             request.form['description'],
             str(datetime.datetime.now()),
             request.form['deadline'])[0][0]

        choices = [(s_id, x, 0) for x in request.form.getlist('choices') if x]
        flash(str(choices))
        data.executemany(
            "INSERT INTO Schedule_cols(s_id, label, type, parent) VALUES (?,?,?, NULL)",
            choices)

        flash("Oprettelse gennemført")
        return redirect(url_for('schedule.overview'))
    else:
        deadline_calendar = html.calendar('schedule.deadline', 'yyyyMMdd', 'arrow', True, 24, False, 'future')
        time_calendar = html.calendar('schedule.time', 'yyyyMMdd', 'arrow', True, 24, False, 'future')

        return render_template("new.html", deadline_calendar=deadline_calendar, time_calendar=time_calendar)

@schedule.route('/schedule/<sid>', methods=['GET', 'POST'])
@logged_in
def event(sid):
    event = data.execute("SELECT s_id, title, description, created, closes FROM Schedule WHERE s_id = ?", sid)
    return render_template("event.html", event=event)
