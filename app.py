from flask import Flask,request, render_template, flash, redirect, url_for,session, logging, send_file, Response
from flask_mysqldb import MySQL 
from datetime import timedelta, datetime
from werkzeug.utils import secure_filename
import os
import plagcheck
import webbrowser

app = Flask(__name__)
app.secret_key = "yesitisasupersecretkey"

#Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'getitchecked'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SESSION_TYPE'] = 'filesystem'

#init Mysql
mysql = MySQL(app)

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')

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
		try:
			cur = mysql.connection.cursor()
			cur.execute('INSERT INTO student(name, email, usn, phonenum, password, branch) VALUES(%s,%s,%s,%s,%s,%s)',(name, email, usn, phone, password, branch))
			mysql.connection.commit()
			cur.close()
			message = 'Successfully Registered'
			flash(message,'success')
			return render_template('registerStudent.html')
		except:
			message='Cannot Register!! please login if already registered'
			flash(message,'error')
			return render_template('registerStudent.html')
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
			message = 'Successfully Registered'
			flash(message,'success')
			return render_template('registerFaculty.html')
		except:
			message='Cannot Register!! please login if already registered'
			flash(message,'error')
			return render_template('registerFaculty.html')
	return render_template('registerFaculty.html')

@app.route('/slogin', methods = ['GET', 'POST'])
def slogin():
	if(request.method == "POST"):
		email = request.form.get('email')
		password = request.form.get('password')
		cur = mysql.connection.cursor()
		res = cur.execute('SELECT * FROM student WHERE email=%s and password=%s',(email, password))
		mysql.connection.commit()
		if(res>0):
			session['login'] = True
			session['user'] = 'stu'
			session['stuid'] = cur.fetchall()[0]['usn']
			cur.close()
			return redirect(url_for('home'))
	return render_template('loginStudent.html')

@app.route('/flogin', methods = ['GET', 'POST'])
def flogin():
	if(request.method == "POST"):
		email = request.form.get('email')
		password = request.form.get('password')
		cur = mysql.connection.cursor()
		res = cur.execute('SELECT * FROM faculty WHERE email=%s and password=%s',(email, password))
		mysql.connection.commit()
		if(res>0):
			session['login'] = True
			session['user'] = 'fac'
			session['facid'] = cur.fetchall()[0]['facultyId']
			return redirect(url_for('home'))
		cur.close()
	return render_template('loginFaculty.html')

@app.route('/addassign', methods=['GET', 'POST'])
def addassign():
	if(request.method == "POST" and session['user'] and session['user']=='fac'):
		try:
			id = request.form.get('id')
			scheme = request.form.get('scheme')
			sem = request.form.get('sem')
			sub_code =  request.form.get('sub_code')
			file = request.files['file']
			filename =  file.filename
			path = os.path.join(BASE_DIR, filename)
			file.save(os.path.join(BASE_DIR, filename))
			last_date = request.form.get('last')
			facid = session['facid']
			cur = mysql.connection.cursor()
			res = cur.execute('INSERT INTO assignment(id, facultyId, path, scheme, sem, sub_code, last_date) VALUES(%s, %s, %s, %s, %s, %s, %s)', (id, facid, path, scheme, sem, sub_code, last_date))
			mysql.connection.commit()
			cur.close()
			if(res>0):
				return redirect(url_for('home'))
		except:
			flash('error uploading assignment try again', 'error')
	return render_template('uploadFaculty.html')

@app.route('/assigntype', methods=['GET', 'POST'])
def assigntype():
	if(request.method=='POST' and session['login'] and session['user']=='stu'):
		atype = request.form.get('type')
		if(atype=='uni'):
			return redirect(url_for('unique'))
		elif(atype=='com'):
			return redirect(url_for('common'))
	return render_template('assignType.html')

@app.route('/unique', methods=['GET', 'POST'])
def unique():
	cur = mysql.connection.cursor()
	cur.execute('SELECT id from assignment')
	reslt = cur.fetchall()
	mysql.connection.commit()
	cur.close()
	if(request.method == "POST" and session['user'] and session['user']=='stu'):
		try:
			scheme = request.form.get('scheme')
			sem = request.form.get('sem')
			subcode = request.form.get('subcode')
			file = request.files['file']
			filename =  file.filename
			path = os.path.join(BASE_DIR, filename)
			file.save(os.path.join(BASE_DIR, filename))
			usn = session['stuid']
			aid = request.form.get('aid')
			cur = mysql.connection.cursor()
			res = cur.execute('SELECT upload.path FROM upload, assignment where upload.aid=assignment.id and assignment.scheme=%s and assignment.sem=%s and assignment.sub_code=%s',(scheme, sem, subcode))
			mysql.connection.commit()
			if(res>0):
				plagcheck.writeTextUser(path)
				paths = cur.fetchall()
				for i in paths:
					print(i)
					plagcheck.writeTextFaculty(i['path'])
					check = plagcheck.Check_Plagiarism('user.txt','faculty.txt')
					if(check>50):
						flash('Cannot upload pdf due to plagiarism','error')
						return redirect(url_for('unique'))

				res = cur.execute('INSERT INTO upload(aid, usn, path, type) VALUES(%s, %s, %s, %s)', (aid, usn, path, 'unique'))
				mysql.connection.commit()
				cur.close()
				if(res>0):
					flash('Uploaded successfully')
					return redirect(url_for('home'))
			else:
				res = cur.execute('INSERT INTO upload(aid, usn, path, marks, type) VALUES(%s, %s, %s, %s, %s)', (aid, usn, path, 10, 'unique'))
				mysql.connection.commit()
				cur.close()
				if(res>0):
					flash('Uploaded successfully')
					return redirect(url_for('home'))
		except:
			flash('Error uploading file', 'error')
	return render_template('uploadu.html', res=reslt)

@app.route('/common', methods=['GET', 'POST'])
def common():
	cur = mysql.connection.cursor()
	cur.execute('SELECT id from assignment')
	reslt = cur.fetchall()
	mysql.connection.commit()
	cur.close()
	if(request.method == "POST" and session['user'] and session['user']=='stu'):
		try:
			scheme = request.form.get('scheme')
			sem = request.form.get('sem')
			subcode = request.form.get('subcode')
			file = request.files['file']
			filename =  file.filename
			path = os.path.join(BASE_DIR, filename)
			file.save(os.path.join(BASE_DIR, filename))
			usn = session['stuid']
			aid = request.form.get('aid')
			cur = mysql.connection.cursor()
			res = cur.execute('SELECT assignment.path FROM assignment where assignment.id=%s and assignment.scheme=%s and assignment.sem=%s and assignment.sub_code=%s',(aid, scheme, sem, subcode))
			mysql.connection.commit()
			if(res>0):
				mks = []
				plagcheck.writeTextUser(path)
				paths = cur.fetchall()
				for i in paths:
					print(i)
					plagcheck.writeTextFaculty(i['path'])
					check = plagcheck.Check_Plagiarism('user.txt','faculty.txt')
					mk = plagcheck.autoMarkAssign(check)
					mks.append(mk)
				maxmks = min(mks)
				res = cur.execute('INSERT INTO upload(aid, usn, path, marks, type) VALUES(%s, %s, %s, %s, %s)', (aid, usn, path, maxmks, 'common'))
				mysql.connection.commit()
				cur.close()
				if(res>0):
					flash('Uploaded successfully')
					return redirect(url_for('home'))
			else:
				res = cur.execute('INSERT INTO upload(aid, usn, path, marks, type) VALUES(%s, %s, %s, %s, %s)', (aid, usn, path, 10, 'common'))
				mysql.connection.commit()
				cur.close()
				if(res>0):
					flash('Uploaded successfully')
					return redirect(url_for('home'))
		except:
			flash('Error uploading file', 'error')
	return render_template('uploadc.html', res=reslt)


@app.route('/viewmarks', methods=['GET', 'POST'])
def viewmarks():
	if(session['user'] == 'fac'):
		cur = mysql.connection.cursor()
		cur.execute('SELECT upload.usn as usn, student.name as name, upload.marks as marks, upload.type as type, assignment.sub_code as subcode, upload.path as path FROM assignment, upload, student where assignment.id=upload.aid and student.usn=upload.usn')
		mysql.connection.commit()
		res = cur.fetchall()
		li = []
		idx=-1
		flag=0
		for i in res:
			if(len(li)==0):
				idx+=1
				li.append(i['subcode'])
			else:
				for j in li:
					if(i['subcode'] in j):
						flag=1
						break
				if(flag == 0):
					idx+=1
					li.append(i['subcode'])
		cur.close()
		if(request.method == 'GET'):
			scheme = request.args.get('scheme')
			# cur = mysql.connection.cursor()
			# cur.execute('SELECT upload.usn as usn, student.name as name, upload.marks as marks, upload.type as type FROM assignment, upload, student where assignment.id=upload.aid and student.usn=upload.usn and assignment.scheme=%s',(scheme))
			# mysql.connection.commit()
			cur = mysql.connection.cursor()
			cur.execute('SELECT upload.usn as usn, student.name as name, upload.marks as marks, upload.type as type, assignment.sub_code as subcode, upload.path as path FROM assignment, upload, student where assignment.id=upload.aid and student.usn=upload.usn and assignment.sub_code=%s',[scheme])
			mysql.connection.commit()
			res = cur.fetchall()
			cur.close()
			return render_template('marksConnect.html',res=res, li=li)
		return render_template('marksConnect.html',res=res, li=li)
	# return render_template('marksConnect.html')

@app.route('/assignopt', methods=['GET', 'POST'])
def assignopt():
	if(request.method == 'POST'):
		opt = request.form.get('opt')
		if(opt == 'View'):
			usn = session['stuid']
			cur = mysql.connection.cursor()
			cur.execute('SELECT * from upload where usn=%s', [usn])
			mysql.connection.commit()
			res = cur.fetchall()
			cur.close()
			return render_template('marksview.html',res=res)
		elif(opt == 'Upload'):
			return redirect(url_for('assigntype'))
	return render_template('option.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if(__name__ == '__main__'):
	app.run(debug=True)