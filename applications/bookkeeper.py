# -*- coding: utf-8 -*-

from __future__ import division
import random, datetime, string, time, re

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, mail, html, expinterpreter
from lib.tools import logged_in, empty, url_front, now

import config


bookkeeper = Blueprint('bookkeeper', __name__, template_folder = '../templates/bookkeeper')

@bookkeeper.route("/bookkeeper/")
def overview():
    # TODO: Filter so you only see books referencing you
    books = data.execute("SELECT * FROM Books ORDER BY created DESC")

    return render_template("bookkeeper/overview.html", books=books)

@bookkeeper.route("/bookkeeper/new", methods=["GET", "POST"])
def new_book():
    # TODO: merge features of book and new_book
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
        usernames = usernames.replace('"', '')
        usernames = usernames.replace('&quot;', '')
        usernames = [name.split()[0] for name in re.split(';\s', usernames) if name != ""]
        #usernames = sorted(set(usernames))

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
        users.sort()


        # TODO: fill with current
        participants = data.execute("SELECT * FROM Book_participants as B INNER JOIN Users as U ON B.participant = U.username WHERE b_id = ?", b_id)
        participants = ['&quot;{0}&quot; {1}; '.format(p['username'], p['name']) for p in participants]
        participants.sort()
        participants = "".join(participants)
        print participants

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
    #raw_entries = data.execute("SELECT * FROM Entries WHERE b_id = ? ORDER BY date ASC", b_id)
    user = session['username']
    raw_entries = data.execute('SELECT * FROM Entries LEFT OUTER JOIN (SELECT e_id, SUM(share) AS share_total FROM Debts GROUP BY e_id) USING (e_id) LEFT OUTER JOIN (SELECT e_id, share FROM Debts WHERE debtor = ?) USING(e_id);', user)
    entries = []
    for entry in raw_entries:
        d = {}
        d.update(entry)

        amount = entry['amount']
        # TODO: check for errors, do this on insertion
        amount = amount if type(amount) == int else expinterpreter.interpret(amount)

        share_total = entry['share_total']
        if share_total == None:
            share_total = 0
        share = entry['share']
        if share == None:
            share = 0

        final_share = "{0}/{1}".format(share, share_total)

        if share_total == 0:
            owes = 0
        else:
            owes = (amount / share_total) * share

        owes = "{0}kr.".format(owes)
        if share == 0:
            final_share = ""
            owes = ""
        d.update({"final_share":final_share, "owes":owes})
        entries += [d]

    local_totals = [{"name":"Ole", "amount":"40"}]
    global_totals = [{"name":"Ole", "amount":"70"}]
    return render_template("bookkeeper/book.html", book=book, entries=entries, local_totals=local_totals, global_totals=global_totals)

    #"select * from Entries as E join (select e_id, sum(share) as share_total from Debts) as T on E.e_id = T.e_id;"
    #raw_entries = data.execute('SELECT * FROM Entries AS E JOIN (SELECT e_id, SUM(share) AS share_total FROM Debts) AS T INNER JOIN (SELECT e_id, share FROM Debts WHERE debtor = ?) AS D ON E.e_id = T.e_id and E.e_id= D.e_id ORDER BY date ASC;', user)





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
            return redirect(url_for('bookkeeper.book', b_id=b_id))

        b = data.Bucket(request.form)
        if b.description == "":
            flash("Please enter a description")
            return(html.back())
        b.amount
        b.date
        if e_id == None:
            b.b_id = b_id
            # TODO: distinguish between creator and creditor
            b.creditor = session['username']
            e_id = b >= "Entries"
            e_id = str(e_id)
        else:
            b.creditor = b.creditor.replace('"', '').replace('&quot;', '')
            if b.creditor == "":
                flash("Please enter creditor")
                return(html.back())
            b.creditor = b.creditor.split()[0]
            b >> ("UPDATE Entries $ WHERE b_id = ? and e_id = ?", b_id, e_id)


        # EXPLANATION: ensure all 'share's are valid integers before any database modification
        debts = []
        for req in request.form.iterkeys():
            if req.startswith("participant_"):
                debtor = req[12:] # len("participant_") == 12
                share_string = request.form[req]
                if share_string != "":
                    try:
                        # EXPLANATION: we store both the string and its result, if it evaluates to something meaningful
                        share = expinterpreter.interpret(share_string)
                        debts.append((debtor, share_string, share))
                    except expinterpreter.ExpinterpreterException as e:
                        flash("Invalid expression in " + debtor + ": " + share)
                        return(html.back())

        # TODO: The following is not harming, but is it necessary?
        # TODO: Think more about this line, is the previous statement true?
        data.execute("DELETE FROM Debts WHERE e_id = ?", e_id)

        for debtor, share_string, share in debts:
            # NOTE: insert automaticly replaces old entries
            data.execute("INSERT INTO Debts(e_id, debtor, share_string, share) VALUES (?, ?, ?, ?)", e_id, debtor, share_string, share)

        return redirect(url_for("bookkeeper.book", b_id=b_id))
    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        if e_id == None:
            description = ""
            amount = ""
            date = ""
            creditor = session['username']
        else:
            entry = data.execute("SELECT * FROM Entries WHERE e_id = ?", e_id)[0]
            description = entry['description']
            amount = entry['amount']
            date = entry['date']
            creditor = entry['creditor']
        w.textfield("description", "Hvad", value=description)
        w.textfield("amount", u"Beløb", value=amount)
        # TODO: make WebBuilder understand calendars
        w.html('<input type="text" id="bookkeeper.date" maxlength="25" size="25" name="date" value="'+date+'">' +
               html.calendar("bookkeeper.date")
               + '<span class="note">(Format: yyyy-MM-dd)</span>', description=u"Hvornår")

        participants = data.execute("SELECT * FROM Book_participants as B INNER JOIN Users as U ON B.participant = U.username WHERE b_id = ?", b_id)
        participant_names = ['\\"{0}\\" {1}'.format(user['username'], user['name']) for user in participants]
        #participant_names = [user['username'] for user in participants]
        w.html(html.autocomplete(participant_names, "creditor", default=creditor), description=u"Udlægger", value="abekat")

        # Extract users
        if e_id == None:
            previous_debtors = []
        else:
            previous_debtors = data.execute("SELECT username, name, share_string FROM Debts as D INNER JOIN Users as U ON D.debtor = U.username WHERE e_id = ?", e_id)

        usernames = [debtor['username'] for debtor in previous_debtors]
        #participants = data.execute("SELECT * FROM Book_participants as B INNER JOIN Users as U ON B.participant = U.username WHERE b_id = ?", b_id)

        new_participants = [{'username':p['username'], 'name':p['name'], 'share_string':''} for p in participants if p['username'] not in usernames]

        all_participants = previous_debtors + new_participants
        all_participants = sorted(all_participants, cmp=lambda x, y: cmp(x['username'],y['username']))

        for user in all_participants:
            name = 'participant_{0}'.format(user['username'])
            description = '&quot;{0}&quot; {1}'.format(user['username'], user['name'])
            value = user['share_string']
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


def to_usernamelist(users):
    return ['\\"{0}\\" {1}'.format(user['username'], user['name']) for user in users]

def from_usernamelist(usernames):
    usernames = usernames.replace('"', '')
    usernames = usernames.replace('&quot;', '')
    usernames = [name.split()[0] for name in re.split(';\s', usernames) if name != ""]
    usernames = sorted(set(usernames))
    return usernames
