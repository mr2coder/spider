# -*- coding:utf8 -*-
from web import app
from flask import request, session, g, redirect, url_for, abort, render_template, flash, jsonify
#from web.python.paper import models
from datetime import datetime

@app.route('/config')
def config():
	#paper spider setting
	if not session.get('logged_in'):
		return redirect(url_for('login'))
	return render_template('/config/index.html')

@app.route('/test')
def test():
	#paper spider setting
	return render_template('/config/test1.html')

@app.route('/test1')
def ex():
	#paper spider setting
	return render_template('/config/test2.html')

@app.route('/open_file' ,methods=['POST'])
def open_file():
	#paper spider setting
	#site = str(request.form.get('site')).replace("\"", '/')
	#site='/paper/index.html'
	#return render_template(site)
	site = str(request.form.get('site'))
	print(site)
	site = site.replace("\\", '/')
	print(site)
	filename = '/home/zjun/Desktop/MyCode/yang/web/templates/config/abc.txt' # txt文件和当前脚本在同一目录下，所以不用写具体路径
	
	pos = []
	Efield = []
	file_content = []
	try:
		with open(filename) as file_to_read:
			# while True:
			# 		lines = file_to_read.readline() # 整行读取数据
			# 		if not lines:
			# 			break
			# 			pass
			# 		file_content.append(lines)
			file_content = file_to_read.read() 
		print(file_content.strip())
		return file_content.strip()
	except Exception as e :
		print(str(e))
		return "hello world"



if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'filesystem'
	app.debug = True
	app.run(host='0.0.0.0')




