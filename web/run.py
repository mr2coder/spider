# -*- coding:utf8 -*-
import sys,os
sys.path.append(os.path.pardir)
path = os.path.abspath(__file__).replace('\\','/').split('/')
sys.path.append('/'.join(path[:-1])+'/python/utils/')

from web import app
app.secret_key = '!@#$%^&*()'
app.config['SESSION_TYPE'] = 'filesystem'
app.debug = True
# socketio = SocketIO(app, async_mode=None)
if __name__ == '__main__':
	# socketio.run(app, debug=True)
	app.run(host='0.0.0.0')