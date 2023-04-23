from flask import Flask,request, render_template, flash, redirect, url_for,session, logging, send_file, Response
from flask_mysqldb import MySQL 
from datetime import timedelta, datetime

app = Flask(__name__)
app.secret_key = "yesitisasupersecretkey"

#Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'getitchecked'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#init Mysql
mysql = MySQL(app)


@app.before_request
def make_session_permanent():
	session.permanent = True
	app.permanent_session_lifetime = timedelta(hours=24)
	

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/sregister", methods = ['POST','GET'])
def register():
	if(request.method == 'POST'):
		email = request.form.get('email')
		name = request.form.get('name')
		usn = request.form.get('usn')
		phone = request.form.get('phone')
		password = request.form.get('password')
		branch = request.form.get('branch')
		cur = mysql.connection.cursor()
		cur.execute('INSERT INTO student(name, email, usn, phonenum, password, branch) VALUES(%s,%s,%s,%s,%s,%s)',(name, email, usn, phone, password, branch))
		mysql.connection.commit()
		cur.close()
	return render_template('registerStudent.html')


@app.route('/fregister', methods=['GET', 'POST'])
def fregister():
	if(request.method == "POST"):
		fid = request.form.get('fid')
		name = request.form.get('name')
		email = request.form.get('email')
		phone = request.form.get('phone')
		password = request.form.get('password')
		branch = request.form.get('branch')
		try:
			cur = mysql.connection.cursor()
			cur.execute('INSERT INTO faculty(name, email, facultyId, phonenum, password, branch) VALUES(%s,%s,%s,%s,%s,%s)',(name, email, fid, phone, password, branch))
			mysql.connection.commit()
			cur.close()
		except:
			return redirect(url_for('home'))
		return redirect(url_for('home'))
	return render_template('registerFaculty.html')

@app.route('/slogin', methods = ['GET', 'POST'])
def slogin():
	if(request.method == "POST"):
		email = request.form.get('email')
		password = request.form.get('password')
		cur = mysql.connection.cursor()
		res = cur.execute('SELECT * FROM student WHERE email=%s and password=%s',(email, password))
		mysql.connection.commit()
		cur.close()
		if(res>0):
			return redirect(url_for('home'))
	return render_template('loginFaculty.html')

@app.route('/flogin', methods = ['GET', 'POST'])
def flogin():
	if(request.method == "POST"):
		email = request.form.get('email')
		password = request.form.get('password')
		cur = mysql.connection.cursor()
		res = cur.execute('SELECT * FROM faculty WHERE email=%s and password=%s',(email, password))
		mysql.connection.commit()
		cur.close()
		if(res>0):
			return redirect(url_for('home'))
	return render_template('loginStudent.html')


if(__name__ == '__main__'):
	app.run(debug=True)