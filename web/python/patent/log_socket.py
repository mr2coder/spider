# -*- coding:utf8 -*-
from web import app,socketio
from flask_socketio import emit, disconnect
from web.python.utils.patent_url_spider import auto_click as target

# def target(url,socketio):
# 	while True:
# 		socketio.sleep(1)
# 		socketio.emit('my_response',
# 			{'data': '免费代理获取中  \n这可能花费几分钟，请稍后...'},
# 			namespace='/patent')
#开始链接
back_thread = None
@socketio.on('connect', namespace='/patent')
def test_connect():
	emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('message', namespace='/patent')
def run(message):
	global back_thread
	if back_thread==None:
		back_thread = socketio.start_background_task(target=target,
			id=message,socketio=socketio,proxy=False)

#断开链接
@socketio.on('disconnect', namespace='/patent')
def disconnect_request():
	global back_thread
	if back_thread!=None:
		back_thread.kill()
		back_thread = None
	emit('disconnect', {'data': 'disconnect', 'count': 0})
	print('my name is disconnnect')
	disconnect()
	

