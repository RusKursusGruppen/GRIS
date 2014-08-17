# -*- coding: utf-8 -*-

import random, datetime, re, itertools

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint
import psycopg2

from lib import data, password, html
from lib.tools import logged_in, now, rkgyear, nonify, get

rusmanager = Blueprint('rusmanager', __name__, template_folder = '../templates/rusmanager')

@rusmanager.route('/rusmanager')
@logged_in('rkg', 'mentor')
def overview():
    russer = data.execute("SELECT * FROM Russer ORDER BY name ASC")
    return render_template("rusmanager/overview.html", russer=russer)

@rusmanager.route('/rusmanager/<r_id>', methods=['GET', 'POST'])
@logged_in('rkg', 'mentor')
def rus(r_id):
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape("Ændringer anulleret"))
            return redirect(url_for('rusmanager.overview'))

        b = data.Bucket(request.form)
        b.filled_by = session["username"]
        b.can_contact = True if "can_contact" in request.form else False
        b.called = "called" in request.form
        b.name
        b.gender
        b.birthday = nonify(b.birthday)
        b.co
        b.address
        b.zipcode
        b.city
        b.move_time
        b.new_address
        b.new_zipcode
        b.new_city
        b.phone
        b.email
        b.vacation
        b.priority
        b.gymnasium
        b.since_gymnasium
        b.supplementary_exams
        b.merit
        b.code_experience
        b.special_needs
        b.plays_instrument
        b.other
        b.tshirt
        b.paid = "paid" in request.form
        b.attending_uniday = "attending_uniday" in request.form
        b.attending_campus = "attending_campus" in request.form
        b.attending_rustour = "attending_rustour" in request.form

        b.rustour = nonify(b.rustour)
        b.dutyteam = nonify(b.dutyteam)
        if b.dutyteam is not None:
            t_id = data.execute("SELECT t_id FROM Dutyteams WHERE d_id = ?", b.dutyteam)
            t_id = str(t_id[0]['t_id'])
            if b.rustour != t_id:
                b.dutyteam = None
        b.mentor = nonify(b.mentor)
        b >> ("UPDATE Russer SET $ WHERE r_id = ?", r_id)

        # Friends:
        friends = request.form['friends']
        friends = friends.replace('"', '')
        friends = friends.replace('&quot;', '')
        friend_ids = [name.split()[0] for name in re.split(';\s', friends) if name != ""]

        for friend in friend_ids:
            try:
                b = data.Bucket()
                b.r_id1, b.r_id2 = sorted((int(friend), int(r_id)))
                b >= "Friends"
            except psycopg2.IntegrityError as e:
                pass

        # Friends of us:
        user_friends = request.form['user_friends']
        user_friends = user_friends.replace('"', '')
        user_friends = user_friends.replace('&quot;', '')
        user_friends = [name.split()[0] for name in re.split(';\s', user_friends) if name != ""]

        for friend in user_friends:
            try:
                b = data.Bucket()
                b.r_id = r_id
                b.username = friend
                b >= "Friends_of_us"
            except psycopg2.IntegrityError as e:
                pass

        flash("Rus opdateret")

        if "next" in request.form:
            russer = data.execute("SELECT r_id FROM Russer ORDER BY name ASC")
            russer = [str(rus['r_id']) for rus in russer]
            try:
                next = russer[russer.index(r_id) + 1]
                return redirect(url_for('rusmanager.rus', r_id=next))
            except (ValueError, IndexError):
                pass

        if "previous" in request.form:
            russer = data.execute("SELECT r_id FROM Russer ORDER BY name ASC")
            russer = [str(rus['r_id']) for rus in russer]
            try:
                index = russer.index(r_id) - 1
                if index < 0:
                    raise IndexError()
                previous = russer[index]
                return redirect(url_for('rusmanager.rus', r_id=previous))
            except (ValueError, IndexError):
                pass


        return redirect(url_for('rusmanager.overview'))
    else:
        rus = data.execute("SELECT * FROM Russer WHERE r_id = ?", r_id)
        if len(rus) == 0:
            return "Den rus findes ikke din spasser!"
        else:
            rus = rus[0]

        year = rkgyear()
        tours = data.execute("SELECT * FROM Tours WHERE year = ?", year)
        tours = [(tour['t_id'], tour['tour_name']) for tour in tours]
        tours = [(None, "None")] + tours

        birthday = rus["birthday"]
        if birthday == None:
            birthday = ""
        elif isinstance(birthday, datetime.date):
            birthday = birthday.isoformat()

        dutyteams = data.execute("SELECT * FROM Dutyteams WHERE t_id = ?", rus["rustour"])
        dutyteams = [(dutyteam['d_id'], dutyteam['name']) for dutyteam in dutyteams]
        dutyteams = [(None, "None")] + dutyteams

        mentors = data.execute("SELECT * FROM Mentorteams WHERE year = ?", year)
        mentors = [(mentor['m_id'], mentor['mentor_names']) for mentor in mentors]
        mentors = [(None, "None")] + mentors


        # Friends:
        russer = data.execute("SELECT r_id, name FROM Russer WHERE r_id != ?", r_id)
        russer = ['\\"{0}\\" {1}'.format(rus['r_id'], rus['name']) for rus in russer]
        friends = data.execute("SELECT * FROM ((SELECT r_id2 as r_id FROM Friends WHERE r_id1 = ?) UNION (SELECT r_id1 as r_id FROM Friends where r_id2 = ?)) as a INNER JOIN Russer USING (r_id) ORDER BY Name", r_id, r_id)
        friends = ['&quot;{0}&quot; {1}; '.format(friend['r_id'], friend['name']) for friend in friends]
        friends = "".join(friends)

        # Friends of us:
        users = data.execute("SELECT username, name FROM Users WHERE deleted = ?", False)
        users = ['\\"{0}\\" {1}'.format(user['username'], user['name']) for user in users]
        user_friends = data.execute("SELECT username, name FROM Friends_of_us INNER JOIN USERS Using (username) WHERE r_id = ?", r_id)
        user_friends = ['&quot;{0}&quot; {1}; '.format(friend['username'], friend['name']) for friend in user_friends]
        user_friends = "".join(user_friends)

        gender = [("male", "Mand"), ("female", "Kvinde"), ("other", "andet")]

        wb = html.WebBuilder()
        wb.form()
        wb.formtable()
        wb.checkbox("can_contact", "Må kontaktes")
        wb.checkbox("called", "Opringet")
        wb.textfield("name", "Navn")
        wb.select("gender", "Køn", gender)
        wb.calendar("birthday", "Fødselsdag")
        wb.textfield("phone", "Tlf")
        wb.textfield("email", "email")
        wb.textfield("co", "co")
        wb.textfield("address", "Adresse")
        wb.textfield("zipcode", "Postnummer")
        wb.textfield("city", "By")
        wb.textfield("move_time", "Flyttedato")
        wb.textfield("new_address", "Ny adresse")
        wb.textfield("new_zipcode", "Nyt postnummer")
        wb.textfield("new_city", "Ny by")
        wb.textfield("vacation", "Ferie")
        wb.textfield("priority", "DIKU prioritet")
        wb.textfield("gymnasium", "Adgangsgivende eksamen (inkl. år)")
        wb.textfield("since_gymnasium", "Lavet efterfølgende")
        wb.textfield("supplementary_exams", "Tager du supplerende eksamener")
        wb.textfield("merit", "Merit")
        wb.textfield("code_experience", "Kode erfaring")
        wb.textfield("special_needs", "Specielle behov")
        wb.textfield("plays_instrument", "Spiller instrument")
        wb.textarea("other", "Andet")
        #wb.textfield("Friends", "Kender")
        wb.checkbox("attending_uniday", "Deltager unidag")
        wb.checkbox("attending_campus", "Deltager campus")
        wb.checkbox("attending_rustour", "Deltager rustur")
        wb.select("rustour", "Skal på:", tours)
#        wb.textfield("dutyteam", "Tjansehold")
        wb.select("dutyteam", "Tjansehold:", dutyteams)
        wb.select("mentor", "Mentorhold:", mentors)
        wb.textfield("tshirt", "Tshirt størrelse")
        wb.checkbox("paid", "Betalt")
        wb.html(html.autocomplete_multiple(russer, "friends", default=friends), description="Tilføj bekendte russer")
        wb.html(html.autocomplete_multiple(users, "user_friends", default=user_friends), description="Tilføj bekendte vejledere")
        wb.html('<button type="submit" name="next" value="next">Gem og gå videre</button>')
        wb.html('<button type="submit" name="previous" value="previous">Gem og gå til forige</button>')

        form = wb.create(rus)

        return render_template("rusmanager/rus.html", form=form, name=rus['name'])

@rusmanager.route('/rusmanager/new', methods=['GET', 'POST'])
@logged_in('rkg', 'mentor')
def new():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape("Rus IKKE tilføjet"))
            return redirect(url_for('rusmanager.overview'))

        name = " ".join([x.capitalize() for x in request.form['name'].split()])
        r_id = data.execute("INSERT INTO Russer(name) VALUES(?) RETURNING r_id", name)[0][0]
        flash("Rus oprettet")
        return redirect(url_for('rusmanager.rus', r_id=r_id))
    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("name", "Navn")
        form = w.create()
        return render_template("form.html", form=form)

@rusmanager.route('/rusmanager/friends')
@logged_in('rkg', 'mentor')
def friends():
    friends = data.execute("SELECT r_id1, name1, r_id2, name AS name2 FROM (SELECT r_id1, name AS name1, r_id2 FROM (SELECT * FROM Friends UNION (SELECT r_id2 AS r_id1, r_id1 AS r_id2 FROM Friends)) AS a INNER JOIN Russer ON r_id1 = r_id) AS b INNER JOIN Russer ON r_id2 = r_id ORDER BY name1")
    friends = itertools.groupby(friends, key=get('name1'))
    friends = [(x[0], list(x[1])) for x in friends]
    friends = [({'name1':name, 'r_id1':l[0]['r_id1']}, l) for name, l in friends]

    user_friends = data.execute("SELECT username, Users.name as users_name, r_id, Russer.name as russer_name FROM Friends_of_us INNER JOIN Users USING (username) INNER JOIN Russer Using (r_id) ORDER BY Russer.name")
    user_friends = itertools.groupby(user_friends, key=get('russer_name'))
    user_friends = [(x[0], list(x[1])) for x in user_friends]
    user_friends = [({'russer_name':name, 'r_id':l[0]['r_id']}, l) for name, l in user_friends]

    return render_template("rusmanager/friends.html", friends=friends, user_friends=user_friends)
