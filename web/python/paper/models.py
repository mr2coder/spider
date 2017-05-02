# -*- coding:utf8 -*-
import sys,pprint
from mongo import mongoConnection
import subprocess
from python.setting import *
import requests
from lxml import html
import re,time,datetime
import collections
import copy
from itertools import repeat
from multiprocessing.dummy import Pool as ThreadPool	
import threading
WANFANG_BASE_URL = 'http://s.wanfangdata.com.cn/Paper.aspx?q='

def db_find(key):
	wanFang = mongoConnection.mongoConnection()
	result = wanFang.collection.find({},{key:1})
	return result

def paper_statistic(begin,end,key):
	key_words = db_find(key)
	key_dict = {}
	for line in key_words:
		if not isinstance(line[key],list):
			x = line[key]
			if key_dict.get(x):
				key_dict[x] +=1
			else:
				key_dict[x] = 1
		else:
			for x in line[key]:
				if key_dict.get(x):
					key_dict[x] +=1
				else:
					key_dict[x] = 1
			
	c = sorted(key_dict.items(), key=lambda d:d[1],reverse=True)
	# for x in c[begin:end]:
	# 	print x[0],x[1]
	return c[begin:min(end,len(c))]


def url_constract(**kwargs):
	#build wanfang's search url
	url = WANFANG_BASE_URL
	if kwargs.get('title'):
		url += ' 题名:{0}'.format(kwargs.get('title'))
	if kwargs.get('keyword'):
		url += ' 关键词:{0}'.format(kwargs.get('keyword'))
	if kwargs.get('abstract'):
		url += ' 摘要:{0}'.format(kwargs.get('abstract'))
	if kwargs.get('author'):
		url += ' 作者:{0}'.format(kwargs.get('author'))
	if kwargs.get('insititution'):
		url += ' 作者单位:{0}'.format(kwargs.get('insititution'))
	if kwargs.get('begin') or kwargs.get('end'):
		url += ' 日期:{0}-{1}'.format(kwargs.get('begin'),kwargs.get('end'))
	return url

def sorted_by_times(ls):
	out_dict = {}
	for line in ls:
		if out_dict.get(line):
			out_dict[line] +=1
		else:
			out_dict[line] = 1
	c = sorted(out_dict.items(), key=lambda d:d[1],reverse=True)
	return c

		
def get_count(**kwargs):
	#default collection:paper_new
	#get collection's item num
	wanFang = mongoConnection.mongoConnection(**kwargs)
	result = wanFang.collection.count()
	return result

def get_collections(**kwargs):
	wanFang = mongoConnection.mongoConnection(**kwargs)
	collections =  wanFang.db.collection_names()
	collections.remove('system.indexes')
	data = [{'collection':x,'count':wanFang.db[x].count()} for x in collections]
	return data

def api_delete_task(url):
	try:
		#delete spider information
		mongo = mongoConnection.mongoConnection(db='wanFang',collection='spider')
		_ = mongo.collection.remove({'url':url})
		#delete paperinfo's information
		mongo = mongoConnection.mongoConnection(db='wanFang',collection='paperinfo')
		_ = mongo.collection.remove({'url':url})
		return 0
	except Exception as e:
		return -1

def add_item(**kwargs):
	"""
	add  task, don't ask me why use dict as the param... 
	just because it's more shorter.
	"""
	try:
		wanFang = mongoConnection.mongoConnection(db='wanFang',collection='spider')
		url = url_constract(**kwargs)
		kwargs['url'] = url
		tag = wanFang.collection.insert(kwargs)
		return tag
	except Exception as e:
		print(e)
		return None

def already_exist_data():
	#get query task list
	mongo = mongoConnection.mongoConnection(db='wanFang',collection='spider')
	info = mongo.collection.find({},{'last_time':1,'url':1,'time':1,'feq':1,'_id':0})
	info = [x for x in info]
	#get related count
	mongo = mongoConnection.mongoConnection(db='wanFang',collection='paperinfo')
	find = mongo.collection.find #function reference
	for x in info:x['count'] = find({'url':x['url']}).count()
	return info

def task_tr_click(url):
	mongo = mongoConnection.mongoConnection(db='wanFang',collection='paperinfo')
	info = mongo.collection.find({'url':url},{'spidertime':1})
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
	mongo = mongoConnection.mongoConnection(db='wanFang',collection='spider')
	content = list(mongo.collection.find({'url':url},{'_id':0}))
	
	if len(content)>0:
		content = content[0]
	return {'xy_value':xy_value,'content':content}

def modify_task(**kwargs):
	#modify task
	o_url = kwargs['url']
	url = url_constract(**kwargs)
	mongo = mongoConnection.mongoConnection(db='wanFang',collection='spider')
	feq = list(mongo.collection.find({'url':o_url},{'feq':1,'_id':0}))[0]
	if_exist = mongo.collection.find({'url':url}).count()
	if if_exist!=0 and feq['feq'] == kwargs['feq']:return None
	kwargs['url'] = url
	if url!=o_url:
		i_tag = mongo.collection.insert(kwargs)
		# r_tag = mongo.collection.remove({'url':o_url}) #逻辑问题,旧有的任务会造成paper悬空,因此暂时不删除原有任务
	else:
		mongo.collection.update({'url':url},{"$set":{"feq":kwargs['feq']}})
	return 0

def paper_list(url):
	#根据task的url查询关于次url的所有文章，返回dict，
	mongo = mongoConnection.mongoConnection(db='wanFang',collection='paperinfo')
	info = mongo.collection.find({'url':url},{'_id':0,
		'spidertime':1,'title':1,'link':1,'abstract':1,'authors':1,'date':1})
	info = [x for x in info]
	for line in info:
		line['authors'] = list(line['authors'].keys())
		line['abstract'] = line['abstract']['Chinese']
		if line['date']:
			line['date'] = line['date'].get('year')
	return info

def download_begin(url):
	try:
		print(url)
		popen = subprocess.Popen(['python','python/utils/paper_url_spider.py','-t','click','-c',url], 
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