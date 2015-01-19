# -*- coding: utf-8 -*-

from flask import Blueprint, request, session

from lib.tools import abort, logged_in, now, rkgyear

blueprint = Blueprint("rustours", __name__, url_prefix="/api")
from gris import data

@blueprint.route("/rustours")
@logged_in
def rustours():
    if "year" in request.values:
        year = request.values["year"]
        tours = data.execute("SELECT * FROM Tours WHERE year = ? ORDER BY tour_name ASC", year)
    else:
        tours = data.execute("SELECT * FROM Tours ORDER BY year DESC, tour_name ASC")
        tours = itertools.groupby(tours, key=get("year"))
    return tours

@blueprint.route("/rustours/tour", methods=["GET", "POST"])
@logged_in
def rustour():
    tour_id = request.values.get("tour_id", None)
    with data.transaction():
        tour = data.execute("SELECT * FROM Tours WHERE tour_id = ?", tour_id)
        russer = data.execute("SELECT * FROM Russer WHERE rustour = ? ORDER BY name ASC", tour_id)
        tutors = data.execute("SELECT * FROM tours_tutors WHERE tour_id = ? ORDER BY username ASC", tour_id)

        teams = data.execute("SELECT * FROM Team_categories LEFT OUTER JOIN Teams WHERE tour_id = ?", tour_id)
        #TODO: left join on teams members
        #TODO: also find russer not assigned to a team for each category
    #TODO: show something about teams

@blueprint.route("/rustours/new", methods=["POST"])
@logged_in("rkg")
def new():
    b = data.Bucket(request.form)
    b.type
    if b.tour_name == "":
        b.tour_name = "Unavngiven rustur"

    if "year" in b:
        b.year
    else:
        b.year = rkgyear()

    if "theme" in b:
        b.theme

    if "notes" in b:
        b.notes

    b >= "Tours"


@blueprint.route("/rustours/update", methods=["POST"])
@logged_in("rkg")
def update():
    b = data.Bucket(request.form)

    if "tour_name" in b:
        if b.tour_name == "":
            b.tour_name = "Unavngiven rustur"

    if "theme" in b:
        b.theme

    if "type" in b:
        b.type

    if "year" in b:
        b.year

    if "notes" in b:
        b.notes

    b >> ("UPDATE Tours $ WHERE tour_id = ?", b["tour_id"])


@blueprint.route("/rustours/delete", methods=["POST"])
@logged_in("rkg")
def delete():
    b = data.Bucket(request.form)
    if b.delete:
        try:
            # TODO: delete dependencies?
            data.execute("DELETE FROM Tours WHERE tour_id = ?", b.tour_id)
        except:
            abort("Could not delete tour, there are people/items associated with it")


@blueprint.route("/rustours/tutors/add", methods=["POST"])
@logged_in("rkg")
def add_tutor():
    b = data.Bucket(request.form)
    b.tour_id
    b.user_id
    b >= "Tours_tutors"

@blueprint.route("/rustours/tutors/remove", methods=["POST"])
@logged_in("rkg")
def remove_tutor():
    b = data.Bucket(request.form)
    data.execute("DELETE FROM Tours_tutors WHERE tour_id = ? and user_id = ?", b.tour_id, b.user_id)



### TEAMS ###
@blueprint.route("/rustours/teams/category/add", methods=["POST"])
@logged_in("rkg")
def add_team_category():
    b = data.Bucket(request.form)
    b.tour_id
    b.category
    b >= "Team_categories"

@blueprint.route("/rustours/teams/category/update", methods=["POST"])
@logged_in("rkg")
def update_team_category():
    b = data.Bucket(request.form)
    b.category
    b >> ("UPDATE Team_categories $ WHERE tour_id = ?", b["tour_id"])

@blueprint.route("/rustours/teams/category/delete", methods=["POST"])
@logged_in("rkg")
def delete_team_category():
    b = data.Bucket(request.form)
    data.execute("DELETE FROM Team_categories WHERE team_category_id = ?", b.team_category_id)


@blueprint.route("/rustours/teams/add", methods=["POST"])
@logged_in("rkg")
def add_team():
    b = data.Bucket(request.form)
    b.team_category_id
    b.team_name
    b >= "Teams"

@blueprint.route("/rustours/teams/update", methods=["POST"])
@logged_in("rkg")
def update_team():
    b = data.Bucket(request.form)
    b.team_name
    b >> ("UPDATE Teams $ WHERE team_id = ?", b["team_id"])

@blueprint.route("/rustours/teams/delete", methods=["POST"])
@logged_in("rkg")
def delete_team():
    b = data.Bucket(request.form)
    data.execute("DELETE FROM Teams WHERE team_id = ?", b.team_id)


@blueprint.route("/rustours/teams/members/add", methods=["POST"])
@logged_in("rkg")
def add_team_member():
    b = data.Bucket(request.form)
    b.team_id
    b.rus_id
    b >= "Team_members"

@blueprint.route("/rustours/teams/members/remove", methods=["POST"])
@logged_in("rkg")
def remove_team_member():
    b = data.Bucket(request.form)
    data.execute("DELETE FROM Team_members WHERE team_id = ? and rus_id = ?", b.team_id, b.rus_id)
