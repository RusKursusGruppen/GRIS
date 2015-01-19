# -*- coding: utf-8 -*-

from flask import Blueprint, request, session

from lib.tools import abort, logged_in, now, rkgyear

blueprint = Blueprint("mentorteams", __name__, url_prefix="/api")
from gris import data

@blueprint.route("/mentorteams")
@logged_in
def mentorteams():
    if "year" in request.values:
        year = request.values["year"]
        tours = data.execute("SELECT * FROM Mentor_teams WHERE year = ? ORDER BY mentor_team_name ASC", year)
    else:
        teams = data.execute("SELECT * FROM Mentor_teams ORDER BY year DESC, mentor_team_name ASC")
        teams = itertools.groupby(tours, key=get("year"))
    return teams

@blueprint.route("/mentorteams/mentorteam", methods=["GET", "POST"])
@logged_in
def mentorteam():
    mentor_id = request.values.get("mentor_id", None)
    with data.transaction():
        tour = data.execute("SELECT * FROM Mentor_teams WHERE mentor_id = ?", mentor_id)
        russer = data.execute("SELECT * FROM Russer WHERE mentor = ? ORDER BY name ASC", mentor_id)
        tutors = data.execute("SELECT * FROM Mentors WHERE mentor_id = ? ORDER BY username ASC", mentor_id)


@blueprint.route("/mentorteams/add", methods=["POST"])
@logged_in
def new():
    b = data.Bucket(request.form)
    b.type
    if b.mentor_team_name == "":
        b.mentor_team_name = "Unavngivet mentorhold"

    if "year" in b:
        b.year
    else:
        b.year = rkgyear()

    if "notes" in b:
        b.notes

    b >= "Mentor_teams"

@blueprint.route("/mentorteams/update", methods=["POST"])
@logged_in
def update():
    b = data.Bucket(request.form)

    if "mentor_team_name" in b:
        if b.mentor_team_name == "":
            b.mentor_team_name = "Unavngivet mentorhold"

    if "year" in b:
        b.year

    if "notes" in b:
        b.notes

    b >> ("UPDATE Mentor_teams $ WHERE mentor_id = ?", b["mentor_id"])

@blueprint.route("/mentorteams/delete", methods=["POST"])
@logged_in("rkg")
def delete():
    b = data.Bucket(request.form)
    if b.delete:
        with data.transaction():
            # TODO: delete dependencies?
            try:
                data.execute("DELETE FROM Mentor_teams WHERE mentor_id = ?", b.mentor_id)
            except:
                abort("Could not delete mentor team, there are people/items associated with it")


@blueprint.route("/mentorteams/mentors/add", methods=["POST"])
@logged_in
def add_mentor():
    b = data.Bucket(request.form)
    b.mentor_id
    b.user_id
    b >= "Mentors"

@blueprint.route("/mentorteams/mentors/remove", methods=["POST"])
@logged_in("rkg")
def remove_tutor():
    b = data.Bucket(request.form)
    data.execute("DELETE FROM Mentors WHERE mentor_id = ? and user_id = ?", b.mentor_id, b.user_id)
