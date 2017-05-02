# -*- coding:utf8 -*-
import sys,pprint
from mongo import mongoConnection
from python.setting import *
import requests
from lxml import html
import re,time,datetime
import collections
import copy
from itertools import repeat
from multiprocessing.dummy import Pool as ThreadPool	
import threading
import subprocess
from bson.objectid import ObjectId
	
def get_count(**kwargs):
	#default collection:patent_new
	#get collection's item num
	patent = mongoConnection.mongoConnection(**kwargs)
	result = patent.collection.count()
	return result

def get_collections(**kwargs):
	patent = mongoConnection.mongoConnection(**kwargs)
	collections =  patent.db.collection_names()
	collections.remove('system.indexes')
	data = [{'collection':x,'count':patent.db[x].count()} for x in collections]
	return data

def patent_add_item(**kwargs):
	"""
	add task, don't ask me why use dict as the param... 
	just because it's more shorter.
	"""
	try:
		patent = mongoConnection.mongoConnection(db='patent',collection='spider')
		tag = patent.collection.insert(kwargs)
		return tag
	except Exception as e:
		print(e)
		return None

def already_exist_data():
	#get query task list
	mongo = mongoConnection.mongoConnection(db='patent',collection='spider')
	info = mongo.collection.find({})
	info = [x for x in info]
	#get related count
	mongo = mongoConnection.mongoConnection(db='patent',collection='patentinfo')
	find = mongo.collection.find #function reference
	for x in info:
		x['_id'] = str(x['_id'])
		x['count'] = find({'spider_id':x['_id']},{'_id':0}).count()
	return info

def task_tr_click(spider_id):
	mongo = mongoConnection.mongoConnection(db='patent',collection='patentinfo')
	info = mongo.collection.find({'spider_id':spider_id},{'spidertime':1})
	info = dict(collections.Counter([str(x['spidertime'].split(' ')[0]) for x in info]))
	#time
	oneday = datetime.timedelta(days=1) 
	now = datetime.date.today()
	x_value = [str(now-oneday*x) for x in range(30)]
	x_value.reverse()
	y_value = []
	for x in x_value:
		value = info.get(x)
		if value==None:
			y_value.append(0)
		else:
			y_value.append(value)
	xy_value = {'y_value':y_value,'x_value':x_value}
	content = list(mongo.collection.find({'spider_id':spider_id},{'_id':0}))
	return {'xy_value':xy_value,'content':content}

def patent_delete_task(spider_id):
	try:
		#delete spider information
		mongo = mongoConnection.mongoConnection(db='patent',collection='spider')
		_ = mongo.collection.remove({'_id':ObjectId(spider_id)})
		#delete ppatentinfo's information
		mongo = mongoConnection.mongoConnection(db='patent',collection='patentinfo')
		_ = mongo.collection.remove({'spider_id':spider_id})
		return 0
	except Exception as e:
		return -1


def download_begin(spider_id):
	try:
		popen = subprocess.Popen(['python','python/utils/patent_url_spider.py','-t','click','-c',spider_id], 
			stdout = subprocess.PIPE)
		return popen
	except Exception as e:
		return -1
	

def download_end(popen):
	try:
		popen.kill()
		return 0
	except Exception as e:
		return -1

if __name__ == '__main__':
	pprint.pprint(sys.path)
	print (TIME)