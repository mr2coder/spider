# -*- coding:utf8 -*-
import sys,pprint
from mongo import mongoConnection
from python.setting import *
import subprocess
import re,time,datetime
import collections



def store_spider(**kwargs):
	"""
	"""
	try:
		mongoDB = mongoConnection.mongoConnection(db='video',collection='spider')
		if not isinstance(kwargs['site'], list):kwargs['site'] = [kwargs['site']]
		infomations = [{'content':kwargs['content'],'status':1, 
		'site':site, 'feq':kwargs['feq'], 'length':kwargs['length'],'time_limit':kwargs['time_limit'],
		'time':kwargs['time'],'last_time':kwargs['time'],'inactive':0 } 
								for site in kwargs['site']]
		infomation_id = mongoDB.collection.insert_many(infomations, ordered=False)
		return infomation_id
	except Exception as e:
		print (e)
		return None
	



def initial_spider():
	mongo = mongoConnection.mongoConnection(db='video',collection='spider')
	info = mongo.collection.find({},{'_id':0})
	info = [x for x in info]
	return info

def api_video_detail(content, site):
	mongo = mongoConnection.mongoConnection(db='video',collection='urlinfo')
	info = mongo.collection.find({'content':content,'site':site},{'_id':0})
	info = [x for x in info]
	return {'info':info}

def api_video_gragh(content, site):
	mongo = mongoConnection.mongoConnection(db='video',collection='urlinfo')
	info = mongo.collection.find({'content':content,'site':site},{'spidertime':1})
	info = dict(collections.Counter([str(x['spidertime'].split(' ')[0]) for x in info]))
	#time
	oneday = datetime.timedelta(days=1) 
	now = datetime.date.today()
	x_value = [str(now-oneday*x) for x in range(120)] #display 120days data
	x_value.reverse()
	y_value = []
	for x in x_value:
		value = info.get(x)
		if value==None:
			y_value.append(0)
		else:
			y_value.append(value)
	xy_value = {'y_value':y_value,'x_value':x_value}
	return {'xy_value':xy_value,'content':content}

def api_delete_task(content,site,time):
	try:
		#delete spider information
		mongo = mongoConnection.mongoConnection(db='video',collection='spider')
		_ = mongo.collection.remove({'content':content,'site':site,'time':time})
		#delete urlinfo information
		mongo = mongoConnection.mongoConnection(db='video',collection='urlinfo')
		_ = mongo.collection.remove({'content':content,'site':site})
		return 0
	except Exception as e:
		return -1

def api_video_download_begin(content,site):
	try:
		popen = subprocess.Popen(['python', 
			'python/utils/video_url_spider.py','-t','click','-c',content,'-s',site],
			stdout = subprocess.PIPE)
		return popen
	except Exception as e:
		return -1
	

def api_video_download_end(popen):
	try:
		popen.kill()
		return 0
	except Exception as e:
		return -1


if __name__ == '__main__':
	mongo = mongoConnection(db='video',collection='spider')


