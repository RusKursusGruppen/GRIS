# -*- coding: utf-8 -*-

import random, datetime, string, time, itertools, re

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, mail, html
from lib.tools import logged_in, empty, url_front, now, rkgyear, get

import config

rustours = Blueprint('rustours', __name__, template_folder = '../templates/rustours')

@rustours.route('/rustours')
@logged_in
def overview():
    tours = data.execute("SELECT * FROM Tours ORDER BY year DESC")
    tours = itertools.groupby(tours, key=get("year"))
    return render_template("rustours/overview.html", tours=tours)

@rustours.route('/rustours/tour/<t_id>')
@logged_in('rkg')
def rustour(t_id):
    tour = data.execute("SELECT * FROM Tours WHERE t_id = ?", t_id)[0]
    russer = data.execute("SELECT * FROM Russer WHERE rustour = ? ORDER BY name ASC", t_id)
    tutors = data.execute("SELECT * FROM tours_tutors WHERE t_id = ?", t_id)

    dutyteams = data.execute("SELECT Russer.r_id, Russer.name, Dutyteams.name as dutyteam FROM Russer FULL OUTER JOIN Dutyteams ON Russer.dutyteam = Dutyteams.d_id WHERE Russer.rustour = ? and Russer.dutyteam IS NOT NULL ORDER BY Dutyteams.d_id ASC", t_id)
    dutyteams = itertools.groupby(dutyteams, key=get("dutyteam"))
    dutyteams = [(x[0], list(x[1])) for x in dutyteams]

    all_teams = data.execute("SELECT name FROM Dutyteams WHERE t_id = ? ORDER BY d_id ASC", t_id)
    all_teams = [x['name'] for x in all_teams]

    result = []
    for team in all_teams:
        if len(dutyteams) > 0 and dutyteams[0][0] == team:
            result.append(dutyteams.pop(0))
        else:
            result.append((team, []))
    dutyteams = result

    unassigned = data.execute("SELECT r_id, name FROM Russer WHERE rustour = ? AND dutyteam IS NULL ORDER BY name DESC", t_id)

    return render_template("rustours/rustour.html", tour=tour, russer=russer, tutors=tutors, dutyteams=dutyteams, unassigned=unassigned)

@rustours.route('/rustours/new', methods=['GET', 'POST'])
@logged_in('rkg')
def new():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape("Rustur ikke oprettet"))
            return redirect(url_for('rustours.overview'))

        b = data.Bucket(request.form)
        b.type
        if b.tour_name == "":
            b.tour_name = "Unavngiven rustur"
        if b.year.isdecimal():
            b.year = int(b.year)
        else:
            flash("Please enter a valid year")
            return html.back()
        b >= "Tours"
        return redirect(url_for('rustours.overview'))

    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("tour_name", "Navn", value="Unavngiven rustur")
        w.textfield("year", "År", value=rkgyear())
        w.select("type", "Type", [('p', 'Pigetur'), ('t', 'Transetur'), ('m', 'Munketur')])
        form = w.create()
        return render_template("form.html", form=form)

@rustours.route('/rustours/tour/<t_id>/settings', methods=['GET', 'POST'])
@logged_in('rkg')
def settings(t_id):
    if request.method == "POST":
        if 'cancel' in request.form:
            return redirect(url_front())

        b = data.Bucket(request.form)
        b.theme
        b.type
        b.notes
        if b.tour_name == "":
            b.tour_name = "Unavngiven rustur"
        if b.year.isdecimal():
            b.year = int(b.year)
        else:
            flash("Please enter a valid year")
            return html.back()
        b >> ("UPDATE Tours $ WHERE t_id = ?", t_id)

        tutors = request.form['tutors']
        tutors = tutors.replace('"', '')
        tutors = tutors.replace('&quot;', '')
        tutors = [name.split()[0] for name in re.split(';\s', tutors) if name != ""]

        old = data.execute("SELECT username FROM Tours_tutors WHERE t_id = ?", t_id)
        old = [tutor['username'] for tutor in old]

        for tutor in set(old) - set(tutors):
            data.execute("DELETE FROM Tours_tutors WHERE t_id = ? and username = ?", t_id, tutor)
        for tutor in sorted(set(tutors) - set(old)):
            data.execute("INSERT INTO Tours_tutors(t_id, username) VALUES (?, ?)", t_id, tutor)

        return redirect(url_for('rustours.rustour', t_id=t_id))

    else:
        tours = data.execute("SELECT * FROM Tours WHERE t_id = ?", t_id)
        if len(tours) != 1:
            flash(escape("Den tur findes ikke"))
            return redirect(url_for("rustours.overview"))
        tour = tours[0]

        all_tutors = data.execute("SELECT * FROM Users WHERE username IN (Select username from Group_users where groupname = 'rkg')")
        all_tutors = ['\\"{0}\\" {1}'.format(tutor['username'], tutor['name']) for tutor in all_tutors]
        all_tutors.sort()

        actual_tutors = data.execute("SELECT * FROM Tours_tutors INNER JOIN Users USING(username) WHERE t_id = ?", t_id)
        actual_tutors = ['&quot;{0}&quot; {1}; '.format(tutor['username'], tutor['name']) for tutor in actual_tutors]
        actual_tutors.sort()
        actual_tutors = "".join(actual_tutors)

        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("tour_name", "Navn")
        w.textfield("theme", "Tema")
        w.textfield("year", "År")
        w.select("type", "Type", [('p', 'Pigetur'), ('t', 'Transetur'), ('m', 'Munketur')])
        w.html(html.autocomplete_multiple(all_tutors, "tutors", default=actual_tutors), description="Vejledere", value="abekat")
        w.textarea("notes", "Noter")
        form = w.create(tour)
        return render_template("rustours/settings.html", form=form, t_id=t_id)

@rustours.route('/rustours/tour/<t_id>/delete', methods=['GET', 'POST'])
@logged_in('rkg')
def delete(t_id):
    if request.method == "POST":
        if 'delete' in request.form:
            try:
                data.execute("DELETE FROM Tours WHERE t_id = ?", t_id)
            except:
                flash("Could not delete tour, there are people/items associated with it")
                return redirect(url_for('rustours.rustour', t_id=t_id))
            return redirect(url_for('rustours.overview'))
        else:
            flash(escape("Nothing deleted"))
            return redirect(url_for('rustours.rustour', t_id=t_id))

    else:
        tours = data.execute("SELECT * FROM Tours WHERE t_id = ?", t_id)
        if len(tours) != 1:
            flash(escape("Den tur findes ikke"))
            return redirect(url_for("rustours.overview"))
        tour = tours[0]

        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.html("Vil du slette rusturen?")
        w.html('<button type="submit" name="delete" value="delete">Slet rustur</button>', "Slet rustur?")
        form = w.create()
        return render_template("form.html", form=form)

@rustours.route('/rustours/tour/<t_id>/dutyteams', methods=['GET', 'POST'])
@logged_in('admin')
def dutyteams(t_id):
    if request.method == "POST":
        if 'cancel' in request.form:
            return redirect(url_for('rustours.rustour', t_id=t_id))

        if request.form['new'] != "":
            b = data.Bucket()
            b.name = request.form['new']
            b.t_id = t_id
            b >= "Dutyteams"

        dutyteams = data.execute("SELECT d_id FROM Dutyteams WHERE t_id = ?", t_id)
        dutyteams = set(str(dutyteam['d_id']) for dutyteam in dutyteams)

        for d_id in request.form.keys():

            if d_id in dutyteams:
                b = data.Bucket()
                b.name = request.form[d_id]
                b >> ("UPDATE Dutyteams $ WHERE t_id = ? AND d_id = ?", t_id, d_id)

        return redirect(url_for("rustours.rustour", t_id=t_id))

    else:
        dutyteams = data.execute("SELECT * FROM Dutyteams WHERE t_id = ? ORDER BY d_id ASC", t_id)

        w = html.WebBuilder()
        w.form()
        w.formtable()
        for dutyteam in dutyteams:
            w.textfield(dutyteam['d_id'], "Omdøb:", value=dutyteam['name'])
        w.textfield("new", "Nyt tjansehold:")
        form = w.create()
        return render_template("form.html", form=form)
