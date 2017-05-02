# -*- coding:utf8 -*-
from web import app
from flask import request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from web.python.home import models

# app.secret_key = "super secret key"
app.config['USERNAME'] = 'zjun'
app.config['PASSWORD'] = '1111'

# app.config.from_envvar('SETTINGS', silent=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	# pprint.pprint(sys.modules)
	if request.method == 'POST':
		# return "app.config['USERNAME']"
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			return redirect(url_for('index'))
	return render_template('/login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/index')
def index():
	#the login page
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	datas = models.get_collections()
	keywords = models.paper_statistic(0,28,'keywords')
	return render_template('/home/index.html',info={'datas':datas,'keywords':keywords})



if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'filesystem'
	app.debug = True
	app.run(host='0.0.0.0')




