# -*- coding: utf-8 -*-

import random, datetime, string, time, itertools, re

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, mail, html
from lib.tools import logged_in, empty, url_front, now, rkgyear, get

import config

mentorteams = Blueprint('mentorteams', __name__, template_folder = '../templates/mentorteams')

@mentorteams.route('/mentorteams')
@logged_in
def overview():
    teams = data.execute("SELECT * FROM Mentorteams LEFT JOIN Mentors USING (m_id) LEFT JOIN Users USING (username) ORDER BY year DESC, mentor_names ASC")
    teams = itertools.groupby(teams, key=get("year"))
    teams = [(x[0], [(y[0], list(y[1])) for y in itertools.groupby(x[1], key=get("m_id"))]) for x in teams]
    return render_template("mentorteams/overview.html", teams=teams)

@mentorteams.route('/mentorteams/team/<m_id>')
@logged_in('mentor')
def mentorteam(m_id):
    team = data.execute("SELECT * FROM Mentorteams WHERE m_id = ?", m_id)[0]
    russer = data.execute("SELECT * FROM Russer WHERE mentor = ?", m_id)
    mentors = data.execute("SELECT * FROM Mentors WHERE m_id = ?", m_id)
    return render_template("mentorteams/mentorteam.html", team=team, russer=russer, mentors=mentors)

@mentorteams.route('/mentorteams/new', methods=['GET', 'POST'])
@logged_in('mentor')
def new():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape("Mentorhold ikke oprettet"))
            return redirect(url_for('mentorteams.overview'))

        b = data.Bucket(request.form)
        if b.mentor_names == "":
            b.mentor_names = "Unavngivet mentorhold"
        if b.year.isdecimal():
            b.year = int(b.year)
        else:
            flash("Please enter a valid year")
            return html.back()
        b >= "Mentorteams"
        return redirect(url_for('mentorteams.overview'))

    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("mentor_names", "Navn", value="Unavngivet mentorhold")
        w.textfield("year", "År", value=rkgyear())
        form = w.create()
        return render_template("form.html", form=form)

@mentorteams.route('/mentorteams/team/<m_id>/settings', methods=['GET', 'POST'])
@logged_in('mentor')
def settings(m_id):
    if request.method == "POST":
        if 'cancel' in request.form:
            return redirect(url_front())

        b = data.Bucket(request.form)
        if b.mentor_names == "":
            b.mentor_names = "Unavngivet mentorhold"
        if b.year.isdecimal():
            b.year = int(b.year)
        else:
            flash("Please enter a valid year")
            return html.back()
        b >> ("UPDATE Mentorteams $ WHERE m_id = ?", m_id)

        mentors = request.form['mentors']
        mentors = mentors.replace('"', '')
        mentors = mentors.replace('&quot;', '')
        mentors = [name.split()[0] for name in re.split(';\s', mentors) if name != ""]

        old = data.execute("SELECT username FROM Mentors WHERE m_id = ?", m_id)
        old = [mentor['username'] for mentor in old]

        for mentor in set(old) - set(mentors):
            data.execute("DELETE FROM Mentors WHERE m_id = ? and username = ?", m_id, mentor)
        for mentor in sorted(set(mentors) - set(old)):
            data.execute("INSERT INTO Mentors(m_id, username) VALUES (?, ?)", m_id, mentor)

        return redirect(url_for('mentorteams.mentorteam', m_id=m_id))

    else:
        teams = data.execute("SELECT * FROM Mentorteams WHERE m_id = ?", m_id)
        if len(teams) != 1:
            flash(escape("Det hold findes ikke"))
            return redirect(url_for("mentorteams.overview"))
        team = teams[0]

        all_mentors = data.execute("SELECT * FROM Users WHERE username IN (Select username from Group_users where groupname = 'mentor')")
        all_mentors = ['\\"{0}\\" {1}'.format(mentor['username'], mentor['name']) for mentor in all_mentors]
        all_mentors.sort()

        actual_mentors = data.execute("SELECT * FROM Mentors INNER JOIN Users USING(username) WHERE m_id = ?", m_id)
        actual_mentors = ['&quot;{0}&quot; {1}; '.format(mentor['username'], mentor['name']) for mentor in actual_mentors]
        actual_mentors.sort()
        actual_mentors ="".join(actual_mentors)

        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("mentor_names", "Navn")
        w.textfield("year", "År")
        w.html(html.autocomplete_multiple(all_mentors, "mentors", default=actual_mentors), description="Mentorer", value="abekat")
        form = w.create(team)
        return render_template("mentorteams/settings.html", form=form)


@mentorteams.route('/mentorteams/team/<m_id>/delete', methods=['GET', 'POST'])
@logged_in('admin')
def delete(m_id):
    if request.method == "POST":
        if 'delete' in request.form:
            try:
                data.execute("DELETE FROM Mentorteams WHERE m_id = ?", m_id)
            except:
                flash("Could not delete team, there are people/items associated with it")
                return redirect(url_for('mentorteams.mentorteam', m_id=m_id))
            return redirect(url_for('mentorteams.overview'))
        else:
            flash(escape("Nothing deleted"))
            return redirect(url_for('mentorteams.mentorteam', m_id=m_id))

    else:
        teams = data.execute("SELECT * FROM Mentorteams WHERE m_id = ?", m_id)
        if len(teams) != 1:
            flash(escape("Det hold findes ikke"))
            return redirect(url_for("mentorteams.overview"))
        team = teams[0]

        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.html("Vil du slette holdet?")
        w.html('<button type="submit" name="delete" value="delete">Slet</button>', "Slet mentorhold?")
        form = w.create()
        return render_template("form.html", form=form)

@mentorteams.route('/mentorteams/team/<m_id>/add_to_rustour', methods=['GET', 'POST'])
@logged_in('mentor')
def add_to_rustour(m_id):
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape("Ingen ændringer"))
            return redirect(url_for('mentorteams.mentorteam', m_id=m_id))

        b = data.Bucket(request.form)

        russer = data.execute("SELECT r_id FROM Russer WHERE mentor = ?", m_id)
        russer = [(b.tour_name, rus['r_id']) for rus in russer]

        data.executemany("UPDATE Russer SET rustour = ? WHERE r_id = ?", russer)
        flash("Alle russer på mentorholdet er blevet sat på rustur".format(b.tour_name))
        return redirect(url_for("mentorteams.mentorteam", m_id=m_id))
    else:
        rustours = data.execute("SELECT * FROM Tours WHERE year = ?", rkgyear())
        rustours = [(tour['t_id'], tour['tour_name']) for tour in rustours]

        wb = html.WebBuilder()
        wb.form()
        wb.formtable()
        wb.select("tour_name", "Tildel rustur", rustours)
        form = wb.create()
        return render_template("form.html", form=form)
