# -*- coding:utf8 -*-
from flask import Flask, render_template
# from flask_socketio import SocketIO, emit, disconnect
app = Flask(__name__)
# socketio = SocketIO(app, async_mode=None) 
from python.home import views
from python.paper import views
from python.news import views
from python.patent import views
from python.video import views
from python.config import views
@app.errorhandler(404)  
def page_not_found(e):  
	return render_template('404.html'), 404 
