#!/usr/bin/python
import email
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import date
from threading import Timer
from time import sleep
import schedule

msg = MIMEMultipart('alternative')
msg['Subject'] = "Claire's Stream"
msg['From'] = 'simplestream2016@gmail.com'
msg['To'] = 'csonderm@nd.edu'

html = """\
<html>
	<head></head>
	<body>
        <p>Here is your stream for this week:<br>
        </p>
        </body>
</html>
"""
emailBody = MIMEText(html, 'html')
msg.attach(emailBody)
s = smtplib.SMTP('smtp.gmail.com', 587)
s.ehlo()
s.starttls()
s.login('simplestream2016@gmail.com', 'cse30246')
s.sendmail('simplestream2016@gmail.com','csonderm@nd.edu', msg.as_string())
s.quit()
