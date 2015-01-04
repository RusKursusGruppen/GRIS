# -*- coding: utf-8 -*-
import random, string

from sqlalchemy.exc import IntegrityError

from gris import db

import lib.mail
from lib import mail
import models
from models import User
import config

def invite(emails):
    """Will generate and add a User_creation_key to the session.
    Remember to commit it"""
    length = config.USER_CREATION_KEY_LENGTH
    alphabet = string.ascii_letters + string.digits
    keys = [];

    for email in emails:
        keyFound = False
        key = None
        while not keyFound:
            key = ''.join(random.choice(alphabet) for x in range(length))
            existing = models.User_creation_key.query.filter_by(key=key).first()
            if existing is None:
                try:
                    creation_key = models.User_creation_key(key=key, email=email)
                    db.session.add(creation_key)
                    db.session.commit()
                    keys.append(creation_key)
                    keyFound = True
                except IntegrityError as e:
                    db.session.close()
        # url = config.URL + url_for("???", key=key)
        url = config.URL + "/TODO-find-out-how-to-set-up-link/" + key #TODO:
        mail.invitation_mail(url=url).send(email)

    # Notify admins
    mail.invitation_adminmail(emails="\n".join(emails)).to_admins()

def test():
    email.create_mail_template("hej", "hej igen")().send(["fiskomaten@gmail.com"])#, "vpb984@alumni.ku.dk"])
