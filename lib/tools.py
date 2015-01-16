# -*- coding: utf-8 -*-

import datetime, random, time
from functools import wraps
import werkzeug
from flask import request, session

def abort(code=None, description=None):
    _abort = werkzeug.exceptions.abort
    if code is None:
        code = 500
    if description is None:
        if not isinstance(code, int):
            description = code
            code = 500
            _abort(code, description)
        _abort(code)
    _abort(code, description)

def now():
    return datetime.datetime.now(datetime.timezone.utc)

def sleep(start, end=None):
    if end is not None:
        time.sleep(start, end)
    elif isinstance(start, (tuple, list)):
        a, b = start
        t = a + random.random() * (b - a)
        time.sleep(t)
    else:
        time.sleep(start)


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
                    groups = lib.data.execute("SELECT groupname FROM Group_users WHERE user_id = ?", session["user_id"])
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
