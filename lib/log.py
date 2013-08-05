# -*- coding: utf-8 -*-

import io

from flask import session

from lib.tools import now

import config

def log(message, level="INFO"):
    user = session['username']
    time = now()
    string = "{0} | {1} | {2} | {3}\n".format(level, time, user, message)
    string = unicode(string)
    with io.open(config.LOGFILE, "a") as f:
        f.write(string)
    if config.PRINT_LOG:
        print(string)

def data(sql, args, error=False):
    # EXPLANATION: We don't want to log selections
    if sql[:6].lower() == 'select':
        return

    args = ','.join(str(a) for a in args)
    string = '"{0}" ({1})'.format(sql, args)
    if error:
        log(string, level="DATABASE ERROR!!!")
    else:
        log(string, level="DATABASE")
