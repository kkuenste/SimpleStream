from flask import Flask, render_template, request, json, flash, make_response, Markup, redirect, url_for
from flask.ext.mysql import MySQL
import json

app = Flask(__name__)
app.secret_key = 'some_secret'

mysql = MySQL()

#Global Login variables
userEmail = ""

# MySQL configs
app.config['MYSQL_DATABASE_USER'] = 'kkuenste'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pw'
app.config['MYSQL_DATABASE_DB'] = 'teamnull'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

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

	if _email and _password:
		cursor.callproc('sp_verifyUser', (_email, _password))
		data = cursor.fetchall()
		
		if len(data) is 0:
			conn.commit()

		print data[0][0]
		print type(data[0][0])
		if data[0][0] == 1:
			return redirect(url_for('stream'))
		else:
			message = "Username or password is not correct. Please try again."
			return make_response(message,200,headers)
			


@app.route('/showSignUp')
def showSignUp():
	return render_template('signup.html')


@app.route('/signUp', methods=['POST'])
def signUp():
	_fname = request.form['inputFirstName']
	_lname = request.form['inputLastName']
	_email = request.form['inputEmail']
	_password = request.form['inputPassword']
	
	if _fname and _lname and _email and _password:
                cursor.callproc('sp_createUser', (_fname, _lname, _email, _password))
                data = cursor.fetchall()
                if len(data) is 0:
                        conn.commit()

                return json.dumps({'html':'<span>All fields pass.</span>'})
	else:
		return json.dumps({'html':'<span>Enter the required fields</span>'})	



@app.route('/showAccount')
def showAccountDetails():        
	return render_template('account.html')

@app.route('/savePassword', methods=['POST'])
def savePassword():
        _email = request.form['inputEmail']
        _pass = request.form['inputPassword']

	if _email and _pass:
		cursor.callproc('sp_updatePassword', (_email, _pass))
               	data = cursor.fetchall()
                if len(data) is 0:
                        conn.commit()

                return json.dumps({'html':'<span>All fields pass.</span>'})
        else:
                return json.dumps({'html':'<span>Enter the required fields</span>'})



@app.route('/deleteUser', methods=['POST'])
def deleteUser():
        _email = request.form['inputEmail2']

        if _email:
                cursor.callproc('sp_deleteUser', (_email,))
                data = cursor.fetchall()
                if len(data) is 0:
                        conn.commit()

                return json.dumps({'html':'<span>All fields pass.</span>'})
        else:
                return json.dumps({'html':'<span>Enter the required fields</span>'})



@app.route('/showNames', methods=['POST'])
def showNames():

        headers = {'Content-Type': 'text/html'}
        _name = request.form['inputName']

        if _name:
                cursor.callproc('sp_returnNames', (_name,))
                data = cursor.fetchall()
                message = data
                if len(data) is 0:
                        conn.commit()


                return make_response(_name,200,headers)
                #flash(json.dumps(data))
                #return render_template('account.html')
                #return redirect(url_for('displayNames', name=_name))


@app.route('/displayNames', methods=['GET'])
def displayNames():
        headers = {'Content-Type': 'text/html'} 
        return make_response(render_template("account.html", data=request.args.get('name')), 200, headers)
        #return render_template("account.html", data=request.args.get('name'))


@app.route('/stream', methods=['GET'])
def simpleStream():
	return render_template('stream.html')



'''
@app.route('/showNames', methods=['GET'])
def showNames()
        print("EHERE")
        return render_template('test.html')


        _name = request.form['inputName']
        if _name:
                cursor.callproc('sp_returnNames', (_name,))
                data = cursor.fetchall()
                if len(data) is 0:
                        conn.commit()
                        

                #return json.dumps({'html':'<span>All fields pass.</span>'})
        else:
                return json.dumps({'html':'<span>Enter the required fields</span>'})


        return render_template('test.html')#, data='hey')
'''
if __name__ == "__main__":
	app.run()
