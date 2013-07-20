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

@bookkeeper.route("/bookkeeper/book/<b_id>/modify", methods=["GET", "POST"])
def modify_book(b_id):
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape(u"Ændringer annulleret"))
            return redirect(url_for('bookkeeper.overview'))
        b = data.Bucket(request.form)
        b.title
        b.description
        b >> ("UPDATE Books $ WHERE b_id = ?", b_id)

        string = request.form['users']
        string = string.replace('"', '')
        usernames = [name.split()[0] for name in re.split(';\s', string)]
        usernames = sorted(set(usernames))
        # TODO: ensure no one with debts/outstandings is removed

        print (request.form['scba'])
        return redirect(url_for("bookkeeper.book", b_id=b_id))
    else:
        book = data.execute("SELECT * FROM Books where b_id = ?", b_id)[0]
        raw_users =  data.execute("SELECT username, name FROM Users")
        users = ['\\"{0}\\" {1}'.format(user['username'], user['name']) for user in raw_users]

        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("title", "Overskrift")
        w.textarea("description", "beskrivelse")
        w.html(html.autocomplete_multiple(users, "users"), description="Deltagere")
        form = w.create(book)
        return render_template("bookkeeper/modify_book.html", form=form)

@bookkeeper.route("/bookkeeper/book/<b_id>", methods=["GET", "POST"])
def book(b_id):
    book = data.execute("SELECT * FROM Books WHERE b_id = ?", b_id)[0]
    raw_entries = data.execute("SELECT * FROM entries WHERE b_id = ? ORDER BY created ASC", b_id)
    entries = []
    for entry in raw_entries:
        d = {}
        d.update(entry)
        d.update({"share":"3/4", "owes":"40,-"})
        entries += [d]
    print entries

    local_totals = [{"name":"Ole", "amount":"40"}]
    global_totals = [{"name":"Ole", "amount":"70"}]
    return render_template("bookkeeper/book.html", book=book, entries=entries, local_totals=local_totals, global_totals=global_totals)

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


@bookkeeper.route("/bookkeeper/book/<b_id>/entry/<e_id>", methods=["GET", "POST"])
def entry(b_id, e_id):
    if request.method == "POST":
        b = data.Bucket(request.form)
        b.description
        b.amount
        b >> ("UPDATE Entries WHERE e_id = ?", e_id)

        b = data.Bucket(request.form)
        return redirect(url_for("bookkeeper.book", b_id=b_id))
    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("description", "Hvad")
        w.textfield("amount", "Beløb")

# bookkeeper - regnskabssystemet
# record / book - regnskab (S-togstur)
# entry - indtastning (1 ramme øl, 200,-)
# share - andel, hvor meget man skylder (X har drukket "share" af øllene)

# creditor - udlægger
# debitor - bruger
