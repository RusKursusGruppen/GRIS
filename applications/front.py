# -*- coding: utf-8 -*-

import datetime, string, time

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, mail, html
from lib.tools import logged_in, empty, now, url_front

import config

front = Blueprint('front', __name__, template_folder = '../templates/front')

@front.route('/')
@logged_in
def frontpage():
    rkg      = session['rkg']
    vejleder = session['tutor']
    mentor   = session['mentor']
    news = data.execute("SELECT * FROM News ORDER BY created DESC")# WHERE for_tutors = ? OR for_mentors = ?", tutor, mentor)
    return render_template("front/frontpage.html", news=news)

@front.route('/add_news', methods=['GET', 'POST'])
@logged_in
def add_news():
    if request.method == 'POST':
        if 'cancel' in request.form:
            return redirect(url_front())
        creator = session['username']
        created = now()
        title = request.form['title']

        get_flashed_messages()
        if title == "":
            flash("Please enter a title")
            return html.back()

        text = request.form['text']
        data.execute("INSERT INTO News(creator, created, title, text) VALUES(?,?,?,?)", creator, created, title, text)
        return redirect(url_front())
    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("title", "Overskrift")
        w.textarea("text", "Tekst")

        form = w.create()
        return render_template('form.html', form=form)
