import requests
from lxml import html
import re,time,datetime
import argparse
import fetch_free_proxyes as fproxy
import random,os
from bson.objectid import ObjectId

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

patt = 'http://so.iqiyi.com/so/q_{content}_ctg__t_{length}_page_{pagenum}_p_1_qc_0_rd_{time_limt}_site_{site}_m_1_bitrate_?af=true'
def build_url(content,site,time_limt='level0',length='level1',pagenum=1):
	arr_len = {'level0':'0','level1':'2','level2':'3','level3':'4','level4':'5'}
	arr_time = {'level0':'','level1':'1','level2':'2','level3':'3'}
	url = patt.format(content=content,pagenum=str(pagenum),
		time_limt=arr_time[time_limt],
		length=arr_len[length],site=site)
	return url

#获取页面数目
def get_page_nums(content,site,time_limt='level0',length='level1',pagenum=1):
	url = build_url(content,site,time_limt,length,pagenum)
	response = requests.get(url=url)
	doc = html.fromstring(response.text)
	temp = doc.xpath("//div[@class='search_result_tip']//em[@class='keyword']/text()")[-1]
	temp = temp.split('万')
	total_items = float(temp[0])
	if len(temp)==2:
		total_items = float(temp[0])*10000
	return int(total_items)

#获取页面文本信息
def get_page_info(content,site,time_limt='level0',length='level1',pagenum=1):
	url = build_url(content,site,time_limt,length,pagenum)
	response = requests.get(url=url)
	doc = html.fromstring(response.text)
	lens = doc.xpath("//span[@class='icon-vInfo']/text()")
	titles = doc.xpath("//h3[@class='result_title']/a/@title")
	links = doc.xpath("//h3[@class='result_title']/a/@href")
	p_times = doc.xpath("//em[@class='result_info_desc']/text()")[::2]
	infos = doc.xpath("//div[@class='result_info_cont result_info_cont-row1']")
	infos = [x.xpath("./span/text()") for x in infos]
	for x in range(len(infos)):
		if len(infos[x])==0:
			infos[x] = ''
		else:
			infos[x] = infos[x][0].strip()
	result = [{"videoname":x[0].strip(),
				"url":x[1],
				"showtime":x[2],
				"videoinfo":x[3],
				"playtimes":'',
				"spidertime":time.strftime( '%Y-%m-%d %X', time.localtime()),
				"site":site,
				"content":content,
				"status":1,
				} for x in zip(titles, links, p_times, infos)]
	return result

#爬虫路口
def iqiyi_url_spider(content,site='iqiyi',socketio=None):
	mongoDB = mongoConnection.mongoConnection(db='video',collection='spider')
	data = list(mongoDB.collection.find({'content':content,'site':site},{'time_limit':1,'_id':0,'length':1}))[0]
	print(data)
	page_num = get_page_nums(content,site,time_limt=data['time_limit'],length=data['length'])
	if socketio:socketio.emit('my_response', {'data': '总数为:'+str(page_num)},namespace='/video')
	page_num = min((page_num+19)//20,20)
	mongoDB = mongoConnection.mongoConnection(db='video',collection='urlinfo')
	for index in range(1,page_num+1):
		result = get_page_info(content,site,time_limt=data['time_limit'],length=data['length'],pagenum=index)
		if socketio:
			for line in result:
				socketio.emit('my_response',  
					{'data': 'Currently crawling title is: '+line['videoname']},
					namespace='/video')
				socketio.sleep(1)
				try:
					print(line)
					infomation_id = mongoDB.collection.insert(line)
					mongoDB.db['spider'].update({'site':site,'content':content},{'$set':{'inactive':0}})
				except Exception as e:
					logger.debug(e)
			socketio.emit('my_response', {'data': '已完成'},namespace='/video')
			socketio.emit('disconnect', {'data': 'disconnect'},namespace='/video')





if __name__ == '__main__':
	result = get_page_info('时间规划局','cntv')
	print(len(result))
	iqiyi_url_spider('时间规划局','cntv')
	# print(result)


