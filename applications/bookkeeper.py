# -*- coding: utf-8 -*-

from __future__ import division
import random, datetime, string, time, re

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, mail, html, expinterpreter
from lib.tools import logged_in, empty, url_front, now

import config


bookkeeper = Blueprint('bookkeeper', __name__, template_folder = '../templates/bookkeeper')

@bookkeeper.route("/bookkeeper/")
@logged_in
def overview():
    # TODO: Filter so you only see books referencing you
    books = data.execute("SELECT * FROM Books ORDER BY created DESC")

    return render_template("bookkeeper/overview.html", books=books)

@bookkeeper.route("/bookkeeper/new", methods=["GET", "POST"])
@logged_in
def new_book():
    # TODO: merge features of book and new_book
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape("Ændringer annulleret"))
            return redirect(url_for('bookkeeper.overview'))
        b = data.Bucket(request.form)
        b.title
        b.description
        b.creator = session['username']
        b.created = now()
        b_id = (b >= "Books")
        return redirect(url_for("bookkeeper.book", b_id=b_id))
    else:
        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("title", "Overskrift")
        w.textarea("description", "beskrivelse")
        form = w.create()
        return render_template("form.html", form=form)

@bookkeeper.route("/bookkeeper/book/<b_id>/modify", methods=["GET", "POST"])
@logged_in
def modify_book(b_id):
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape("Ændringer annulleret"))
            return redirect(url_for("bookkeeper.book", b_id=b_id))

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
        print(participants)

        w = html.WebBuilder()
        w.form()
        w.formtable()
        w.textfield("title", "Overskrift")
        w.textarea("description", "beskrivelse")
        w.html(html.autocomplete_multiple(users, "users", default=participants), description="Deltagere", value="abekat")
        form = w.create(book)
        return render_template("form.html", form=form)


@bookkeeper.route("/bookkeeper/book/<b_id>", methods=["GET", "POST"])
@logged_in
def book(b_id):
    # TODO: The books are technically correct, but we need to fix 2 things.
    #       1. You shouldn't see what you owe to yourself
    #       2. When you owe money to someone who also owes to you this should be substracted from each other


    book = data.execute("SELECT * FROM Books WHERE b_id = ?", b_id)[0]
    user = session['username']
    # TODO: convert internal representation to øre
    # TODO: decide on floating vs integer for currency
    raw_entries = data.execute(raw_entries_sql, b_id, user)


    # TODO: substract reverse debts
    local_totals = data.execute(local_totals_sql, b_id, user, user)
    global_totals = data.execute(global_totals_sql, user, user)

    raw_breakdown = data.execute(raw_breakdown_sql, b_id, b_id, b_id, b_id, b_id)
    entries = []
    for entry in raw_entries:
        d = {}
        d.update(entry)

        #amount = money(entry['amount'])
        #d['amount'] = amount

        share_total = entry['share_total']
        if share_total == None:
            share_total = 0
        share = entry['share']
        if share == None:
            share = 0

        final_share = "{0}/{1}".format(share, share_total)

        owes = entry['owes']
        if owes == None:
            owes = 0

        #owes = "{0}kr.".format(owes)
        if share == 0:
            final_share = ""
            owes = ""

        d.update({"final_share":final_share, "owes":owes})
        entries += [d]

    breakdown = []
    for row in raw_breakdown:
        res = {}
        for c in row.keys():
            if row[c] == None:
                res[c] = ""
            else:
                res[c] = row[c]
        breakdown.append(res)

    return render_template("bookkeeper/book.html", book=book, entries=entries, breakdown=breakdown, local_totals=local_totals, global_totals=global_totals)


# Select all entries in a book,
# add sum of shares per entry,
# add your shares
# calculate how much you owe
#
# b_id, debtor

raw_entries_sql = """
SELECT *,          /* Calculate how much you owe */
  ((amount*1)/share_total*share) AS owes
FROM               /* Select all entries in a book */
  (SELECT *
   FROM Entries
   where b_id = ?)
LEFT OUTER JOIN    /* add sum of shares per entry */
  (SELECT e_id,
          SUM(share) AS share_total
   FROM Debts
   GROUP BY e_id)
   USING (e_id)
LEFT OUTER JOIN    /* add your shares */
  (SELECT e_id,
          share
   FROM Debts
   WHERE debtor = ?)
  USING(e_id);
"""


# calculate the sum of owings from the raw_entries
# and remove null entries
#
# b_id, debtor
local_totals_sql = """
SELECT *
FROM
  (SELECT creditor,
          SUM(owes) AS total
   FROM

     /* raw_entries_sql: */
     (SELECT *,
      ((amount*1)/share_total*share) AS owes
      FROM
        (SELECT *
         FROM Entries
         WHERE b_id = ?)
      LEFT OUTER JOIN
        (SELECT e_id,
                SUM(share) AS share_total
         FROM Debts
         GROUP BY e_id)
        USING (e_id)
      LEFT OUTER JOIN
        (SELECT e_id,
                share
         FROM Debts
         WHERE debtor = ?)
        USING(e_id))

   GROUP BY creditor)
WHERE total is not Null AND creditor != ?
"""


# calculate there of owings from all entries
# remove null entries
#
# debtor
global_totals_sql = """
SELECT *
FROM
  (SELECT creditor,
          SUM(owes) AS total
   FROM
     (SELECT *,
             ((amount*1)/share_total*share) AS owes
      FROM
        Entries
      LEFT OUTER JOIN
        (SELECT e_id,
                SUM(share) AS share_total
         FROM Debts
         GROUP BY e_id)
        USING (e_id)
      LEFT OUTER JOIN
        (SELECT e_id,
                share
         FROM Debts
         WHERE debtor = ?)
        USING(e_id))
   GROUP BY creditor)
WHERE total is not Null AND creditor != ?
"""


raw_breakdown_sql = """
SELECT *,
       (IFNULL(credit, 0)-IFNULL(debt,0)) AS balance
FROM
  (SELECT *
   FROM
     (SELECT creditor AS user
      FROM Entries
      WHERE b_id = ?)
   UNION
     SELECT debtor AS user
     FROM Debts
   LEFT OUTER JOIN Entries
     USING(e_id)
   WHERE b_id = ?
   UNION
     SELECT participant AS user
     FROM Book_participants
     WHERE b_id = ?)
LEFT OUTER JOIN
  (SELECT creditor AS user,
          SUM(amount) AS credit
   FROM Entries
   WHERE b_id = ?
   GROUP BY creditor)
  USING (user)
LEFT OUTER JOIN
  (SELECT debtor AS user,
          SUM(debt) AS debt
   FROM
     (SELECT *,
             ((amount*1)/share_total*share) AS debt
      FROM Debts
      LEFT OUTER JOIN
      Entries USING(e_id)
      LEFT OUTER JOIN
        (SELECT e_id,
                SUM(share) AS share_total
         FROM Debts
         GROUP BY e_id)
        USING(e_id)
      WHERE b_id = ?)
   GROUP BY debtor)
  USING(user)
"""



# @bookkeeper.route("/bookkeeper/book/<b_id>/new_entry", methods=["GET", "POST"])
# def new_entry(b_id):
#     if request.method == "POST":
#         if 'cancel' in request.form:
#             flash(escape("Ændringer annulleret"))
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
#         w.textfield("amount", "Beløb")
#         form = w.create()
#         return render_template("bookkeeper/new_entry.html", form=form)

@bookkeeper.route("/bookkeeper/book/<b_id>/new_entry", methods=["GET", "POST"])
@bookkeeper.route("/bookkeeper/book/<b_id>/entry/<e_id>", methods=["GET", "POST"])
@logged_in
def entry(b_id, e_id=None):
    if request.method == "POST":
        if 'cancel' in request.form:
            flash(escape("Ændringer annulleret"))
            return redirect(url_for('bookkeeper.book', b_id=b_id))

        b = data.Bucket(request.form)
        if b.description == "":
            flash("Please enter a description")
            return html.back()
        b.amount_string
        # TODO: check for errors
        try:
            b.amount = expinterpreter.interpret_amount(b.amount_string)
        except expinterpreter.ExpinterpreterException as e:
            flash("invalid amount")
            return html.back()

        b.date
        b.creditor = b.creditor.replace('"', '').replace('&quot;', '')
        if b.creditor == "":
            flash("Please enter a creditor")
            return html.back()
        b.creditor = b.creditor.split()[0]

        if e_id == None:
            b.b_id = b_id
            e_id = (b >= "Entries")
            e_id = str(e_id)
        else:
            b >> ("UPDATE Entries $ WHERE b_id = ? and e_id = ?", b_id, e_id)


        # EXPLANATION: ensure all 'share's are valid integers before any database modification
        debts = []
        for req in request.form.keys():
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
                        return html.back()

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
            amount_string = ""
            date = ""
            creditor = session['username']
        else:
            entry = data.execute("SELECT * FROM Entries WHERE e_id = ?", e_id)[0]
            description = entry['description']
            amount_string = entry['amount_string']
            date = entry['date']
            creditor = entry['creditor']
        w.textfield("description", "Hvad", value=description)
        w.textfield("amount_string", "Beløb", value=amount_string)
        # TODO: make WebBuilder understand calendars
        w.html('<input type="text" id="bookkeeper.date" maxlength="25" size="25" name="date" value="'+date+'">' +
               html.calendar("bookkeeper.date")
               + '<span class="note">(Format: yyyy-MM-dd)</span>', description="Hvornår")

        participants = data.execute("SELECT * FROM Book_participants as B INNER JOIN Users as U ON B.participant = U.username WHERE b_id = ?", b_id)
        participant_names = ['\\"{0}\\" {1}'.format(user['username'], user['name']) for user in participants]
        #participant_names = [user['username'] for user in participants]
        w.html(html.autocomplete(participant_names, "creditor", default=creditor), description="Udlægger", value="abekat")

        # Extract users
        if e_id == None:
            previous_debtors = []
        else:
            previous_debtors = data.execute("SELECT username, name, share_string FROM Debts as D INNER JOIN Users as U ON D.debtor = U.username WHERE e_id = ?", e_id)

        usernames = [debtor['username'] for debtor in previous_debtors]
        #participants = data.execute("SELECT * FROM Book_participants as B INNER JOIN Users as U ON B.participant = U.username WHERE b_id = ?", b_id)

        new_participants = [{'username':p['username'], 'name':p['name'], 'share_string':''} for p in participants if p['username'] not in usernames]

        all_participants = previous_debtors + new_participants
        all_participants = sorted(all_participants, key=lambda x: x['username'])

        for user in all_participants:
            name = 'participant_{0}'.format(user['username'])
            description = '&quot;{0}&quot; {1}'.format(user['username'], user['name'])
            value = user['share_string']
            w.textfield(name, description, value=value)


        form = w.create()
        return render_template("form.html", form=form)




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
