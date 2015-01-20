# -*- coding: utf-8 -*-

import datetime, random, time
from functools import wraps
import werkzeug
import flask
from flask import request, session

import gris


class AbortException(Exception):
    def __init__(self, code, description=None):
        self.code = code
        self.description = description

def abort(code=None, description=None):
    _abort = werkzeug.exceptions.abort
    if code is None:
        code = 500
    if description is None:
        if not isinstance(code, int):
            description = code
            code = 500
            raise AbortException(code, description)
        raise AbortException(code)
    raise AbortException(code, description)

def success(message=None):
    result = dict(success=True)
    if message is not None:
        result["message"] = message
    return jsonify(result)

def now():
    return datetime.datetime.now(datetime.timezone.utc)

def rkgyear(date=None):
    if date is None:
        date = now()
    date = date - dateutil.relativedelta.relativedelta(months=+6)
    return date.year

def sleep(start, end=None):
    if end is not None:
        time.sleep(start, end)
    elif isinstance(start, (tuple, list)):
        a, b = start
        t = a + random.random() * (b - a)
        time.sleep(t)
    else:
        time.sleep(start)

def jsonify(*args, **kwargs):
    args = [item.__html__() if hasattr(item, "__html__") else item
            for item in args]
    return flask.jsonify(*args, **kwargs)

def empty(lst):
    return lst == None or len(lst) == 0

def logged_in(*args):
    # EXPLANATION: logged_in is called as a decorator
    if callable(args[0]):
        fn = args[0]
        @wraps(fn)
        def decorated(*args, **kwargs):
            if not session.get("logged_in"):
                session["login_origin"] = request.path
                abort(403)
            else:
                return fn(*args, **kwargs)
        return decorated

    else:
        # EXPLANATION: decorator factory called with something to iterate
        if isinstance(args[0], str):
            rights = list(args)
        else:
            rights = list(args[0])

        # Admins can do everything
        rights.append("admin")

        def decorator(fn):
            @wraps(fn)
            def decorated(*args, **kwargs):
                if not session.get("logged_in"):
                    session["login_origin"] = request.path
                    abort(403)
                else:
                    groups = gris.data.execute("SELECT groupname FROM Group_users WHERE user_id = ?", session["user_id"])
                    for group in groups:
                        if group["groupname"] in rights:
                            return fn(*args, **kwargs)
                    abort(403)
            return decorated
        return decorator

def is_admin():
    if "is_admin" not in flask.g:
        groups = lib.data.execute("SELECT groupname FROM Group_users WHERE user_id = ?", session["user_id"]).scalars()
        flask.g.is_admin = "admin" in groups
    return flask.g.is_admin
