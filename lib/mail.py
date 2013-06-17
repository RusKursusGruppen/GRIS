
from smtplib import SMTP
from email.mime.text import MIMEText
import config

def send(to, subject, text):
    msg = MIMEText(text, 'plain', "utf-8")
    msg['To'] = to
    msg['From'] = config.EMAIL
    msg['Subject'] = subject

    s = SMTP()
    s.connect()
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()
