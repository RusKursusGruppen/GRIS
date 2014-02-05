# -*- coding: utf-8 -*-

import random, datetime, string, time, itertools

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, mail, html
from lib.tools import logged_in, empty, url_front, now

import config

rustours = Blueprint('rustours', __name__, template_folder = '../templates/rustours')

@rustours.route('/rustours')
def overview():
    tours = data.execute("SELECT * FROM Tours ORDER BY year DESC")
    tours = itertools.groupby(tours, key=lambda tour: tour['year'])
    # print("")
    # for x,y in tours:
    #     print(x, list(y))

    # print("")

    # for year in tours:
    #     print(year[0])
    #     for tour in year[1]:
    #         print(tour

    return render_template("rustours/overview.html", tours=tours)

@rustours.route('/rustours/tour/<t_id>')
def rustour(t_id):
    tour = data.execute("SELECT * FROM Tours WHERE t_id = ?", t_id)[0]
    return render_template("rustours/rustour.html", tour=tour)

@rustours.route('/rustours/new', methods=['GET', 'POST'])
def new():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape("Rus IKKE tilføjet"))
            return redirect(url_for('rustours.overview'))

        b = data.Bucket(request.form)
        b.type
        b.year = int(now()[:4])
        b >= "Tours"
        return redirect(url_for('rustours.overview'))

    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.select("type", "Type", [('p', 'Pigetur'), ('t', 'Transetur'), ('m', 'Munketur')])
        form = w.create()
        return render_template("form.html", form=form)
