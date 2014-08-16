# -*- coding: utf-8 -*-

from smtplib import SMTP
from email.mime.text import MIMEText

from lib import data

import config

def send(to, subject, text, type="html"):
    msg = MIMEText(text, type, "utf-8")
    if isinstance(to, str):
        # We dont bother to send the destination header for lists of mails
        msg['To'] = to
    msg['From'] = config.EMAIL
    msg['Subject'] = subject

    session = SMTP(config.EMAIL_HOST, config.EMAIL_HOST_PORT)
    session.ehlo()
    session.starttls()
    session.login(config.EMAIL, config.EMAIL_PASSWORD)
    session.sendmail(config.EMAIL, to, msg.as_string())

def admin(subject, text, type="plain"):
    if config.MAIL_ADMINS:
        admins = data.execute("SELECT email FROM Group_users INNER JOIN Users USING (username) WHERE groupname = ? and email IS NOT NULL", "admin")
        if len(admins) > 0:
            send(admins, subject, text, type)
