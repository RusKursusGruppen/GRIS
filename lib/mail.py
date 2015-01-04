# -*- coding: utf-8 -*-

import flask_mail

from gris import db, mail

import models
import config

class Message(flask_mail.Message):
    def send(self, to=None):
        recipients = []
        if to is not None:
            if isinstance(to, str):
                recipients.append(to)
            else:
                recipients.extend(to)

        if isinstance(self.recipients, str):
            recipients.append(self.recipients)
        else:
            recipients.extend(self.recipients)

        if self.sender is None:
            self.sender = (config.MAIL_NAME, config.MAIL)

        with mail.connect() as connection:
            for recipient in recipients:
                self.recipients = [recipient]
                flask_mail.Message.send(self, connection)
        self.recipients = recipients

    def to_admins(self, override=False):
        if override or config.MAIL_ADMINS:
            admins = (db.session.query(models.User)
                      .filter(models.User.groups.any(groupname="admin"))\
                      .filter(models.User.email != None).all())

            self.send([admin.email for admin in admins])

def create_mail_template(subject="", body=None, html=True):
    def fill_mail_template(**kwargs):
        nonlocal subject, body, html
        if body is not None:
            body = body.format(**kwargs)
        if html:
            return Message(subject=subject, html=body)
        else:
            return Message(subject=subject, body=body)
    return fill_mail_template

invitation_mail = create_mail_template(
    "Invitation til GRIS", """
Hej du er blevet inviteret til GRIS.
GRIS er RKGs intranet, hvis du skal være med i RKG skal du have en bruger her.
For at oprette en bruger skal du følge det følgende link.
Linket er unikt og virker kun en enkelt gang.

<a href="{url}">Opret bruger</a>
""")

invitation_adminmail = create_mail_template(
    "User Invited", """
An invitation has been send to the following addresses:
{emails}
    """, html=False)
