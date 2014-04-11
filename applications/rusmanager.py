# -*- coding: utf-8 -*-

import random, datetime

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, html
from lib.tools import logged_in, now

rusmanager = Blueprint('rusmanager', __name__, template_folder = '../templates/rusmanager')

@rusmanager.route('/rusmanager')
@logged_in('tutor', 'mentor')
def overview():
    russer = data.execute("select r_id, name from Russer")
    return render_template("rusmanager/overview.html", russer=russer)

@rusmanager.route('/rusmanager/<r_id>', methods=['GET', 'POST'])
@logged_in('tutor', 'mentor')
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
        b.uniday = 1 if "uniday" in request.form else 0
        b.campus = 1 if "campus" in request.form else 0
        b.tour = 1 if "tour" in request.form else 0
        b.rustour
        b.dutyteam
        b.birthday
        b >> ("UPDATE Russer SET $ WHERE r_id = ?", r_id)

        flash("Rus opdateret")
        return redirect(url_for('rusmanager.overview'))
    else:
        rus = data.execute("SELECT * FROM Russer WHERE r_id == ?", r_id)
        if len(rus) == 0:
            return "Den rus findes ikke din spasser!"
        else:
            rus = rus[0]

        year = now()[:4]
        tours = data.execute("SELECT * FROM Tours WHERE year = ?", year)
        tours = [(tour['t_id'], tour['tour_name']) for tour in tours]
        tours = [(None, "None")] + tours

        wb = html.WebBuilder()
        wb.form()
        wb.formtable()
        wb.checkbox("called", "Opringet")
        wb.textfield("name", "Navn")
        wb.textfield("birthday", "Fødselsdag")
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
        wb.checkbox("uniday", "Deltager unidag")
        wb.checkbox("campus", "Deltager campus")
        wb.checkbox("tour", "Deltager rustur")
        wb.select("rustour", "Skal på:", tours)
        wb.textfield("dutyteam", "Tjansehold")

        wb.textfield("tshirt", "Tshirt størrelse")
        wb.checkbox("paid", "Betalt")
        form = wb.create(rus)

        return render_template("rusmanager/rus.html", form=form, name=rus['name'])

@rusmanager.route('/rusmanager/new', methods=['GET', 'POST'])
@logged_in('tutor', 'mentor')
def new():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape("Rus IKKE tilføjet"))
            return redirect(url_for('rusmanager.overview'))

        name = " ".join([x.capitalize() for x in request.form['name'].split()])
        lastrowid = data.execute_lastrowid("INSERT INTO Russer(name, called) VALUES(?,?)", name, 0)
        flash("Rus oprettet")
        return redirect(url_for('rusmanager.rus', r_id=str(lastrowid)))
    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("name", "Navn")
        form = w.create()
        return render_template("form.html", form=form)
