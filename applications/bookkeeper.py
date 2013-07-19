# -*- coding: utf-8 -*-

import random, datetime, string, time

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, mail, html
from lib.tools import logged_in, empty, url_front, now

import config


bookkeeper = Blueprint('bookkeeper', __name__, template_folder = '../templates/bookkeeper')

@bookkeeper.route("/bookkeeper")
def overview():
    # TODO: Filter so you only see books referencing you
    books = data.execute("SELECT * FROM Books ORDER BY created DESC")

    return render_template("bookkeeper/overview.html", books=books)

@bookkeeper.route("/bookkeeper/new", methods=["GET", "POST"])
def new_book():
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape(u"Ændringer annulleret"))
            return redirect(url_for('bookkeeper.overview'))
        b = data.Bucket(request.form)
        b.title
        b.description
        b.creator = session['username']
        b.created = now()
        b >= "Books"
        return redirect(url_for("bookkeeper.overview"))
    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("title", "Overskrift")
        w.textarea("description", "beskrivelse")
        form = w.create()
        return render_template("bookkeeper/new_book.html", form=form)

@bookkeeper.route("/bookkeeper/book/<b_id>", methods=["GET", "POST"])
def book(b_id):
    book = data.execute("SELECT * FROM Books WHERE b_id = ?", b_id)[0]
    return render_template("bookkeeper/book.html", book=book)

@bookkeeper.route("/bookkeeper/book/<b_id>/new_entry", methods=["GET", "POST"])
def new_entry(b_id):
    if request.method == "POST":
        b = data.Bucket(request.form)
        b.b_id = b_id
        b.created = now()
        b.creditor = session['username']
        b.description
        b.amount
        b >= "Entries"

        return redirect(url_for("bookkeeper.book", b_id=b_id))
    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("description", "Hvad")
        w.textfield("amount", u"Beløb")
        form = w.create()
        return render_template("bookkeeper/new_entry.html", form=form)



# bookkeeper - regnskabssystemet
# record / book - regnskab (S-togstur)
# entry - indtastning (1 ramme øl, 200,-)
# share - andel, hvor meget man skylder (X har drukket "share" af øllene)

# creditor - udlægger
# debitor - bruger
