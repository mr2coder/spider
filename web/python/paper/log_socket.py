# -*- coding:utf8 -*-
from web import app
from flask_socketio import SocketIO, emit, disconnect
socketio = SocketIO(app)

#socket area
def log_socket():
	#手动出发爬虫，输出信息返回客户端
	count = 0
	while True:
		socketio.sleep(1)
		socketio.emit('my_response',
			{'data': 'Server generated event', 'count': count},
			namespace='/runtinme_log')
		count += 1
#开始链接
back_thread = None
@socketio.on('connect', namespace='/runtinme_log')
def test_connect():
	global back_thread
	if back_thread==None:
		back_thread = socketio.start_background_task(target=log_socket)
	emit('my_response', {'data': 'Connected', 'count': 0})
	return None

#断开链接
@socketio.on('disconnect_paper', namespace='/runtinme_log')
def disconnect_request():
	global back_thread
	if back_thread!=None:
		back_thread.kill()
		back_thread = None
	# disconnect()
	return False
	

