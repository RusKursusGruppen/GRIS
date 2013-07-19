# -*- coding: utf-8 -*-

import random, datetime, string, time

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import data, password, mail, html
from lib.tools import logged_in, empty, url_front

import config


bookkeeper = Blueprint('bookkeeper', __name__, template_folder = '../templates/bookkeeper')

@bookkeeper.route("/bookkeeper")
def overview():
    # TODO: Filter so you only see books referencing you
    books = data.execute("SELECT * FROM Books ORDER BY created DESC")

    return render_template("bookkeeper/overview.html", books=books)

@bookkeeper.route("/bookkeeper/new", methods=["GET", "POST"])
def new_book():

    return render_template("bookkeeper/new_book.html")

@bookkeeper.route("/bookkeeper/sheet/<sid>", methods=["GET", "POST"])
def sheet(sid):
    return render_template("bookkeeper/sheet.html")

@bookkeeper.route("/bookkeeper/sheet/<sid>/newtransaction", methods=["GET", "POST"])
def new_transaction(sid):
    return render_template("bookkeeper/sheet.html")



# bookkeeper - regnskabssystemet
# record / book - regnskab (S-togstur)
# entry - indtastning (1 ramme øl, 200,-)
# share - andel, hvor meget man skylder (X har drukket "share" af øllene)

# creditor - udlægger
# debitor - bruger
