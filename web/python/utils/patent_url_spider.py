import requests
from lxml import html
import re,time,datetime
from multiprocessing.dummy import Pool as ThreadPool	
import argparse
import fetch_free_proxyes as fproxy
import random,os
from patentSpider import FormData
from bson.objectid import ObjectId
URL = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/showSearchResult-startWa.shtml'
#add sys.path
import logging.config
path = os.path.abspath(__file__).replace('\\','/').split('/')
logfile = os.path.join( '/'.join(path[:-4]),"logger.conf")
logging.config.fileConfig(logfile)
logger = logging.getLogger("patent")

#add sys.path
import sys
sys.path.append('/'.join(path[:-3]))
from mongo import mongoConnection
TIMEOUT = 10
def str2Num(string=""):
	#把字符串转化为数字，'34534j34'=>3453434
	sum_ = 0
	for x in string:
		if (x<='9')and(x>='0'):
			sum_ = sum_*10+int(x)
	return sum_


def get_page_nums(url,form):
	try:
		response = requests.post(url, data=form)
		doc = html.fromstring(response.text)
		total_num = doc.xpath('//input[@id="result_totalCount"]/@value')[0]
		total_num = str2Num(total_num)
		return total_num
	except Exception as e:
		logger.debug("Error:total page number get failed")
		
def get_patent(url,form,proxie,time=TIMEOUT, **kwarg):
	'''
	Description:get patent's detail informations
	Paramaters:

	'''
	item = {}
	#random choice proxies
	try:
		if proxie is None:response = requests.post(url, data=form, timeout=time)
		else:response = requests.post(url, data=form, proxies=proxie, timeout=time)
		#if reaponse's statuts_code !=200,means that access failed
		if response.status_code!=200:
			logger.debug("论文访问失败！！")
			return None
		#transform to 'lxml' format
		doc = html.fromstring(response.text)
		re_html = re.compile('<.*?>')
		titles = doc.xpath('//div[@class="item-header clear"]/h1/div[2]/a/@title')
		titles = [re_html.sub('',x) for x in titles]
		
		t_ids = doc.xpath('//div[@class="item-content-body left"]/p[1]/text()')
		r_dates = doc.xpath('//div[@class="item-content-body left"]/p[2]/a/text()')
		o_ids = doc.xpath('//div[@class="item-content-body left"]/p[3]/text()')
		o_dates = doc.xpath('//div[@class="item-content-body left"]/p[4]/a/text()')
		icp_ids = doc.xpath('//div[@class="item-content-body left"]/p[5]')
		icp_ids = [";".join(x.xpath('.//span/a/@_name')) for x in icp_ids]
		insititutions = doc.xpath('//div[@class="item-content-body left"]/p[6]')
		insititutions = [[re_html.sub('',i) for i in x.xpath('.//span/a/@_name')] for x in insititutions]
		authors = doc.xpath('//div[@class="item-content-body left"]/p[7]')
		authors = [[i.strip() for i in x.xpath('.//span/a/text()')] for x in authors]
		proxies = doc.xpath('//div[@class="item-content-body left"]/p[8]/text()')
		proxy_insititutions = doc.xpath('//div[@class="item-content-body left"]/p[9]/text()')

		del_index = [] #用来保存将要删除数据的位置,当一条数据的机构与作者个数不能对应时,就丢掉这条数据
		for i in range(len(insititutions)):
			if len(insititutions[i])==0 or (len(insititutions[i])!=1 and len(insititutions[i])!=len(authors[i])):
				del_index.append(i)
			if len(insititutions[i])!=len(authors[i]) and len(insititutions[i])==1:
				insititutions[i] *= len(authors[i])
		
		item["titles"] = [value for index,value in enumerate(titles) if index not in del_index]
		item["t_ids"] = [value for index,value in enumerate(t_ids) if index not in del_index]
		item["o_ids"] = [value for index,value in enumerate(o_ids) if index not in del_index]
		item["o_dates"] = [value for index,value in enumerate(o_dates) if index not in del_index]
		item["authors"] = [value for index,value in enumerate(authors) if index not in del_index]
		item["institutions"] = [value for index,value in enumerate(insititutions) if index not in del_index]
		item["proxies"] = [value for index,value in enumerate(proxies) if index not in del_index]
		item["proxy_insititutions"] = [value for index,value in enumerate(proxy_insititutions) if index not in del_index]
		item["icp_ids"] = [value for index,value in enumerate(icp_ids) if index not in del_index]
		item["r_dates"] = [value for index,value in enumerate(r_dates) if index not in del_index]
		return item
	except Exception as e:
		logger.debug('页面解析失败')
		logger.debug(e)
		return -1

def form_produce(content,page = None):
	#构造查询条件式
	format_str = []
	if content.get('begin'):
		format_str.append('申请日>'+content.get('begin'))
	if content.get('end'):
		format_str.append('申请日<'+content.get('end'))
	if content.get('title'):
		format_str.append('发明名称=('+content.get('title')+')')
	if content.get('qwords'):
		format_str.append('摘要=('+content.get('qwords')+')')
	if content.get('author'):
		format_str.append('发明人=('+content.get('author')+')')
	if content.get('insititution'):
		format_str.append('申请（专利权）人=('+content.get('insititution')+')')
	format_str = " AND ".join(format_str)
	form = FormData(format_str)
	if page:
		form.resultPagination_start = page
	return form.get_form()

def click(url,content,socketio=None,proxy=False):
	proxies = [None]
	if proxy:
		if socketio:
			socketio.sleep(1)
			socketio.emit('my_response',
				{'data': '免费代理获取中  \n这可能花费几分钟，请稍后...'},
				namespace='/patent')
		proxies = fproxy.fetch_all()
		proxies = [{'http':'http://'+x} for x in proxies]
		if socketio:
			socketio.sleep(1)
			socketio.emit('my_response',
				{'data': '免费代理获取中  \n这可能花费几分钟，请稍后...'},
				namespace='/patent')
	form = form_produce(content)
	num = get_page_nums(url,form)
	logger.info(num)
	mongo = mongoConnection.mongoConnection(db='patent',collection='patentinfo')
	i = 1
	if not num and socketio:
		socketio.emit('my_response', {'data': '目标网站连接失败,请稍后重试!'},namespace='/patent')
		socketio.emit('disconnect', {'data': 'disconnect'},namespace='/patent')
		return
	while i<= num:
		failed_tag = 0
		attempt = 0
		form = form_produce(content,i)
		proxie = random.choice(proxies)
		patents = get_patent(url,form,proxie)
		while patents is None:
			logger.debug('失败次数为：'+str(attempt+1)+str(failed_tag))
			failed_tag +=1
			attempt += 1
			if attempt%3==0:
				attempt = 0
				break
			if failed_tag%10==0:
				logger.info("抓取新代理，请稍等")
				if socketio:
					socketio.sleep(1)
					socketio.emit('my_response',
						{'data': '抓取新代理，请稍等'},
						namespace='/patent')
				proxies = fproxy.fetch_all()
				proxies = [{'http':'http://'+x} for x in proxies]
			proxie = random.choice(proxies)
			# print('新换ip代理为：',proxie)
			patents = get_patent(url,form,proxie)
		
		failed_tag = 0
		if patents!= -1:
			try:
				for x in patents['titles']:
					logger.info('title:'+x)
					if socketio:
						socketio.sleep(1)
						socketio.emit('my_response',
							{'data': 'title:'+x},
							namespace='/patent')
				store(patents,str(content['_id']))
			except Exception as e:
				logger.debug(e)
				logger.debug('插入数据库失败...')
		i += 50

def store(patents,spider_id):
	#将得到的patents存入mongdb
	result = [{"title":x[0].strip(),
				"t_id":x[1],
				"o_id":x[2],
				"o_date":x[3].strip(),
				"author":x[4],
				"spidertime":time.strftime( '%Y-%m-%d %X', time.localtime()),
				"institution":x[5],
				"proxie":x[6],
				"proxy_insititution":x[7],
				"icp_id":x[8],
				"spider_id":spider_id,
				"r_date":x[9]} for x in zip(
					patents["titles"],
					patents["t_ids"],
					patents["o_ids"],
					patents["o_dates"],
					patents["authors"],
					patents["institutions"],
					patents["proxies"],
					patents["proxy_insititutions"],
					patents["icp_ids"],
					patents["r_dates"])]
	mongoDB = mongoConnection.mongoConnection(db='patent',collection='patentinfo')
	infomation_id = mongoDB.collection.insert_many(result, ordered=False)
	return infomation_id


def auto_run(proccess_num=10):
	mongo = mongoConnection.mongoConnection(db='patent',collection='spider')
	tasks = list(mongo.collection.find({}))
	pool = ThreadPool(proccess_num)
	results = pool.map(click, zip(repeat(URL), tasks))

def auto_click(id,socketio=None,proxy=False):
	mongo = mongoConnection.mongoConnection(db='patent',collection='spider')
	content = list(mongo.collection.find({'_id':ObjectId(id)}))
	content = content[0]
	url = URL
	socketio.emit('my_response',
			{'data': URL},
			namespace='/patent')
	socketio.sleep(1)
	click(url,content,socketio=socketio,proxy=proxy)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-t','--type',dest='type')
	parser.add_argument('-c','--content',dest='content')
	args = parser.parse_args()
	spider_id = args.content
	#数据库链接
	mongo = mongoConnection.mongoConnection(db='patent',collection='spider')
	content = list(mongo.collection.find({'_id':ObjectId(spider_id)}))
	content = content[0]
	url = URL
	if(args.type=='click'):
		click(url,content)
	elif args.type=='auto':
		auto_run()
	logger.info('Success: Task update finshed..')


def test_get_patent():
	url = 'http://d.wanfangdata.com.cn/Periodical/xtgcydzjs201610009'
	get_patent(url,proxies=[None])
	while True:
		print("*****")

if __name__ == '__main__':
	test_get_patent()
	main()
	# a = []
	# print(a==[])
