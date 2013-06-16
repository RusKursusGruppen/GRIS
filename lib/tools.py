# -*- coding: utf-8 -*-
from functools import wraps
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint

import datetime

### TOOLS ###
def empty(lst):
    return lst == None or len(lst) == 0

def logged_in(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        if not session.get('logged_in'):
            session['login_origin'] = request.path
            abort(401)
        else:
            return fn(*args, **kwargs)
    return decorator

def now():
    return str(datetime.datetime.now())

def string_to_time(str):
    format = "%Y-%m-%d %H:%M:%S.%f"
    return datetime.datetime.strptime(str, format)

def html_calendar(id, dFormat = 'yyyyMMdd', selector = 'arrow', time = False, tFormat = 24, seconds = False, futurepast = ''):
    html = '<img src="/static/images/cal.gif" onclick="javascript:NewCssCal(\'{0}\',\'{1}\',\'{2}\',{3},{4},{5},\'{6}\')" class="calendar" />'.format(
        id, dFormat, selector, str(time).lower(), str(tFormat), str(seconds).lower(), futurepast)
    return html
