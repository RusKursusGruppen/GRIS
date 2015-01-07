# -*- coding: utf-8 -*-

import datetime
import werkzeug

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
