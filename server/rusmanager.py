# -*- coding: utf-8 -*-

from flask import Blueprint, request, session

from lib.tools import abort, logged_in, now, rkgyear

blueprint = Blueprint("rusmanager", __name__, url_prefix="/api")
from gris import data

@blueprint.route('/rusmanager')
@logged_in('rkg', 'mentor')
def russer():
    year = request.values.get("year", None)
    russer = data.execute("SELECT * FROM Russer WHERE year = ? ORDER BY name ASC", year)
    return russer


@blueprint.route('/rusmanager/rus')
@logged_in('rkg', 'mentor')
def rus():
    rus_id = request.values.get("rus_id", None)
    rus = data.execute("SELECT * FROM Russer WHERE rus_id = ?", rus_id).one()
    #TODO: find friends
    #TODO: find friends of us
    return rus


@blueprint.route('/rusmanager/new', methods=["GET", "POST"])
@logged_in('rkg')
def new():
    b = data.request()
    names = []
    if "name" in b:
        names.append(name)
    if "names" in b:
        if isinstance(b.names, str):
            names.extend(b.names.split(";"))
        else:
            names.extend(b.names)

    names = (" ".join(word.capitalize() for word in name.split()) for name in names)
    year = rkgyear()
    query = ((name, year) for name in names)

    data.executemany("INSERT INTO Russer(name, year) VALUES (?, ?)", query)

@blueprint.route("/rusmanager/update", methods=["POST"])
@logged_in("rkg")
def update():
    b = data.request()
    if "year" in b: b.year

    if "filled_by" in b: session["user_id"]
    if "last_updated" in b: now()

    if "can_contact" in b: b.can_contact
    if "called" in b: b.called

    if "name" in b: b.name
    if "ku_id" in b: b.ku_id
    if "gender" in b: b.gender
    if "birthday" in b: b.birthday
    if "phone" in b: b.phone
    if "email" in b: b.email
    if "co" in b: b.co
    if "address" in b: b.address
    if "zipcode" in b: b.zipcode
    if "city" in b: b.city

    if "moving" in b: b.moving
    if "move_time" in b: b.move_time
    if "new_address" in b: b.new_address
    if "new_zipcode" in b: b.new_zipcode
    if "new_city" in b: b.new_city

    if "vacation" in b: b.vacation
    if "priority" in b: b.priority

    if "gymnasium" in b: b.gymnasium
    if "since_gymnasium" in b: b.since_gymnasium
    if "supplementary_exams" in b: b.supplementary_exams
    if "merit" in b: b.merit

    if "code_experience" in b: b.code_experience
    if "special_needs" in b: b.special_needs
    if "plays_instrument" in b: b.plays_instrument
    if "other" in b: b.other
    if "tshirt" in b: b.tshirt
    if "paid" in b: b.paid

    if "attending_uniday" in b: b.attending_uniday
    if "attending_campus" in b: b.attending_campus
    if "attending_rustour" in b: b.attending_rustour

    if "rustour" in b: b.rustour
    if "mentor" in b: b.mentor

    b >> ("UPDATE Russer $ WHERE rus_id = ?", b["rus_id"])

@blueprint.route("/rusmanager/delete", methods=["POST"])
@logged_in("rkg")
def delete():
    b = data.request()
    if b.delete:
        try:
            data.execute("DELETE FROM Russer WHERE rus_id = ?", b.rus_id)
        except:
            abort("Could not delete Rus, there are people/items associated with it")

@blueprint.route('/rusmanager/friends')
@logged_in('rkg', 'mentor')
def friends():
    #TODO: this has just been copied over, should probably be refactored/refined/redone!
    friends = data.execute("SELECT rus_id1, name1, rus_id2, name AS name2 FROM (SELECT rus_id1, name AS name1, rus_id2 FROM (SELECT * FROM Friends UNION (SELECT rus_id2 AS rus_id1, rus_id1 AS rus_id2 FROM Friends)) AS a INNER JOIN Russer ON rus_id1 = rus_id) AS b INNER JOIN Russer ON rus_id2 = rus_id ORDER BY name1")
    friends = itertools.groupby(friends, key=get('name1'))
    friends = [(x[0], list(x[1])) for x in friends]
    friends = [({'name1':name, 'rus_id1':l[0]['rus_id1']}, l) for name, l in friends]

    user_friends = data.execute("SELECT user_id, Users.name as users_name, rus_id, Russer.name as russer_name FROM Friends_of_us INNER JOIN Users USING (user_id) INNER JOIN Russer Using (rus_id) ORDER BY Russer.name")
    user_friends = itertools.groupby(user_friends, key=get('russer_name'))
    user_friends = [(x[0], list(x[1])) for x in user_friends]
    user_friends = [({'russer_name':name, 'rus_id':l[0]['rus_id']}, l) for name, l in user_friends]

@blueprint.route('/rusmanager/status')
@logged_in('rkg', 'mentor')
def status():
    #TODO: copy over
    abort()
