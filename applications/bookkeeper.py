# -*- coding: utf-8 -*-

import random, datetime, string, time, re

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, mail, html, expinterpreter
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
        return render_template("form.html", form=form)

@bookkeeper.route("/bookkeeper/book/<b_id>/modify", methods=["GET", "POST"])
def modify_book(b_id):
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape(u"Ændringer annulleret"))
            return redirect(url_for('bookkeeper.overview'))

        # TOPIC: insert descriptors
        b = data.Bucket(request.form)
        b.title
        b.description
        b >> ("UPDATE Books $ WHERE b_id = ?", b_id)

        # TOPIC: fetch new participants
        usernames = request.form['users']
        print usernames
        usernames = usernames.replace('"', '')
        usernames = usernames.replace('&quot;', '')
        usernames = [name.split()[0] for name in re.split(';\s', usernames) if name != ""]
        usernames = sorted(set(usernames))
        print usernames

        old = data.execute("SELECT participant FROM Book_participants where b_id = ?", b_id)
        old = [u[0] for u in old]

        # TOPIC: update list of participants in database, deleting missing and inserting new
        for user in set(old) - set(usernames):
            data.execute("DELETE FROM Book_participants where b_id = ? AND participant = ?", b_id, user)
        for user in sorted(set(usernames) - set(old)):
            data.execute("INSERT INTO Book_participants(b_id, participant) VALUES (?, ?)", b_id, user)

        # TODO: maybe we should ensure no one with debts/outstandings is removed?

        return redirect(url_for("bookkeeper.book", b_id=b_id))
    else:
        book = data.execute("SELECT * FROM Books where b_id = ?", b_id)[0]
        raw_users =  data.execute("SELECT username, name FROM Users")
        users = ['\\"{0}\\" {1}'.format(user['username'], user['name']) for user in raw_users]

        # TODO: fill with current
        participants = data.execute("SELECT * FROM Book_participants as B INNER JOIN Users as U ON B.participant = U.username WHERE b_id = ?", b_id)
        participants = ['&quot;{0}&quot; {1}; '.format(p['username'], p['name']) for p in participants]
        participants = "".join(participants)

        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("title", "Overskrift")
        w.textarea("description", "beskrivelse")
        w.html(html.autocomplete_multiple(users, "users", default=participants), description="Deltagere", value="abekat")
        form = w.create(book)
        return render_template("form.html", form=form)

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

    local_totals = [{"name":"Ole", "amount":"40"}]
    global_totals = [{"name":"Ole", "amount":"70"}]
    return render_template("bookkeeper/book.html", book=book, entries=entries, local_totals=local_totals, global_totals=global_totals)

# @bookkeeper.route("/bookkeeper/book/<b_id>/new_entry", methods=["GET", "POST"])
# def new_entry(b_id):
#     if request.method == "POST":
#         if 'cancel' in request.form:
#             flash(escape(u"Ændringer annulleret"))
#             return redirect(url_for('bookkeeper.overview'))

#         b = data.Bucket(request.form)
#         b.b_id = b_id
#         b.created = now()
#         b.creditor = session['username']
#         b.description
#         b.amount
#         b >= "Entries"

#         return redirect(url_for("bookkeeper.book", b_id=b_id))
#     else:
#         w = html.WebBuilder()
#         w.form()
#         w.formtable()
#         w.textfield("description", "Hvad")
#         w.textfield("amount", u"Beløb")
#         form = w.create()
#         return render_template("bookkeeper/new_entry.html", form=form)

@bookkeeper.route("/bookkeeper/book/<b_id>/new_entry", methods=["GET", "POST"])
@bookkeeper.route("/bookkeeper/book/<b_id>/entry/<e_id>", methods=["GET", "POST"])
def entry(b_id, e_id=None):
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape(u"Ændringer annulleret"))
            if e_id == None:
                return redirect(url_for('bookkeeper.overview'))
            else:
                return redirect(url_for('bookkeeper.book', b_id=b_id))

        b = data.Bucket(request.form)
        if b.description == "":
            flash("Please enter a description")
            return(html.back())
        b.amount
        if e_id == None:
            b.b_id = b_id
            b.created = now()
            # TODO: distinguish between creator and creditor
            b.creditor = session['username']
            b >= "Entries"
        else:
            b >> ("UPDATE Entries $ WHERE b_id = ? and e_id = ?", b_id, e_id)


        # EXPLANATION: ensure all 'share's are valid integers before any database modification
        debts = []
        for req in request.form.iterkeys():
            if req.startswith("participant_"):
                debtor = req[12:] # len("participant_") == 12
                share = request.form[req]
                try:
                    # EXPLANATION: we should store the string as the user specified but ensure it is calculates to a number
                    expinterpreter.interpret(share)
                except expinterpreter.ExpinterpreterException as e:
                    flash("Invalid expression in " + debtor + ": " + share)
                    return(html.back())
                if share != "":
                    debts.append((debtor, share))


        # TODO: The following is not harming, but is it necessary?
        # TODO: Think more about this line, is the previous statement true?
        data.execute("DELETE FROM Debts WHERE e_id = ?", e_id)

        for debtor, share in debts:
            # NOTE: insert automaticly replaces old entries
            data.execute("INSERT INTO Debts(e_id, debtor, share) VALUES (?, ?, ?)", e_id, debtor, share)

        return redirect(url_for("bookkeeper.book", b_id=b_id))
    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        if e_id == None:
            description = ""
            amount = ""
        else:
            entry = data.execute("SELECT * FROM Entries WHERE e_id = ?", e_id)[0]
            description = entry['description']
            amount = entry['amount']
        w.textfield("description", "Hvad", value=description)
        w.textfield("amount", u"Beløb", value=amount)

        # Extract users
        if e_id == None:
            previous_debtors = []
        else:
            previous_debtors = data.execute("SELECT username, name, share FROM Debts as D INNER JOIN Users as U ON D.debtor = U.username WHERE e_id = ?", e_id)

        usernames = [debtor['username'] for debtor in previous_debtors]
        participants = data.execute("SELECT * FROM Book_participants as B INNER JOIN Users as U ON B.participant = U.username WHERE b_id = ?", b_id)

        new_participants = [{'username':p['username'], 'name':p['name'], 'share':''} for p in participants if p['username'] not in usernames]

        all_participants = previous_debtors + new_participants
        all_participants = sorted(all_participants, cmp=lambda x, y: cmp(x['username'],y['username']))

        for user in all_participants:
            name = 'participant_{0}'.format(user['username'])
            description = '&quot;{0}&quot; {1}'.format(user['username'], user['name'])
            value = user['share']
            w.textfield(name, description, value=value)


        form = w.create()
        return render_template("form.html", form=form)





@bookkeeper.route("/bookkeeper/a/")
@bookkeeper.route("/bookkeeper/b/<id>")
def a(id=None):
    return "a"+str(id)



# bookkeeper - regnskabssystemet
# record / book - regnskab (S-togstur)
# entry - indtastning (1 ramme øl, 200,-)
# share - andel, hvor meget man skylder (X har drukket "share" af øllene)

# creditor - udlægger
# debitor - bruger
