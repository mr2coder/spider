# -*- coding:utf8 -*-
# from mongo import mongoConnection

from spider import urlSpider
import requests
from lxml import html
import re,time,datetime
from multiprocessing.dummy import Pool as ThreadPool	
import argparse
import os
from iqiyi import *


#add sys.path
import logging.config
path = os.path.abspath(__file__).replace('\\','/').split('/')

logfile = os.path.join( '/'.join(path[:-4]),"logger.conf")
logging.config.fileConfig(logfile)
logger = logging.getLogger("video")
#add sys.path
import sys
sys.path.append('/'.join(path[:-3]))
from mongo import mongoConnection




def url_spider(kwargs,socketio=None):
	logger.info('target site:{}, spider begin...'.format(kwargs['site']))
	# if 'youtube' in kwargs['site']:
	# 	youtube_url_spider(kwargs['content'],socketio=socketio)
	if 'sina' in kwargs['site']:
		sina_url_spider(kwargs['content'],socketio=socketio)
	if 'bilibili' in kwargs['site']:
		iqiyi_url_spider(kwargs['content'],site='bilibili',socketio=socketio)
	if 'youku' in kwargs['site']:
		iqiyi_url_spider(kwargs['content'],site='youku',socketio=socketio)
	if 'iqiyi' in kwargs['site']:
		iqiyi_url_spider(kwargs['content'],socketio=socketio)
	if 'qq' in kwargs['site']:
		iqiyi_url_spider(kwargs['content'],site='qq',socketio=socketio)
	if 'acfun' in kwargs['site']:
		iqiyi_url_spider(kwargs['content'],site='acfun',socketio=socketio)
	if 'ifeng' in kwargs['site']:
		iqiyi_url_spider(kwargs['content'],site='ifeng',socketio=socketio)
	if 'cntv' in kwargs['site']:
		iqiyi_url_spider(kwargs['content'],site='cntv',socketio=socketio)
	if 'm1905' in kwargs['site']:
		iqiyi_url_spider(kwargs['content'],site='m1905',socketio=socketio)
	if 'tudou' in kwargs['site']:
		iqiyi_url_spider(kwargs['content'],site='tudou',socketio=socketio)
	if 'souhu' in kwargs['site']:
		iqiyi_url_spider(kwargs['content'],site='souhu',socketio=socketio)


def youtube_url_spider(content,socketio=None):
	base_url = 'https://www.youtube.com/results?search_query='
	url = base_url+content
	response = requests.get(url)
	if response.status_code!=200:
		return False
	doc = html.fromstring(response.text)
	mongoDB = mongoConnection.mongoConnection(db='video',collection='spider')


#==================bilibili==============
def get_bilibili_pagenums(response,socketio=None):
	"""
	Gets the number of pages of content
	"""
	try:
		json = response.json()
		page_num = json['numPages']
		logger.info(page_num)
		return page_num
	except Exception as e:
		logger.debug (e)
		return None

def get_bilibili_info(args,socketio=None):
	"""
	"""
	try:
		url = args[0]
		logger.info(url)
		content = args[1]
		sesson = None
		if not sesson:response = requests.get(url)
		else :response = sesson.get(url)
		if response.status_code!=200: return None
		json = response.json()
		doc = html.fromstring(json['html'])
		#Information extraction
		urls = doc.xpath("//li/a/@href")
		names = doc.xpath("//li/a/@title")
		infos = doc.xpath("//li/div/div[@class='des hide']/text()")
		playtimes = [x.strip() for x in doc.xpath("//li/div/div[@class='tags']/span[@class='so-icon watch-num']/text()")[1::2]]
		showtimes = [x.strip() for x in doc.xpath("//li/div/div[@class='tags']/span[@class='so-icon time']/text()")[1::2]]
		authors_sites = re.compile(r'http://space.bilibili.com/[0-9]{0,}').findall(response.text)
		times = []
		for x in playtimes:
			if x[-1]== u'万':
				temp = int(float(x[:-1])*10000)
			elif x[-1]== '-':
				temp = 0
			else:
				temp = int(x)
			times.append(temp)
		
		result = [{"videoname":x[0].strip(),
					"url":x[1],
					"showtime":x[2],
					"videoinfo":x[3].strip(),
					"playtimes":x[4],
					"spidertime":time.strftime( '%Y-%m-%d %X', time.localtime()),
					"site":"sina",
					"content":content,
					"status":1,
					"authors_site":x[5] } for x in zip(names, urls, showtimes, infos, times, authors_sites)]
		# pprint.pprint (len(result))
		# assert 1==2
		mongoDB = mongoConnection.mongoConnection(db='video',collection='urlinfo')
		infomation_id = mongoDB.collection.insert_many(result, ordered=False)
	except Exception as e:
		logger.debug(e)
	

def bilibili_url_spider(content,socketio=None):
	patt = "http://search.bilibili.com/ajax_api/video?keyword={content}&page={page}&duration={duration}"
	patt_para = {'content':content, 'page':'1', 'duration':"1"}
	spider = urlSpider(patt, patt_para)
	page_num_code = spider.get_page_num(get_bilibili_pagenums)
	# print (spider.__pagenums)
	page_num_code and spider.url_info_spider(get_bilibili_info)

#========================iqiyi=======================
	
#=========================sina========================
def sina_url_spider(content,socketio=None):
	try:
		thread_num = 1
		patt = "http://so.video.sina.com.cn/interface/s?from=video&wd={content}&s_id=w00001&p={page}&n=20"
		start_url = patt.format(content=str(content), page='1')
		response = requests.get(start_url)
		if response.status_code!=200:
			logger.info('Error:Network connect failed!')
			logger.info('Please make sure your computer can access the site')
			return None
		json_data = response.json()
		total_num = json_data["total"]
		logger.info('total items:'+str(total_num))
		if socketio:
			socketio.sleep(1)
			socketio.emit('my_response',
				{'data': 'total items:'+str(total_num)},
				namespace='/video')
		#get url's detail infomation
		def get_info(url):
			logger.info('Currently crawling web pages is: '+url)
			if socketio:
				socketio.emit('my_response',
					{'data': 'Currently crawling web pages is: '+url},
					namespace='/video')
				socketio.sleep(1)
			response = requests.get(url)
			if response.status_code!=200: return None
			result = [{"videoname":re.compile(r'(<.*?>)').sub("",x.get("videoname")),
						"url":x.get("url"),
						"showtime":x.get("showtime"),
						"videoinfo":x.get("videoinfo"),
						"playtimes":x.get("playtimes"),
						"spidertime":time.strftime( '%Y-%m-%d %X', time.localtime()),
						"site":"sina",
						"content":content,
						"status":1 } for x in response.json()["list"]]
			mongoDB = mongoConnection.mongoConnection(db='video',collection='urlinfo')
			try:
				infomation_id = mongoDB.collection.insert_many(result, ordered=False)
				mongoDB.db['spider'].update({'site':'sina','content':content},{'$set':{'inactive':0}})
			except Exception as e:
				logger.debug(e)
			return 0
		#creat all page url
		urls = [patt.format(content=content, page=str(x+1)) for x in range((int(total_num)+19)//20)]
		if socketio:
		 	for url in urls:
		 	 	get_info(url) 
		else:
			pool = ThreadPool(thread_num)
			results = pool.map(get_info, urls)
		logger.info('Success: Task update finshed..')
	except Exception as e:
		logger.debug(e)


def youku_url_spider(content):
	pass

def click(content,site,socketio=None,proxy=False):
	args = {}
	logger.info(content+':'+site)
	args['content'] = content
	args['site'] = site
	mongoDB = mongoConnection.mongoConnection(db='video',collection='spider')
	time_ = time.strftime( '%Y-%m-%d %X', time.localtime())
	infomation_id = mongoDB.collection.update({
		'site':site,'content':content},{'$set':{'inactive':1,'last_time':time_}})
	url_spider(args,socketio=socketio)

def auto_run():
	mongo = mongoConnection.mongoConnection(db='video',collection='spider')
	tasks = list(mongo.collection.find({},{'content':1,'site':1,'_id':0}))
	tasks = [(x['content'],x['site']) for x in tasks]
	for x in tasks:
		click(*x)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-t','--type',dest='type')
	parser.add_argument('-c','--content',dest='content')
	parser.add_argument('-s','--site',dest='site')
	args = parser.parse_args()
	content = args.content
	site = args.site
	if(args.type=='click'):
		click(content,site)
	elif args.type=='auto':
		auto_run()





if __name__ == '__main__':
	# content = '美国'
	# site = 'sina'
	# click(content,site)
	print('hhhh')
	logger.info('hhh')
	# main()