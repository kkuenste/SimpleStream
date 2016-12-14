import email
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import date
from threading import Timer
from time import sleep
import schedule

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.function   = function
        self.interval   = interval
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

def sendEmail(sender, receiver, d):
	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Claire's Stream"
	msg['From'] = sender
	msg['To'] = receiver
	
        outer = {}
        test = {}
        test[0] = "2345"
        test[1] = 'https://getuikit.com/docs/images/placeholder_600x400.svg'
        test[2] = 'https://upload.wikimedia.org/wikipedia/commons/f/fb/Emoji_u1f4be.svg'
        test[3] = "This is a link test to check if this is working ignore datascience project is due kind of soon"
        test[4] = "askreddit"
        test[5] = "tylersam"
        outer[0] = test
        outer[1] = test


	html = """\
	<html>
  		<head></head>
  		<body>
    			<p>Here is your stream for this week:<br></p>
        """

        for x in outer:
            string = """
            Score: """ + outer[x][0] + """<br>  
            <a href=' """ + outer[x][2] + """ '> """ + outer[x][3] + """ </a>
            <a href=' """ + outer[x][2] + """ '><img src=' """ + outer[x][1] + """ '></a><br>
            subreddit: """ + outer[x][4] + """   author: """ + outer[x][5] + """
            <hr><br>
            """

            html += string

        html += """
  		</body>
	</html>
	"""


	emailBody = MIMEText(html, 'html')
	msg.attach(emailBody)
	s = smtplib.SMTP('smtp.gmail.com', 587)
	s.ehlo()
	s.starttls()
	s.login('simplestream2016@gmail.com', 'cse30246')
	s.sendmail(sender, receiver, msg.as_string())
	s.quit()

def hello():
	print "Hello claire"

if __name__ == "__main__":
	#print "starting timer:"+"\n"
	#rt = RepeatedTimer(5, sendEmail, "simplestream2016@gmail.com", "tsammons@nd.edu")
	d = {}
	d['item1'] = "blah blah"
	sendEmail("simplestream2016@gmail.com", "tsammons@nd.edu",d )
