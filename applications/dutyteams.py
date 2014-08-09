# -*- coding: utf-8 -*-

import random, datetime, string, time, itertools, re

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, mail, html
from lib.tools import logged_in, empty, url_front, now, rkgyear

import config

dutyteams = Blueprint('dutyteams', __name__, template_folder = '../templates/dutyteams')

@dutyteams.route('/dutyteams')
def overview():
    dutys = data.execute("SELECT * FROM Dutyteams ORDER BY tj_id DESC")
    dutys = itertools.groupby(dutys, key=lambda duty: duty['tj_id'])
    return render_template("dutyteams/overview.html", dutys=dutys)

# @rustours.route('/rustours/tour/<t_id>')
# def rustour(t_id):
#     tour = data.execute("SELECT * FROM Tours WHERE t_id = ?", t_id)[0]
#     russer = data.execute("SELECT * FROM Russer WHERE rustour = ?", t_id)
#     tutors = data.execute("SELECT * FROM tours_tutors WHERE t_id = ?", t_id)
#     dutyteams = data.execute("SELECT * FROM Dutyteams WHERE t_id = ?", t_id)
#     return render_template("rustours/rustour.html", tour=tour, russer=russer, tutors=tutors, dutyteams=dutyteams)

@dutyteams.route('/dutyteams/new', methods=['GET', 'POST'])
def new():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape("Tjansehold ikke oprettet"))
            return redirect(url_for('dutyteams.overview'))

        b = data.Bucket(request.form)
        if b.name == "":
            b.name = "Unavngivet tjansehold"
        b >= "Dutyteams"
        return redirect(url_for('dutyteams.overview'))

    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("name", "Navn", value="Unavngivet tjansehold")
        form = w.create()
        return render_template("form.html", form=form)

# @rustours.route('/rustours/tour/<t_id>/settings', methods=['GET', 'POST'])
# def settings(t_id):
#     if request.method == "POST":
#         if 'cancel' in request.form:
#             return redirect(url_front())

#         b = data.Bucket(request.form)
#         b.theme
#         b.type
#         if b.tour_name == "":
#             b.tour_name = "Unavngiven rustur"
#         if b.year.isdecimal():
#             b.year = int(b.year)
#         else:
#             flash("Please enter a valid year")
#             return html.back()
#         b >> ("UPDATE Tours $ WHERE t_id = ?", t_id)

#         tutors = request.form['tutors']
#         tutors = tutors.replace('"', '')
#         tutors = tutors.replace('&quot;', '')
#         tutors = [name.split()[0] for name in re.split(';\s', tutors) if name != ""]

#         old = data.execute("SELECT username FROM Tours_tutors WHERE t_id = ?", t_id)
#         old = [tutor['username'] for tutor in old]

#         for tutor in set(old) - set(tutors):
#             data.execute("DELETE FROM Tours_tutors WHERE t_id = ? and username = ?", t_id, tutor)
#         for tutor in sorted(set(tutors) - set(old)):
#             data.execute("INSERT INTO Tours_tutors(t_id, username) VALUES (?, ?)", t_id, tutor)

#         return redirect(url_for('rustours.rustour', t_id=t_id))

#     else:
#         tours = data.execute("SELECT * FROM Tours WHERE t_id = ?", t_id)
#         if len(tours) != 1:
#             flash(escape("Den tur findes ikke"))
#             return redirect(url_for("rustours.overview"))
#         tour = tours[0]

#         all_tutors = data.execute("SELECT * FROM Users WHERE username IN (Select username from User_groups where groupname = 'rkg')")
#         all_tutors = ['\\"{0}\\" {1}'.format(tutor['username'], tutor['name']) for tutor in all_tutors]
#         all_tutors.sort()

#         actual_tutors = data.execute("SELECT * FROM Tours_tutors INNER JOIN Users USING(username) WHERE t_id = ?", t_id)
#         actual_tutors = ['&quot;{0}&quot; {1}; '.format(tutor['username'], tutor['name']) for tutor in actual_tutors]
#         actual_tutors.sort()
#         actual_tutors = "".join(actual_tutors)

#         w = html.WebBuilder()
#         w.form()
#         w.formtable()
#         w.textfield("tour_name", "Navn")
#         w.textfield("theme", "Tema")
#         w.textfield("year", "År")
#         w.select("type", "Type", [('p', 'Pigetur'), ('t', 'Transetur'), ('m', 'Munketur')])
#         w.html(html.autocomplete_multiple(all_tutors, "tutors", default=actual_tutors), description="Vejledere", value="abekat")
#         form = w.create(tour)
#         return render_template("settings.html", form=form, t_id=t_id)

# @rustours.route('/rustours/tour/<t_id>/delete', methods=['GET', 'POST'])
# def delete(t_id):
#     if request.method == "POST":
#         if 'delete' in request.form:
#             try:
#                 data.execute("DELETE FROM Tours WHERE t_id = ?", t_id)
#             except:
#                 flash("Could not delete tour, there are people/items associated with it")
#                 return redirect(url_for('rustours.rustour', t_id=t_id))
#             return redirect(url_for('rustours.overview'))
#         else:
#             flash(escape("Nothing deleted"))
#             return redirect(url_for('rustours.rustour', t_id=t_id))

#     else:
#         tours = data.execute("SELECT * FROM Tours WHERE t_id = ?", t_id)
#         if len(tours) != 1:
#             flash(escape("Den tur findes ikke"))
#             return redirect(url_for("rustours.overview"))
#         tour = tours[0]

#         w = html.WebBuilder()
#         w.form()
#         w.formtable()
#         w.html("Vil du slette rusturen?")
#         w.html('<button type="submit" name="delete" value="delete">Slet rustur</button>', "Slet rustur?")
#         form = w.create()
#         return render_template('form.html', form=form)

