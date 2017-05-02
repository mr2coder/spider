# -*- coding:utf8 -*-
from web import app
from flask import request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from web.python.paper import models
from datetime import datetime
from web.python.paper import log_socket




@app.route('/api_paper_add_item',methods=['GET', 'POST'])
def api_paper_add_item():
    title = request.form.get('title')
    keyword = request.form.get('keyword')
    abstract = request.form.get('abstract')
    author = request.form.get('author')
    insititution = request.form.get('insititution')
    begin = request.form.get('begin')
    end = request.form.get('end')
    feq = request.form.get('time')
    time = str(datetime.today())
    time = time.split('.')[0]
    para = {'title':title,'keyword':keyword,'abstract':abstract,
    		'author':author,'insititution':insititution,
    		'begin':begin,'end':end,'feq':feq,
    		'status':1,'time':time,'last_time':time}
    info = models.add_item(**para)
    if info==None:return jsonify(None)
    info = models.already_exist_data()
    return jsonify(info)


@app.route('/paper')
def paper():
	#paper spider setting
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	return render_template('/paper/index.html')

@app.route('/api_paper_delete_task',methods=['GET', 'POST'])
def api_paper_delete_task():
	url = request.form.get('url')
	info = models.api_delete_task(url)
	return jsonify(info)

@app.route('/api_paper_task_tr_click',methods=['GET', 'POST'])
def api_paper_task_tr_click():
	#get task information, include graph and detail data
	url = request.form.get('url',0,type=str)
	graph_data = models.task_tr_click(url)
	return jsonify(graph_data)

@app.route('/api_already_exist_data')
def already_exist_data():
	already_exist_data = models.already_exist_data()
	return jsonify(already_exist_data)

@app.route('/api_paper_modify_task', methods=['GET', 'POST'])
def api_paper_modify_task():
	url = request.form.get('url')
	title = request.form.get('title')
	keyword = request.form.get('keyword')
	abstract = request.form.get('abstract')
	author = request.form.get('author')
	insititution = request.form.get('insititution')
	feq = request.form.get('feq')
	time = str(datetime.today())
	time = time.split('.')[0]
	para = {'url':url,'title':title,'keyword':keyword,'abstract':abstract,
			'author':author,'insititution':insititution,'feq':feq,'time':time,'last_time':time}
	info = models.modify_task(**para)
	return jsonify(info)

@app.route('/api_paper_list', methods=['GET', 'POST'])
def paper_list():
	#所选任务下的论文列表查询
	url = request.form.get('url')
	paper_list = models.paper_list(url)
	return jsonify(paper_list)

"""
popen = None
@app.route('/api_paper_download_begin', methods=['GET', 'POST'])
def api_paper_download_begin():
	url = request.form.get('url')
	global popen
	if not popen:
		popen = models.download_begin(url)
	code = -1
	if popen==-1:code = 0
	return jsonify(code)

@app.route('/api_paper_refresh_log', methods=['GET', 'POST'])
def api_paper_refresh_log():
	global popen
	line = popen.stdout.readline()
	data = {}
	data['line'] = line.decode("utf-8")
	return jsonify(data)

@app.route('/api_paper_download_end', methods=['GET', 'POST'])
def api_paper_download_end():
	global popen
	code = models.download_end(popen)
	popen = None
	return jsonify(code)
"""


if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'filesystem'
	app.debug = True
	app.run(host='0.0.0.0')




