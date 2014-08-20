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

def admin(subject, text, type="plain", mail_admins=None):
    if mail_admins == None:
        mail_admins = config.MAIL_ADMINS
    if mail_admins:
        admins = data.execute("SELECT email FROM Group_users INNER JOIN Users USING (username) WHERE groupname = ? and email IS NOT NULL", "admin_mail_log")
        if len(admins) > 0:
            send(admins, subject, text, type)

new_user_adminmail = """
A new user has been created
Username: {username}
Name: {name}
email: {email}
"""

invitation_send_adminmail = """
An invitation has been send to:
{email}
"""

error_adminmail = """
An error has occurred! <br/>
<b>Username</b>: {username} <br/>
<b>Time</b>: {time} <br/>
<b>IP</b>: {ip} <br/>
<b>url</b>: {url} <br/>
<b>Error code</b>: <br/>
{code}
"""
