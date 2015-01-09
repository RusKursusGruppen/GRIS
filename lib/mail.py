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
            if isinstance(arg, Bucket):
                format_args.update(data.bucket_to_dict(arg))
            else:
                format_args.update(arg)
        format_args.update(**kwargs)

        subject = self.subject
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



invitation = Template(
    "Invitation til GRIS", """
<p>Hej du er blevet inviteret til GRIS.</p>
<p>GRIS er RKGs intranet, hvis du skal være med i RKG skal du have en bruger her.</br>
For at oprette en bruger skal du følge det følgende link.</br>
Linket er unikt og virker kun en enkelt gang.</p>

<p><a href="{url}">Opret bruger</a><p>
    """)

invitation_adminmail = Template(
    "User Invited", """
An invitation has been send to the following addresses:
{emails}

Sending failed to the following:
{failed}
    """, html=False)

forgot_password = Template(
    "Glemt Løsen", """
<p>Hej {name}, du har glemt dit løsen.</br>
Vi har derfor sendt dig dette link hvor du kan vælge et nyt.</br>
Linket virker kun de næste 20 minutter.</p>

<p><a href="{url}">Vælg nyt løsen</a></p>

<p>Hvis du ikke har glemt dit løsen kan du se bort fra denne mail.</p>
""")

forgot_password_multiple_adminmail = Template(
    "Strange forgotten password activity", """
Multiple forgotten password emails has been send to {username}, without the previous link being used.

There were already {times} key[s] in the database.
    """, html=False)

forgot_password_no_email_adminmail = Template(
    "Could not send 'forgotten password' email", """
A user with no email or an invalid has forgot his/her password.
Or at least has pushed the button.

Name: {name}
Username: {username}
Email: {email}
Phone: {phone}
""")
