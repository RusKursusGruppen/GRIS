# -*- coding: utf-8 -*-

import itertools

from flask import Blueprint, request, session

from lib.tools import abort, get, jsonify, logged_in, now, rkgyear, success

blueprint = Blueprint("rustours", __name__, url_prefix="/api")
from gris import data

@blueprint.route("/rustours", methods=["GET", "POST"])
@logged_in
def rustours():
    b = data.request()
    if "year" in b:
        tours = data.execute("SELECT * FROM Tours WHERE year = ? ORDER BY tour_name ASC", b.year)
        tours = [tour.__html__() for tour in tours]
        total = len(tours)
        return jsonify(rustours=tours, total=total)

    else:
        tours = data.execute("SELECT * FROM Tours ORDER BY year DESC, tour_name ASC")
        total = len(tours)
        tours = itertools.groupby(tours, key=get("year"))
        tour_dict = {}
        years = []
        for year, tours_in_year in tours:
            years.append(year)
            tour_dict[year] = [tour().all_dict() for tour in tours_in_year]
        return jsonify(rustours=tour_dict, total=total, years=years)

@blueprint.route("/rustours/tour", methods=["GET", "POST"])
@logged_in
def rustour():
    b = data.request()
    tour_id = b.tour_id
    with data.transaction():
        tour = data.execute("SELECT * FROM Tours WHERE tour_id = ?", tour_id).one()
        tutors = data.execute("SELECT * FROM tours_tutors INNER JOIN Users USING(user_id) WHERE tour_id = ? ORDER BY username ASC", tour_id)
        russer = data.execute("SELECT * FROM Russer WHERE rustour = ? ORDER BY name ASC", tour_id)

        # teams = data.execute("SELECT * FROM Team_categories LEFT OUTER JOIN Teams WHERE tour_id = ?", tour_id)

        #TODO: left join on teams members
        #TODO: also find russer not assigned to a team for each category
        #TODO: show something about teams
        return jsonify(tour=tour, tutors=tutors, russer=russer)

@blueprint.route("/rustours/new", methods=["POST"])
@logged_in("trusted")
def new():
    b = data.request()

    if "year" in b:
        b.year
    else:
        b.year = rkgyear()

    if "type" in b:
        b.type

    if "tour_name" not in b or b.tour_name == "":
        b.tour_name = "Unavngiven rustur"

    if "theme" in b:
        b.theme

    if "notes" in b:
        b.notes

    b >= "Tours"

    return success()

def only_members(tour_id):
    pass

@blueprint.route("/rustours/update", methods=["POST"])
@logged_in("rkg")
def update():
    b = data.request()

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
    return success()


@blueprint.route("/rustours/delete", methods=["POST"])
@logged_in("rkg")
def delete():
    b = data.request()
    if b.delete:
        try:
            # TODO: delete dependencies?
            data.execute("DELETE FROM Tours WHERE tour_id = ?", b.tour_id)
        except:
            abort("Could not delete tour, there are people/items associated with it")


@blueprint.route("/rustours/tutors/add", methods=["POST"])
@logged_in("rkg")
def add_tutor():
    b = data.request()
    b.tour_id
    b.user_id
    b >= "Tours_tutors"
    return success()

@blueprint.route("/rustours/tutors/remove", methods=["POST"])
@logged_in("rkg")
def remove_tutor():
    b = data.request()
    data.execute("DELETE FROM Tours_tutors WHERE tour_id = ? and user_id = ?", b.tour_id, b.user_id)
    return success()



### TEAMS ###
@blueprint.route("/rustours/teams/category/add", methods=["POST"])
@logged_in("rkg")
def add_team_category():
    b = data.request()
    b.tour_id
    b.category
    b >= "Team_categories"

@blueprint.route("/rustours/teams/category/update", methods=["POST"])
@logged_in("rkg")
def update_team_category():
    b = data.request()
    b.category
    b >> ("UPDATE Team_categories $ WHERE tour_id = ?", b["tour_id"])

@blueprint.route("/rustours/teams/category/delete", methods=["POST"])
@logged_in("rkg")
def delete_team_category():
    b = data.request()
    data.execute("DELETE FROM Team_categories WHERE team_category_id = ?", b.team_category_id)


@blueprint.route("/rustours/teams/add", methods=["POST"])
@logged_in("rkg")
def add_team():
    b = data.request()
    b.team_category_id
    b.team_name
    b >= "Teams"

@blueprint.route("/rustours/teams/update", methods=["POST"])
@logged_in("rkg")
def update_team():
    b = data.request()
    b.team_name
    b >> ("UPDATE Teams $ WHERE team_id = ?", b["team_id"])

@blueprint.route("/rustours/teams/delete", methods=["POST"])
@logged_in("rkg")
def delete_team():
    b = data.request()
    data.execute("DELETE FROM Teams WHERE team_id = ?", b.team_id)


@blueprint.route("/rustours/teams/members/add", methods=["POST"])
@logged_in("rkg")
def add_team_member():
    b = data.request()
    b.team_id
    b.rus_id
    b >= "Team_members"

@blueprint.route("/rustours/teams/members/remove", methods=["POST"])
@logged_in("rkg")
def remove_team_member():
    b = data.request()
    data.execute("DELETE FROM Team_members WHERE team_id = ? and rus_id = ?", b.team_id, b.rus_id)
