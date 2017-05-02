# -*- coding:utf8 -*-
from web import app
from flask import request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from web.python.patent import models
from datetime import datetime
import sys



@app.route('/patent_add_item',methods=['GET', 'POST'])
def patent_add_item():
    title = request.form.get('title')
    qwords = request.form.get('qwords')
    author = request.form.get('author')
    insititution = request.form.get('insititution')
    begin = request.form.get('begin')
    end = request.form.get('end')
    feq = request.form.get('time')
    time = str(datetime.today())
    time = time.split('.')[0]
    para = {'title':title,'qwords':qwords,
    		'author':author,'insititution':insititution,
    		'begin':begin,'end':end,'feq':feq,
    		'status':1,'time':time}
    info = models.patent_add_item(**para)
    if info==None:return jsonify(None)
    info = models.already_exist_data()
    return jsonify(info)


@app.route('/patent')
def patent():
	#patent spider setting
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	return render_template('/patent/index.html')

@app.route('/api_patent_delete_task', methods=['GET', 'POST'])
def api_patent_delete_task():
	spider_id = request.form.get('spider_id')
	tag = models.patent_delete_task(spider_id)
	return jsonify(tag)

@app.route('/api_patent_task_tr_click',methods=['GET', 'POST'])
def patent_task_tr_click():
	#get task information, include graph and detail data
	_id = request.form.get('_id',0,type=str)
	graph_data = models.task_tr_click(_id)
	return jsonify(graph_data)

@app.route('/api_patent_already_exist_data')
def patent_already_exist_data():
	already_exist_data = models.already_exist_data()
	return jsonify(already_exist_data)


popen = None
@app.route('/api_patent_download_begin', methods=['GET', 'POST'])
def api_patent_download_begin():
	spider_id = request.form.get('_id')
	global popen
	if not popen:
		popen = models.download_begin(spider_id)
	code = -1
	if popen==-1:code = 0
	return jsonify(code)

@app.route('/api_patent_refresh_log', methods=['GET', 'POST'])
def api_patent_refresh_log():
	global popen
	line = popen.stdout.readline()
	data = {}
	data['line'] = line.decode("utf-8")
	return jsonify(data)

@app.route('/api_patent_download_end', methods=['GET', 'POST'])
def api_patent_download_end():
	global popen
	code = models.download_end(popen)
	popen = None
	return jsonify(code)



if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'filesystem'
	app.debug = True
	app.run(host='0.0.0.0')




