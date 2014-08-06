# -*- coding: utf-8 -*-

import random, datetime, re

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint
import psycopg2

from lib import data, password, html
from lib.tools import logged_in, now, rkgyear, nonify

rusmanager = Blueprint('rusmanager', __name__, template_folder = '../templates/rusmanager')

@rusmanager.route('/rusmanager')
@logged_in('rkg', 'mentor')
def overview():
    russer = data.execute("select r_id, name from Russer")
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
        b.called = 1 if "called" in request.form else 0
        b.name
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
        b.code_experience
        b.special_needs
        b.plays_instrument
        b.other
        b.tshirt
        b.paid = 1 if "paid" in request.form else 0
        b.attending_uniday = 1 if "attending_uniday" in request.form else 0
        b.attending_campus = 1 if "attending_campus" in request.form else 0
        b.attending_rustour = 1 if "attending_rustour" in request.form else 0
        b.rustour = nonify(b.rustour)
        b.dutyteam = nonify(b.dutyteam)
        b.mentor = nonify(b.mentor)
        b.birthday
        b >> ("UPDATE Russer SET $ WHERE r_id = ?", r_id)

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
                print(e)

        flash("Rus opdateret")
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

        dutyteams = data.execute("SELECT * FROM Dutyteams WHERE t_id = ?", rus["rustour"])
        dutyteams = [(dutyteam['tj_id'], dutyteam['name']) for dutyteam in dutyteams]
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

        wb = html.WebBuilder()
        wb.form()
        wb.formtable()
        wb.checkbox("called", "Opringet")
        wb.textfield("name", "Navn")
#        wb.textfield("birthday", "Fødselsdag")
        wb.html('<input type="text" id="rusmanager.birthday" maxlength="25" size="25" name="birthday" value="'+birthday+'">' +
               html.calendar("rusmanager.birthday")
               + '<span class="note">(Format: yyyy-MM-dd)</span>', description="Fødselsdag")
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
        wb.textfield("gymnasium", "Gymnasium")
        wb.textfield("since_gymnasium", "Lavet efterfølgende")
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
        wb.html(html.autocomplete_multiple(russer, "friends", default=friends), description="Tilføj bekendte")
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
        r_id = data.execute("INSERT INTO Russer(name, called) VALUES(?,?) RETURNING r_id", name, 0)[0][0]
        flash("Rus oprettet")
        return redirect(url_for('rusmanager.rus', r_id=r_id))
    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("name", "Navn")
        form = w.create()
        return render_template("form.html", form=form)
