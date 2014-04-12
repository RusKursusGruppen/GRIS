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
    groups = data.execute("SELECT * FROM Groups ORDER BY groupname DESC")

    if request.method == 'POST':
        if 'cancel' in request.form:
            return redirect(url_front())
        creator = session['username']
        created = now()
        title = request.form['title']
        currentgroup = request.form['group']

        get_flashed_messages()
        if title == "":
            flash("Please enter a title")
            return html.back()

        text = request.form['text']
        data.execute("INSERT INTO News(creator, created, title, text) VALUES(?,?,?,?)", creator, created, title, text)

        data.execute("INSERT INTO News_access(n_id, groupname) VALUES((SELECT n_id FROM News WHERE created = ?), (SELECT groupname FROM Groups WHERE groupname = ?))", str(created), currentgroup)
        return redirect(url_front())
    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("title", "Overskrift")

        # Get all groupnames from database
        groupnames = ""
        for group in groups:
            groupnames = groupnames + '<option value="{0}">{0}</option>y'.format(group[0])

        w.html('<select name="group" id="group">' + groupnames +'<\select>')
        w.html('')
        w.textarea("text", "Tekst")

        form = w.create()
        return render_template('form.html', form=form)

@front.route('/modify_news/<id>', methods=['GET', 'POST'])
@logged_in
def modify_news(id):
    groups = data.execute("SELECT * FROM Groups ORDER BY groupname DESC")
    news = data.execute("SELECT * FROM News WHERE n_id = ?", id)
    currentgroup = data.execute("SELECT groupname, n_id FROM news_access")

    displaygroup = "ingen"
    i = 0
    while i < len(currentgroup):
        print(currentgroup[i][1])
        print(id)
        if id == str(currentgroup[i][1]):
           displaygroup = currentgroup[i][0]
        i += 1

    if empty(news) or session['username'] != news[0]['creator']:
        flash("You are not permitted to edit this newsitem")
        return redirect(url_front())
    news = news[0]

    if request.method == 'POST':
        if 'cancel' in request.form:
            return redirect(url_front())

        changegroup = request.form['group']
        data.execute("DELETE FROM News_access WHERE n_id = ?", id)
        data.execute("INSERT INTO News_access (n_id, groupname) VALUES((SELECT n_id FROM news WHERE n_id = ?),(SELECT groupname FROM groups where groupname = ?))", id, changegroup)

        b = data.Bucket(request.form)

        if 'delete' in request.form:
            b >> ("DELETE FROM News WHERE  n_id = ?", id)

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

        # Get all groupnames from database
        groupnames = ""
        for group in groups:
            groupnames = groupnames + '<option value="{0}">{0}</option>y'.format(group[0])

        w.html('<select name="group" id="group">' + groupnames +'<\select>')
        w.html(displaygroup)
        w.html('<button type="submit" name="delete" value="delete">Slet nyhed</button>', "")
        w.textarea("text", "Tekst")
        w.html('<button type="submit" name="delete" value="delete">Slet nyhed</button>', "")

        form = w.create(news)
        return render_template('form.html', form=form)
