# -*- coding: utf-8 -*-

import io

import flask
from flask import session

# import lib.tools
from lib.tools import now

import config

def log(message, level="INFO", logfile=None, print_log=None):
    try:
        user = session['username']
    except:
        user = "NO USER"

    try:
        ip = flask.request.environ["REMOTE_ADDR"]
    except:
        ip = "UNKNOWN IP"

    time = now()
    time = time.strftime("%Y-%m-%d %H:%M:%S")
    string = "{0} | {1} | {2} | {3} | {4}".format(level, time, ip, user, message)

    if logfile == None:
        logfile = config.LOGFILE
    if print_log == None:
        print_log = config.PRINT_LOG

    with open(logfile, "a") as f:
        f.write(string + "\n")
    if print_log:
        print(string)

def data(sql, args, error=False):
    # EXPLANATION: We don't want to log selections
    if sql[:6].lower() == 'select':
        return

    args = ','.join(repr(a) for a in args)
    string = '"{0}" ({1})'.format(sql, args)
    if error:
        log(string, level="DATABASE ERROR!!!")
    else:
        log(string, level="DATABASE")

def request():
    path = flask.request.path
    if path == "/favicon.ico" or path.startswith("/static/"):
        return

    log(path, "REQUEST", config.REQUEST_LOGFILE, config.PRINT_REQUEST_LOG)
