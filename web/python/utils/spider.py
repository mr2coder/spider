# -*- coding:utf8 -*-
import requests
from lxml import html
import json
import random
import sys,os
import logging


class urlSpider(object):
	"""base class"""
	def __init__(self, patt, patt_para, thread_num=5, **kwargs):
		super(urlSpider, self).__init__()
		self.__patt = patt
		self.__thread_num = thread_num
		self.__patt_para = patt_para
		self.__start_url = patt.format(**self.__patt_para)
		self.__session = requests.session()
		self.__proxies = None
		if kwargs.get('proxies')!=None:
			self.__proxies = kwargs.get('proxies')

	def get_page_num(self, get_pagenums):
		try:
			if self.__proxies!=None:
				response = self.__session.get(self.__start_url, proxies=self.__proxies)
			else:
				response = self.__session.get(self.__start_url)
			assert response.status_code==200
			self.__pagenums = get_pagenums(response)
			return True
		except Exception as e:
			print (e)
			return False

	def url_info_spider(self, get_urls):
		"""
		use the 'get_urls' function that define by your self to sipder video base information, 
		"""
		urls = [lambda patt_para=copy.deepcopy(self.__patt_para): 
						self.__patt.format(**patt_para) for x in range(self.__pagenums) 
							if not self.__patt_para.update({"page":x+1})]
		urls = [x() for x in urls]
		print (urls)
		pool = ThreadPool(self.__thread_num)
		results = pool.map(get_urls, zip(urls, repeat(self.__patt_para['content'])))

def click(url,content,form,db,collection,proxies=False):
	if proxies:
		print('免费代理获取中  \n这可能花费几分钟，请稍后...')
		proxies = fproxy.fetch_all()
		proxies = [{'http':'http://'+x} for x in proxies]
		print('免费代理获取完毕，总共%d条。'%len(proxies))
	else:
		proxies = [None]
	mongo = mongoConnection.mongoConnection(db=db,collection=collection)
	i = 1
	while i<= num:
		failed_tag = 0
		attempt = 0
		form = form_produce(content,i)
		proxie = random.choice(proxies)
		patents = get_patent(url,form,proxie)
		while patents is None:
			logging.debug('失败次数为：',attempt+1,failed_tag)
			failed_tag +=1
			attempt += 1
			if attempt%3==0:
				attempt = 0
				break
			if failed_tag%10==0:
				logging.info("抓取新代理，请稍等")
				proxies = fproxy.fetch_all()
				proxies = [{'http':'http://'+x} for x in proxies]
			proxie = random.choice(proxies)
			# print('新换ip代理为：',proxie)
			patents = get_patent(url,form,proxie)
		
		failed_tag = 0
		if patents!= -1:
			try:
				for x in patents['titles']:
					logging.info('title:',x)
				store(patents,str(content['_id']))
			except Exception as e:
				logging.debug(e)
				logging.debug('插入数据库失败...')
		i += 50

def get_paper(url, proxie, **kwarg):
	'''
	Description:get paper's detail informations
	Paramaters:

	'''
	item = {}
	#random choice proxies
	proxie = random.choice(proxies)
	response = requests.get(url, proxies=proxie)
	#if reaponse's statuts_code !=200,means that access failed
	if response.status_code!=200:
		return None

	try:
		#transform to 'lxml' format
		doc = html.fromstring(response.text)
		#get item info
		title =  doc.xpath("//div[@class='section-baseinfo']/h1/text()").extract()[0].strip()
		link = url
		abstract = doc.xpath("//div[@class='baseinfo-feild abstract']//div[@class='text']/text()").extract()
		keywords = doc.xpath("//div[@class='row row-keyword']//a/text()").extract()
		authors =  doc.xpath("//div[@class='row row-author']//a/text()").extract()
		index = doc.xpath("//div[@class='row row-author'][1]//sup/text()").extract()
		institutions = doc.xpath("//div[@class='row row-author']/following-sibling::div[@class='row']/span[@class='text']/span/text()").extract()
		if len(institutions)==0:
			institutions = doc.xpath("//div[@class='row row-author']/following-sibling::div[@class='row']/span[@class='text']/text()").extract()[0].strip()
		date = doc.xpath("//div[@class='row row-magazineName']/following-sibling::div[@class='row']/span/a/text()").extract()
		journal = doc.xpath("//div[@class='row row-magazineName']//a/text()").extract()
		include = doc.xpath("//span[@class='core-box']/span/text()").extract()

		#set the same index with author
		if len(index)!=0:
			institutions = ";".join(institutions)
			institutions = institutions.split(";").split(u"；")
			institutions =[institutions[int(x[1])-1] for x in index]

		item["title"] = title
		item["link"] = link
		item["abstract"] = abstract
		item["keywords"] = keywords
		item["authors"] = authors
		item["institutions"] = institutions
		item["date"] = date
		item["journal"] = journal
		item["include"] = include
		return item
	except Exception as e:
		raise e
		return None


def get_url(url, proxie, **kwarg):
	'''
	Description:get paper's url and quote
	Paramaters:
	'''
	item = {}
	response = requests.get(url, proxies=proxie)
	#if reaponse's statuts_code !=200,means that access failed
	if response.status_code!=200:
		return None

	try:
		#transform to 'lxml' format
		doc = html.fromstring(response.text)
		paper_urls = doc.xpath("//div[@class='record-item-list']//a[@class='title']/@href").extract()
		quotes = doc.xpath("//span[@class='cited']")

		item['paper_urls'] = paper_urls
		item['quotes'] = quotes

		return item
	except Exception as e:
		raise e
		return None


def structure_url(name, sytle, **kwarg):
	pass

def hh():
	pass
	
