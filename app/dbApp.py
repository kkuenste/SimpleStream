from flask import Flask, render_template, request, json
from flask.ext.mysql import MySQL
app = Flask(__name__)

mysql = MySQL()

# MySQL configs
app.config['MYSQL_DATABASE_USER'] = 'kkuenste'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pw'
app.config['MYSQL_DATABASE_DB'] = 'teamnull'i
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()


@app.route("/main")
def main():
	return render_template('index.html')

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
		return json.dumps({'html':'<span>All fields pass.</span>'})
	else:
		return json.dumps({'html':'<span>Enter the required fields</span>'})	
	cursor.callproc('sp_createUser', (_fname, _lname, _email, _password))
	data = cursor.fetchall()
	if len(data) is 0:
		conn.commit()
		return json.dumps({'message':'User created successfully'})
	else:
		return json.dumps({'error':str(data[0])})


@app.route('/showAccount')
def showAccountDetails():
	return render_template('account.html')


if __name__ == "__main__":
	app.run()
