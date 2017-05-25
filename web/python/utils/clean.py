# -*- coding: utf-8 -*-
from functions import *
import json
import time as realtime
from datetime import datetime
import logging.config
import os
path = os.path.abspath(__file__).replace('\\','/').split('/')

logfile = os.path.join( '/'.join(path[:-4]),"logger.conf")
logging.config.fileConfig(logfile)
logger = logging.getLogger("paper")
def __key_clean__(key,**kwargs):
	pass

def __institution_clean__(institution,**kwargs):
	'''
	Disambiguation
	Get uniqe institution name
	'''
	#If several institutions name in the same row,separator by ';' ,get the first one.(it was not supposed to appear,stupid wanFang...)
	institution = institution.decode('utf-8').split(';')[0]
	# print institution
	new_name = ''
	if_no_title_name = ''
	flag = False
	flag2 = False
	index = 0
	temp = ''
	no_title_name_flag = False
	#set separator
	separator = kwargs.get('separator')
	if separator==None:
		separator = '所'
	
	if separator in institution:
		'''
		e.x.
		input:中国电子科技集团,第十四研究所,江苏,南京,210013
		output:电子科技集团14所
		'''
		institution = institution.strip().split(separator)[0].replace(',','').replace('，','').replace(' ','').split(';')[0]
		no_title_name_flag = True
	else:
		'''
		e.x.
		input:中国电子科技集团第十四研究
		output:电子科技集团14所
		'''
		institution = institution.strip().split(" ")[0].split(",")[0].split('，')[0]
	# print institution
	n = {u'一':'1',u'二':'2',u'三':'3',u'四':'4',u'五':'5',u'六':'6',u'七':'7',u'八':'8',u'九':'9',u'十':' '}
	#If has standard name format, e.x. :'中国电子科技集团公司'，'中国电子科技集团'，'电子科技集团公司' same as '电子科技集团'
	if kwargs.get('standard_names'):
		for title in kwargs['standard_names']:
			if title in institution:
				new_name += title
				flag = True
				break

	if flag or no_title_name_flag:
		institution = institution+separator
	try:
		for c in institution.decode(chardet.detect(institution)['encoding']):
			if n.get(c):
				temp += str(n[c])
				index += 1
				flag2 = True

			else:
				# 十四 => 14, 十 => 10, 二十 => 20
				if index != 0:
					if temp[0]==' ':
						temp = '1'+temp
					if temp[-1]==' ':
						temp = temp+'0'
					temp = temp.replace(' ','')
					new_name += temp
					if_no_title_name += temp
					#reset value
					index = 0
					temp = ''
				if_no_title_name += c
			if c <= '9' and c >= '0':
				new_name += str(c)
				flag2 = True


		if flag and flag2:
			return new_name+separator
		return if_no_title_name
	except Exception as e:
		return institution

def __date_clean__(date,**kwargs):
	if len(date)==0:
		return None
	year = date.split(',')[0]
	period = date.split('(')[1].split(')')[0]
	return {'year':year, 'period':period}


def __location_clean__(institution,**kwargs):
	city_list = read_city()
	institution = institution.decode('utf-8')
	institution = institution.split(';')[0]
	city = [x for x in city_list if x in institution]
	if len(city)==0:return None
	#'北京大学.深圳研究生院' => return '深圳' not '北京'
	return city[-1]


def read_city(fname='city.txt'):
	fname = os.path.join( '/'.join(path[:-1]),fname)
	#Return all city's name in China
	file = open(fname,"r")
	name_list = file.readlines()
	file.close()
	names = set()
	for line in name_list:
		line = line.strip("\r\n").strip().split(' ')[1]
		line = line.split('省')
		# print(line)
		if len(line)==1:
			line = line[0].split('区')
		line = line[-1].split('市')[0]
		names.add(line)
	return names

def clean(line):
	standard_names = ['中航工业','电子科技集团']
	try:
		temp = {}
		temp['authors'] = {}
		temp['abstract'] = {}
		temp['institutions']={}
		temp['title'] = line['title']
		temp['link'] = line['link']
		temp['keywords'] = line['keywords']
		temp['quote'] = line['quote']
		temp['spidertime'] = line['spidertime']
		temp['url'] = line['url']
		#set include
		if len(line['include'])==0:
			temp['include'] = None
		else:
			temp['include'] = line['include']
		#set journal
		temp['journal'] = line['journal']
		temp['date'] = __date_clean__(line['date'])
		temp['abstract']['Chinese'] = line['abstract']

		#Because of my stupid when crawl data,so have to do like this...
		#   not notice that if there just have one institution record,spider return a str type,not a list..
		if isinstance(line['institutions'],list):
			for x in range(min(len(line['institutions']),len(line['authors']))):
				institution = __institution_clean__(line['institutions'][x].encode("utf-8"), standard_names=standard_names)
				locate = __location_clean__(line['institutions'][x].encode("utf-8"))
				temp['authors'][line['authors'][x]] = {}
				temp['authors'][line['authors'][x]]['institution'] = institution
				temp['authors'][line['authors'][x]]['location'] = locate
				temp['institutions'][institution] = locate
		else:
			temp['authors'][line['authors'][0]] = {}
			institution =  __institution_clean__(line['institutions'].encode("utf-8"), standard_names=standard_names)
			locate = __location_clean__(line['institutions'].encode("utf-8"))

			for x in line['authors']:
				temp['authors'][x] = {}
				temp['authors'][x]['institution'] = institution
				temp['authors'][x]['location'] = locate
			temp['institutions'][institution] = locate
		# temp['institutions'] = line['institutions']
		return temp
	except Exception as e:
		logger.debug('clean fail')
		logger.debug(temp)
		logger.debug(line)

def main():
	key = 'institution'
	db_conection = mongoConnection.mongoConnection()
	# db_conection.collection = db_conection.db['paper_new']
	result = db_conection.collection.find()
	entrance = db_conection.db['paperinfo']
	#set index
	entrance.ensure_index('link', unique=True)
	# entrance = db_conection.collection
	with open('AI.txt','r') as f:
		result = f.readlines()
	#write file name 
	for line in result:
		try:
			line = json.loads(line)
			line['url'] = 'http://s.wanfangdata.com.cn/Paper.aspx?q= 题名:人工智能'
			time = str(datetime.today())
			time = time.split('.')[0]
			line['spidertime'] = time
			temp = clean(line)
			entrance.insert(temp)
		except Exception as e:
			print(e)
		

		
		


if __name__ == '__main__':
	# institution = '中国航工业集团北京,第十四研究所,江苏,南京,210013'
	# separator = '所'
	# standard_names = ['中航工业','电子科技集团']
	# st = """
	# {"url":"dhfkjhs","spidertime":"2017-04-29","link": "http://d.wanfangdata.com.cn/Periodical/jsjyjyfz201309002", "quote": 164, "journal": "计算机研究与发展", "authors": ["余凯", "贾磊", "陈雨强", "徐伟"], "institutions": "百度 北京100085", "date": ["2013, 50(9)"], "title": "深度学习的昨天、今天和明天", "abstract": "机器学习是人工智能领域的一个重要学科.自从20世纪80年代以来,机器学习在算法、理论和应用等方面都获得巨大成功.2006年以来,机器学习领域中一个叫“深度学习”的课题开始受到学术界广泛关注,到今天已经成为互联网大数据和人工智能的一个热潮.深度学习通过建立类似于人脑的分层模型结构,对输入数据逐级提取从底层到高层的特征,从而能很好地建立从底层信号到高层语义的映射关系.近年来,谷歌、微软、IBM、百度等拥有大数据的高科技公司相继投入大量资源进行深度学习技术研发,在语音、图像、自然语言、在线广告等领域取得显著进展.从对实际应用的贡献来说,深度学习可能是机器学习领域最近这十年来最成功的研究方向.将对深度学习发展的过去和现在做一个全景式的介绍,并讨论深度学习所面临的挑战,以及将来的可能方向.", "keywords": ["机器学习", "深度学习", "语音识别", "图像识别", "自然语言处理", "在线广告"], "include": ["ISTIC", "EI", "PKU"]}
	# """
	# st = json.loads(st)
	# # print(st)
	# temp = clean(st)

	# print __institution_clean__(institution, separator=separator, standard_names=standard_names)

	# print __location_clean__(institution)
	# print __date_clean__(['2008, 34(10)'])
	read_city()
	# db_conection = mongoConnection()
	# # db_conection.collection = db_conection.db['paper_new']
	# result = db_conection.collection.find({},{'link':1})
	# for x in result:
	# 	print x['link']



