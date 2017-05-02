import requests
from lxml import html
import json
import random
import sys
import logging
reload(sys)
sys.setdefaultencoding('utf-8')

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

def ():
	pass
	
