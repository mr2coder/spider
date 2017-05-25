import requests
from lxml import html
import re,datetime
from multiprocessing.dummy import Pool as ThreadPool	
import argparse
import random
import json
import os
import time as realtime
import fetch_free_proxyes as fproxy
import clean
import logging.config
path = os.path.abspath(__file__).replace('\\','/').split('/')

logfile = os.path.join( '/'.join(path[:-4]),"logger.conf")
logging.config.fileConfig(logfile)
logger = logging.getLogger("paper")

#add sys.path
import sys
sys.path.append('/'.join(path[:-3]))
from mongo import mongoConnection


TIMEOUT = 4
FNAME = 'DM.txt'
PAGEINDEX = 'index.txt' #存放下一次应该访问的页码
def str2Num(string=""):
	#把字符串转化为数字，'34534j34'=>3453434
	sum_ = 0
	for x in string:
		if (x<='9')and(x>='0'):
			sum_ = sum_*10+int(x)
	return sum_

def fwrite(f_name,data):
	#讲记录写入文件
	if data==None:return -1
	with open(f_name, 'a+') as fl:
		fl.write(json.dumps(data,ensure_ascii=False))
		fl.write('\n')
	return 0

def page_index(f_name,model,index=1):
	if model=='r':
		if os.path.exists(f_name):
			with open(f_name, 'r') as fl:
				line = fl.readline()
			return int(line.strip())
		else:
			page_index(f_name,'w',index=1)
			return 1
	elif model=='w':
		with open(f_name, 'w') as fl:
			line = fl.write(str(index))

def get_url(url, proxie, time=TIMEOUT,**kwarg):
	'''
	Description:get paper's url and quote
	Paramaters:
	'''
	item = {}
	try:
		if proxie is None:response = requests.get(url, timeout=time)
		else:response = requests.get(url, proxies=proxie, timeout=time)
		# response = requests.get(url)
		#if reaponse's statuts_code !=200,means that access failed
		if response.status_code!=200:
			logger.debug('页面信息访问失败！！')
			return None

		#transform to 'lxml' format
		doc = html.fromstring(response.text)
		paper_urls = doc.xpath("//div[@class='record-item-list']//a[@class='title']/@href")
		quotes = doc.xpath("//span[@class='cited']")

		item['paper_urls'] = paper_urls
		item['quotes'] = [str2Num("".join(x.xpath("text()"))) for x in quotes]
		return item
	except Exception as e:
		logger.debug("页面信息解析失败")
		logger.debug(e)
		return None

def get_page_nums(url):
	try:
		response = requests.get(url)
		doc = html.fromstring(response.text)
		total_num = doc.xpath("//div[@class='total-records']/span/text()")[0]
		total_num = str2Num(total_num)
		return total_num
	except Exception as e:
		logger.debug("Error:total page number get failed")
		
def get_paper(url,quote,proxie,time=TIMEOUT, **kwarg):
	'''
	Description:get paper's detail informations
	Paramaters:

	'''
	item = {}
	#random choice proxies
	try:
		if proxie is None:response = requests.get(url, timeout=time)
		else:response = requests.get(url, proxies=proxie, timeout=time)
		#if reaponse's statuts_code !=200,means that access failed
		if response.status_code!=200:
			logger.debug("论文访问失败！！")
			return None
		#transform to 'lxml' format
		doc = html.fromstring(response.text)
		#get item info
		title =  doc.xpath("//div[@class='section-baseinfo']/h1/text()")[0].strip()
		link = url
		abstract = doc.xpath("//div[@class='baseinfo-feild abstract']//div[@class='text']/text()")
		if len(abstract)>0:
			abstract = abstract[0].strip()
		keywords = doc.xpath("//div[@class='row row-keyword'][1]//a/text()")
		authors =  doc.xpath("//div[@class='row row-author']//a/text()")
		index = doc.xpath("//div[@class='row row-author'][1]//sup/text()")
		institutions = doc.xpath("//div[@class='row row-author']/following-sibling::div[@class='row']/span[@class='text']/span/text()")
		if len(institutions)==0:
			institutions = doc.xpath("//div[@class='row row-author']/following-sibling::div[@class='row']/span[@class='text']/text()")
		date = doc.xpath("//div[@class='row row-magazineName']/following-sibling::div[@class='row']/span/a/text()")
		if len(date)>0:
			date = date[0]
		journal = doc.xpath("//div[@class='row row-magazineName']//a/text()")
		if len(journal)>0:
			journal = journal[0].strip()
		include = doc.xpath("//span[@class='core-box']/span/text()")
		#set the same index with author
		if len(index)!=0:
			institutions = ';'.join(";".join(institutions).split(u"；")).split(";")
			institutions =[institutions[int(x[1])-1] for x in index]
		else:
			institutions = institutions[0].strip()
		item["title"] = title
		item["link"] = link
		item["abstract"] = abstract
		item["keywords"] = keywords
		item["authors"] = authors
		item["institutions"] = institutions
		item["date"] = date
		item["journal"] = journal
		item["include"] = include
		item["quote"] = quote
		item["spidertime"] = realtime.strftime( '%Y-%m-%d %X', realtime.localtime())
		return item
	except Exception as e:
		logger.debug('论文解析失败..')
		logger.debug (e)
		return None	

def click(url,socketio=None,proxy=False):
	logger.info('免费代理获取中  \n这可能花费几分钟，请稍后...')
	if socketio:
		socketio.emit('my_response',
			{'data': '免费代理获取中  \n这可能花费几分钟，请稍后...'},
			namespace='/paper')
		socketio.sleep(1)

	proxies = [None]
	if proxy:
		proxies = fproxy.fetch_all()
		proxies = [{'http':'http://'+x} for x in proxies]
	logger.info('免费代理获取完毕，总共%d条。'%len(proxies))
	if socketio:
		socketio.sleep(1)
		socketio.emit('my_response',
			{'data': '免费代理获取完毕，总共%d条。'%len(proxies)},
			namespace='/paper')
	num = get_page_nums(url)
	logger.info(num)
	mongo = mongoConnection.mongoConnection(db='wanFang',collection='paperinfo')
	# proxies = [None]
	# i = page_index(PAGEINDEX,'r')
	i = 0
	while i<= (num+9)//10:
		failed_tag = 0
		new_url = url+'&p='+str(i)
		# print(new_url)
		proxie = random.choice(proxies)
		item = get_url(new_url,proxie)
		# print('item',item)
		if item is not None and item['paper_urls'] !=[]:
			for paper_url,quote in zip(item['paper_urls'],item['quotes']):
				attempt = 0
				papers = get_paper(paper_url,quote,proxie)
				while papers is None:
					# print ('失败次数为：',attempt+1,failed_tag)
					failed_tag +=1
					attempt += 1
					if attempt%3==0:
						attempt = 0
						break
					if failed_tag%10==0:
						logger.info("抓取新代理，请稍等")
						proxies = fproxy.fetch_all()
						proxies = [{'http':'http://'+x} for x in proxies]
					proxie = random.choice(proxies)
					# print('新换ip代理为：',proxie)
					papers = get_paper(paper_url,quote,proxie)
				
				if papers is not None and papers != -1:
					failed_tag = 0
					logger.info('papers:'+papers['title'])
					if socketio:
						socketio.emit('my_response',
							{'data': 'papers:'+papers['title']},
							namespace='/paper')
						socketio.sleep(1)
					try:
						papers['url'] = url
						papers = clean.clean(papers) #按照规定格式格式化
						mongo.collection.insert(papers)
					except Exception as e:
						logger.debug(e)
						logger.debug(papers)
						logger.debug('插入数据库失败...')
					# fwrite(FNAME, papers)

			i += 1 #此页数据访问成功，开始访问下一页，否则重新选择代理访问
			page_index(PAGEINDEX,'w',str(i+1))
		else:
			failed_tag += 1
			if failed_tag%3==0:
				proxies = fproxy.fetch_all()
				proxies = [{'http':'http://'+x} for x in proxies]


def auto_run(proccess_num=10):
	mongo = mongoConnection.mongoConnection(db='wanFang',collection='spider')
	tasks = list(mongo.collection.find({},{'url':1,'_id':0}))
	tasks = [x['url'] for x in tasks]
	pool = ThreadPool(proccess_num)
	results = pool.map(click, tasks)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-t','--type',dest='type')
	parser.add_argument('-c','--content',dest='content')
	args = parser.parse_args()
	url = args.content
	# url = 'http://s.wanfangdata.com.cn/Paper.aspx?q= 题名:雷达'
	if(args.type=='click'):
		click(url)
	elif args.type=='auto':
		auto_run()
	logger.info('Success: Task update finshed..')


def test_get_paper():
	url = 'http://d.wanfangdata.com.cn/Periodical/xtgcydzjs201610009'
	get_paper(url,proxies=[None])

if __name__ == '__main__':
	# print(type(realtime.strftime( '%Y-%m-%d %X', realtime.localtime())))
	main()
	# a = []
	# print(a==[])
