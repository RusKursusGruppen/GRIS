# -*- coding: utf-8 -*-

import sqlite3
import random
from functools import wraps
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password
from lib.tools import logged_in
import datetime

textfields = [ 'name',
               'filled_by',
               'co',
               'address',
               'zipcode',
               'city',
               'move_time',
               'new_address',
               'new_zipcode',
               'new_city',
               'phone',
               'email',
               'vacation',
               'priority',
               'gymnasium',
               'since_gymnasium',
               'code_experience',
               'special_needs',
               'plays_instrument',
               'other',]

rusmanager = Blueprint('rusmanager', __name__, template_folder = '../templates/rusmanager')
@rusmanager.route('/rusmanager')
@logged_in
def overview():
    #TODO: use "with data.data() as db:"
    db = data.data()
    cur = db.execute("select rid, name from Russer")
    russer = cur.fetchall()
    db.close()
    # russer = [{'name':"A", 'rid':-1},{'name':"B", 'rid':-2}]
    return render_template("rusmanager/overview.html", russer=russer)

@rusmanager.route('/rusmanager/<rid>', methods=['GET', 'POST'])
@logged_in
def rus(rid):
    #form = RusForm(request.form)
    if request.method == "POST":# and form.validate():
        checkboxes = [
            'called',
            'uniday',
            'campus',
            'tour',
        ]
        'rustour'
        'dutyteam'

        if 'cancel' in request.form:
            flash(escape(u"Ændringer anulleret"))
            return redirect(url_for('rusmanager.overview'))

        print(request.form)
        with data.data() as db:
            for field in textfields:
                #SQL injection safe:
                sql = "UPDATE Russer SET {0} = ? WHERE rid == ?;".format(field)
                cur = db.execute(sql, (request.form[field], rid))

            for field in checkboxes:
                #SQL injection safe:
                val = 1 if field in request.form else 0
                sql = "UPDATE Russer SET {0} = ? WHERE rid == ?;".format(field)
                cur = db.execute(sql, (val, rid))

            sql = "UPDATE Russer SET birthday = ? WHERE rid == ?;"
            cur = db.execute(sql, (request.form['birthday'], rid))


        flash("Rus opdateret")
        return redirect(url_for('rusmanager.overview'))
    else:
        with data.data() as db:
            cur = db.execute("SELECT * FROM Russer WHERE rid == ?", (rid,))
            rus = cur.fetchone()

            if not rus:
                return "Den rus findes ikke din spasser!"

            rus = {k:v if v != None else "" for k,v in zip(rus.keys(), rus)}
            return render_template("rusmanager/rus.html", rus=rus)

@rusmanager.route('/rusmanager/new', methods=['GET', 'POST'])
@logged_in
def new():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape(u"Rus IKKE tilføjet"))
            return redirect(url_for('rusmanager.overview'))

        with data.data() as db:
            cur = db.cursor()
            name = " ".join([x.capitalize() for x in request.form['name'].split()])
            cur = cur.execute("INSERT INTO Russer(name, called) VALUES(?,?)", (name,0))
            rus = cur.fetchone()
            flash("Rus oprettet")
            return redirect(url_for('rusmanager.rus', rid=str(cur.lastrowid)))
    else:
        return render_template("rusmanager/new.html")
