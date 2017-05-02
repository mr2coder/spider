# -*- coding:utf8 -*-
from web import app
from flask import request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from web.python.video import models
from datetime import datetime

@app.route('/video')
def video():
	#paper spider setting
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	return render_template('/video/index.html')

@app.route('/api_add_video_spider',methods=['GET', 'POST'])
def api_add_video_spider():
	content = request.form.get('content')
	site = str(request.form.get('site')).replace("\"", '').replace('[','').replace(']','').split(',')
	length = request.form.get('len')
	time_limit = request.form.get('time_limit')
	feq = request.form.get('feq')
	time = str(datetime.today())
	time = time.split('.')[0]
	tag = models.store_spider(content=content, feq=feq, time=time, 
		site=site, length=length, time_limit=time_limit)
	if tag==None:return jsonify(None)
	info = models.initial_spider()
	return jsonify(info)

@app.route('/api_video_initial_spider',methods=['GET', 'POST'])
def api_video_initial_spider():
	info = models.initial_spider()
	return jsonify(info)

@app.route('/api_video_detail')
def api_video_detail():
	content = request.args.get('content')
	site = request.args.get('site')
	info = models.api_video_detail(content,site)
	return jsonify(info)

@app.route('/api_video_gragh')
def api_video_gragh():
	content = request.args.get('content')
	site = request.args.get('site')
	info = models.api_video_gragh(content,site)
	return jsonify(info)

@app.route('/api_play_info',methods=['GET', 'POST'])
def api_play_info():
	videoname = request.args.get('videoname')
	info = models.api_play_info(videoname)
	return jsonify(info)

@app.route('/api_video_delete_task',methods=['GET', 'POST'])
def api_video_delete_task():
	content = request.form.get('content')
	site = request.form.get('site')
	time = request.form.get('time')
	info = models.api_delete_task(content,site,time)
	return jsonify(info)

video_popen = None
@app.route('/api_video_download_begin', methods=['GET', 'POST'])
def api_video_download_begin():
	content = request.form.get('content')
	site = request.form.get('site')
	global video_popen
	if not video_popen:
		video_popen = models.api_video_download_begin(content,site)
	code = -1
	if video_popen==-1:code = 0
	return jsonify(code)

@app.route('/api_video_refresh_log', methods=['GET', 'POST'])
def api_video_refresh_log():
	global video_popen
	line = video_popen.stdout.readline()
	data = {}
	data['line'] = line.decode("utf-8")
	return jsonify(data)

@app.route('/api_video_download_end', methods=['GET', 'POST'])
def api_video_download_end():
	global video_popen
	code = models.api_video_download_end(video_popen)
	video_popen = None
	return jsonify(code)


if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'filesystem'
	app.debug = True
	app.run(host='0.0.0.0')




