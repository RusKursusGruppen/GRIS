# -*- coding: utf-8 -*-

import datetime
import dateutil
import dateutil.relativedelta

from functools import wraps
import psycopg2
import psycopg2.extras

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

from lib import html
import lib.data

### TOOLS ###
def empty(lst):
    return lst == None or len(lst) == 0

def logged_in(*args):
    # EXPLANATION: logged_in is called as a decorator
    if callable(args[0]):
        fn = args[0]
        @wraps(fn)
        def decorated(*args, **kwargs):
            if not session.get('logged_in'):
                session['login_origin'] = request.path
                abort(401)
            else:
                return fn(*args, **kwargs)
        return decorated

    else:
        # EXPLANATION: decorator factory called with something to iterate
        if not isinstance(args[0], str):
            rights = args[0]
        else:
            rights = args

        def decorator(fn):
            @wraps(fn)
            def decorated(*args, **kwargs):
                if not session.get('logged_in'):
                    session['login_origin'] = request.path
                    abort(401)
                else:
                    groups = lib.data.execute('SELECT groupname FROM User_groups WHERE username = ?', session['username'])
                    for group in groups:
                        if group['groupname'] in rights:
                            return fn(*args, **kwargs)
                    flash("You do not have sufficient rights to access this page.")
                    return redirect(url_front())
            return decorated
        return decorator

def url_front():
    return url_for('front.frontpage')

def now():
    return datetime.datetime.now()

def rkgyear(date = None):
    if date == None:
        date = now()
    date = date - dateutil.relativedelta.relativedelta(months = +6)
    return date.year

def string_to_time(str):
    format = "%Y-%m-%d %H:%M:%S.%f"
    return datetime.datetime.strptime(str, format)

def nonify(value):
    if value == "None":
        return None
    return value

def unnonify(value):
    def _unnonify(dictrow):
        dictrow = dictrow.copy()
        for k, v in dictrow.items():
            dictrow[k] = v if v != None else ""
        return dictrow

    if isinstance(value, psycopg2.extras.DictRow):
        return _unnonify(value)
    return [_unnonify(v) for v in value]

def get(key):
    "Returns getter function"
    return lambda x: x[key]
