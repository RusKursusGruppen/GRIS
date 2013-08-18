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

@front.route('/modify_news/<id>', methods=['GET', 'POST'])
@logged_in
def modify_news(id):
    news = data.execute("SELECT * FROM News WHERE n_id = ?", id)

    if empty(news) or session['username'] != news[0]['creator']:
        flash("You are not permitted to edit this newsitem")
        return redirect(url_front())
    news = news[0]

    if request.method == 'POST':
        if 'cancel' in request.form:
            return redirect(url_front())

        b = data.Bucket(request.form)
        if b.title == "":
            flash("Please enter a title")
            return html.back()
        b.text
        b >> ("UPDATE News $ WHERE  n_id = ?", id)
        return redirect(url_front())
    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("title", "Overskrift")
        w.textarea("text", "Tekst")

        form = w.create(news)
        return render_template('form.html', form=form)
