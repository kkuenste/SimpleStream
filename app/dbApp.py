from flask import Flask, render_template, request, json, flash, make_response, Markup, redirect, url_for
from flask.ext.mysql import MySQL
from string import Template
import smtplib
import json
import email
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep
from RepeatedTimer import RepeatedTimer

'''
please test frequency of emails with a setting of Every Day to receive emails ev
ery hour. Uncomment out the number next to this part of the code in emails() and
 saveEmailPreferences() to set it back to normal.

'''

app = Flask(__name__)
app.secret_key = 'some_secret'

mysql = MySQL()

#Global user variables
userEmail = ""
preferenceList = {}
emailJobs = {}

# MySQL configs
app.config['MYSQL_DATABASE_USER'] = 'kkuenste'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pw'
app.config['MYSQL_DATABASE_DB'] = 'teamnull'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()


@app.before_first_request
def emails():
	global emailJobs	

	headers = {'Content-Type': 'text/html'}
	cursor.callproc('sp_getAllEmailData')
	data = cursor.fetchall()
	if len(data) > 0:
		conn.commit()
	for user in data:
		newDict = {}
		newDict['send'] = user[1]
		newDict['numPosts'] = user[2]
		newDict['freq'] = user[3]
#Create timer
		if user[1] == 1:  
			freqCount = 0
			f = user[3]
			userEmail = user[0]
			num = user[2]
			#pd = getPostsForEmail(user[0], user[2])
			sendEmail("simplestream2016@nd.edu", user[0], user[2])
			if f == 1:
               			freqCount = 604800
       			elif f == 2:
				freqCount = 302400
			elif f == 3:
				freqCount = 201600
			else: #every day
				freqCount = 3600#86400
			#newpd = getPostsForEmail(user[0], user[2])
       			rt = RepeatedTimer(freqCount, sendEmail, "simplestream2016@gmail.com", userEmail, num)
	# sent in user email and numposts for call to getPostsForEmail
			newDict['timer'] = rt
		else:
			newDict['timer'] = None
		emailJobs[user[0]] = newDict
	return None

def getPostsForEmail(userEmail, num):
	global emailJobs
	headers = {'Content-Type': 'text/html'}
	cursor.callproc('sp_returnPreferences', (userEmail,))
	data = cursor.fetchall()
	if len(data) >  0:
        	conn.commit()
                cursor.callproc('sp_returnRecommendedPosts', (userEmail, num))
        else:
		conn.commit()
                cursor.callproc('sp_getTopPosts', (userEmail, num))
        data2 = cursor.fetchall()
	postDict={}
        if len(data2) > 0:
                conn.commit()
        	postCount = 1
        	for post in data2:
                	newDict = {}
                	newDict['subreddit']= post[0]
                	newDict['author'] = post[1]
                	newDict['url'] = post[2]
                	newDict['num_comments'] = post[3]
                	newDict['score'] = post[4]
                	newDict['ups'] = post[5]
                	newDict['downs'] = post[6]
                	newDict['title'] = post[7]
                	newDict['selftext'] = post[8]
                	newDict['ID'] = post[9]
                	newDict['over_18'] = post[10]
                	newDict['thumbnail'] = post[11]
                	newDict['link_flair_text'] = post[12]
                	postDict[str(postCount)] = newDict
                	postCount += 1

#	for k, v in postDict.iteritems():
#		print k, v
#		print "\n"
	return postDict
	

#new sign in, first
@app.route("/main")
def main():
	return render_template('index.html')

#@app.route("/signIn")
#def showSignIn():
#	return render_template('signin.html')


@app.route("/verifyUser", methods=['POST'])
def verify():
	
	headers = {'Content-Type': 'text/html'}
	_email = request.form['inputEmail']
	_password = request.form['inputPassword']
	global userEmail
	global preferenceList
	userEmail = ""
	preferenceList.clear()
	
	if _email and _password:
		cursor.callproc('sp_verifyUser', (_email, _password))
		data = cursor.fetchall()
		
		if len(data) is 1:
			conn.commit()

		if data[0][0] == 1:
			userEmail = _email

			cursor.callproc('sp_returnPreferences', (_email,))
			data2 = cursor.fetchall()
			if len(data2) > 0:
				conn.commit()
			for i in data2:
				for j in i:
					preferenceList[j] = 1 
                                
			return make_response('http://dsg1.crc.nd.edu:5001/stream', 200, headers)
			
		else:
			message = "fail"#"Username or password is not correct. Please try again."
			return make_response(message,200,headers)
			


@app.route('/showSignUp')
def showSignUp():
	return render_template('signup.html')


@app.route('/signUp', methods=['POST'])
def signUp():
	global userEmail
	global preferenceList
	global emailJobs
	userEmail = ""
	preferenceList.clear()
	headers = {'Content-Type': 'text/html'}
	_fname = request.form['inputFirstName']
	_lname = request.form['inputLastName']
	_email = request.form['inputEmail']
	_password = request.form['inputPassword']
	
	if _fname and _lname and _email and _password:
                cursor.callproc('sp_createUser', (_fname, _lname, _email, _password))
                data = cursor.fetchall()
                if len(data) is 1:
                        conn.commit()
		if data[0][0] == 1:
			userEmail = _email
			newDict={}
			newDict['freq'] = 1
			newDict['numPosts'] = 10 
			newDict['send'] = 0
			# create new cron job
			newDict['timer'] = None
			emailJobs[_email] = newDict 
			return make_response('http://dsg1.crc.nd.edu:5001/stream', 200, headers)

		else:
			json.dumps({'html':'<span>Couldnt create user.</span>'})
	else:
		return json.dumps({'html':'<span>Enter the required fields</span>'})	

@app.route('/showAccount')
def showAccountDetails():        
	return render_template('preferences.html')

@app.route('/newPassword', methods=['POST'])
def newPassword():
	global userEmail
	global preferenceList
	_email = userEmail
        _pass = request.form['inputNewPassword']
	if _pass:
		x = cursor.callproc('sp_updatePassword', (_email, _pass))
               	data = cursor.fetchall()
                if len(data) is 1:
                        conn.commit()
		if data[0][0] == 1:
               		return json.dumps({'html':'<span>All fields pass.</span>'})
		else:
			return json.dumps({'html':'<span>Couldnt save password.</span>'})
		

        else:
                return json.dumps({'html':'<span>Enter the required fields</span>'})



@app.route('/deleteAccount', methods=['POST'])
def deleteAccount():
	global userEmail
	global preferenceList
	global emailJobs
	headers = {'Content-Type': 'text/html'}

	_email = userEmail
        cursor.callproc('sp_deleteUser', (_email,))
        data = cursor.fetchall()
        if len(data) is 1:
                conn.commit()
	if data[0][0] == 0:
		emailJobs[_email]['timer'].stop()
        	del emailJobs[_email]
		userEmail = ""
		preferenceList.clear()
		
		return make_response('http://dsg1.crc.nd.edu:5001/main', 200, headers)

	else:
		return json.dumps({'html':'<span>Couldnt delete user</span>'})


@app.route('/stream', methods=['GET'])
def simpleStream():
	return render_template('stream.html')

@app.route('/populateStream', methods=['POST'])
def populateStream():
	postDict = {}
	numPosts = request.form['numPosts']
	global userEmail
	global preferenceList
	headers = {'Content-Type': 'text/html'}
	_email = userEmail
		
	# random posts if no preferences
	if len(preferenceList) is 0:
		cursor.callproc('sp_getTopPosts', (_email, numPosts))
	else:
		cursor.callproc('sp_returnRecommendedPosts', (_email, numPosts))
	data = cursor.fetchall()
	if len(data) > 0:
		conn.commit()
	postCount = 1
	for post in data:
		newDict = {}
		newDict['subreddit']= post[0]
		newDict['author'] = post[1]
		newDict['url'] = post[2]
		newDict['num_comments'] = post[3]
		newDict['score'] = post[4]
		newDict['ups'] = post[5]
		newDict['downs'] = post[6]
		newDict['title'] = post[7]
		newDict['selftext'] = post[8]
		newDict['ID'] = post[9]
		newDict['over_18'] = post[10]
		newDict['thumbnail'] = post[11]
		newDict['link_flair_text'] = post[12]
		postDict[str(postCount)] = newDict
		postCount += 1
	td = json.dumps(postDict)
	return make_response(td, 200, headers)
				


@app.route('/addPreference', methods=['POST'])
def addPreference():
	global userEmail
	global preferenceList
	headers = {'Content-Type': 'text/html'}
	_email = userEmail
	_preference = request.form['inputNewPref']
	if _preference:
		cursor.callproc('sp_addPreference', (_email, _preference))
		data = cursor.fetchall()
		if len(data) is 1:
			conn.commit()
		print data[0][0]
		print type(data[0][0])
		if data[0][0] > 0:
			if _preference in preferenceList:
				return make_response("exists", 200, headers)
			else:
				preferenceList[_preference] = 1
				return make_response(_preference, 200, headers)

		else:
			return json.dumps({'html':'<span>Couldnt add pref</span>'})

@app.route('/loadPreferences', methods=['POST'])
def loadPreferences():
	global preferenceList
	global userEmail
	headers = {'Content-Type': 'text/html'}
	sendString = ""
	send = ""
	freq = ""
	numPosts = ""
	_email = userEmail

	for k in preferenceList.keys():
		sendString += k + '\n'
	cursor.callproc('sp_getEmailPreferences', (_email,))
	data = cursor.fetchall()
	if len(data) > 0:
		conn.commit()
	td = {}
	td['prefString'] = sendString
	td['freq'] = data[0][1]
	td['numPosts'] = data[0][2]
	td['send'] = data[0][0]
	tempDict = json.dumps(td)
	return make_response(tempDict, 200, headers)

@app.route('/clearPreferences', methods=['POST'])
def clearPreferences():
	global userEmail
	global preferenceList
	headers = {'Content-Type': 'text/html'}
	_email = userEmail
	cursor.callproc('sp_clearPreferences', (_email,))
	data = cursor.fetchall()
	if len(data) is 1:
		conn.commit()
	if data[0][0] == 1:
		preferenceList.clear()
		return make_response("Preferences cleared", 200, headers)
	else:
		return make_response("Error clearing preferences", 200, headers)
	


@app.route('/saveEmailPreferences', methods=['POST'])
def saveEmailPreferences():
	global email
	global preferenceList
	global emailJobs

	headers = {'Content-Type': 'text/html'}
	_send = request.form['emailCheck']
	_numPosts = request.form['numPosts']
	_freq = request.form['emailFreq']
	_email = userEmail
	
	if _numPosts and _freq:
		cursor.callproc('sp_updateUserAccount', (_email, _send, _freq, _numPosts))
		data = cursor.fetchall()
		if len(data) is 1:
			conn.commit()
		emailJobs[_email]['send'] = _send
		emailJobs[_email]['freq'] = _freq
		emailJobs[_email]['numPosts'] = _numPosts
		print "freq: "+str(_freq)
		print type(_freq)
		if emailJobs[_email]['timer'] is not None:
   	             emailJobs[_email]['timer'].stop()
		if _send == u'1':
			
			freqCount = 0
                	#pd = getPostsForEmail(_email, _numPosts)
                	sendEmail("simplestream2016@nd.edu", _email, int(_numPosts))
                	if _freq == u'1':
                       		freqCount = 604800
                	elif _freq == u'2':
                       		freqCount = 302400
               		elif _freq == u'3':
                       		freqCount = 201600
               		else:
                       		freqCount = 3600#86400
			#newpd = getPostsForEmail(_email, _numPosts)
               		rt = RepeatedTimer(freqCount, sendEmail, "simplestream2016@gmail.com", _email, _numPosts)
			emailJobs[_email]['timer'] = rt
		else:
			emailJobs[_email]['timer'] = None
		return make_response("Email prefs added", 200, headers)
	else:
		return make_response("Couldn't save email prefs", 200, headers)
	

@app.route('/logOut', methods=['POST'])
def logOut():
	global userEmail
	global preferenceList
	headers = {'Content-Type': 'text/html'}
	userEmail = ""
	preferenceList.clear()
	return make_response('http://dsg1.crc.nd.edu:5001/main', 200, headers)

def sendEmail(sender, receiver, n):
	#for k,v in postdict.iteritems():
	#	print k, v

	postdict = getPostsForEmail(receiver, n)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Stream"
        msg['From'] = sender
        msg['To'] = receiver

        html = """\
        <html>
                <head></head>
                <body>
                        <p>Here is your stream:<br>"""

        for x in postdict:
                string = """
                Score: """ + str(postdict[x]['score']) + """<br> 
                <a href=' """ + str(postdict[x]['url']) + """ '> """ + str(postdict[x]['title']) + """ </a><br>
                <a href=' """ + str(postdict[x]['url']) + """ '><img src=' """ + str(postdict[x]['thumbnail']) + """ '></a><br>
                subreddit: """ + str(postdict[x]['subreddit']) + """<br>author: """ + str(postdict[x]['author']) + """ 
                <hr><br>"""
                html += string;
        

        html +=  """
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
	return None


if __name__ == "__main__":
	app.run()
