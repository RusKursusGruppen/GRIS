# -*- coding: utf-8 -*-

from smtplib import SMTPRecipientsRefused
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

        failed = []
        with mail.connect() as connection:
            for recipient in recipients:
                self.recipients = [recipient]
                try:
                    flask_mail.Message.send(self, connection)
                except SMTPRecipientsRefused:
                    failed.append(recipient)
        self.recipients = recipients
        return failed

    def to_admins(self, override=False):
        if override or config.MAIL_ADMINS:
            admins = (db.session.query(models.User)
                      .filter(models.User.groups.any(groupname="admin"))\
                      .filter(models.User.email != None).all())

            return self.send([admin.email for admin in admins])

class Template():
    def __init__(self, subject=None, body=None, html=True):
        self.subject = subject
        self.body = body
        self.html = html

    def format(self, *args, **kwargs):
        format_args = dict()
        for arg in args:
            format_args.update(arg)
        format_args.update(**kwargs)

        body = self.body
        html = self.html

        if isinstance(html, bool):
            if self.html:
                html = body
                body = None
            else:
                html = None

        if body is not None:
            body = body.format(**kwargs)
        if html is not None:
            html = html.format(**kwargs)

        return Message(subject=self.subject, body=body, html=html)

invitation_mail = Template(
    "Invitation til GRIS", """
Hej du er blevet inviteret til GRIS.
GRIS er RKGs intranet, hvis du skal være med i RKG skal du have en bruger her.
For at oprette en bruger skal du følge det følgende link.
Linket er unikt og virker kun en enkelt gang.

<a href="{url}">Opret bruger</a>
""")

invitation_adminmail = Template(
    "User Invited", """
An invitation has been send to the following addresses:
{emails}
    """, html=False)
