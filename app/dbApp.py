from flask import Flask, render_template, request, json
app = Flask(__name__)

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


if __name__ == "__main__":
	app.run()
