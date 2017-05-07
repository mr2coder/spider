# -*- coding: utf-8 -*-
from you_get.common import *
from you_get.extractors import sina,qq,iqiyi,acfun,cntv,ifeng,bilibili,youku,tudou,sohu
import pymongo
import time,random


#add sys.path
import logging.config
path = os.path.abspath(__file__).replace('\\','/').split('/')
logfile = os.path.join( '/'.join(path[:-2]),"logger.conf")
logging.config.fileConfig(logfile)
logger = logging.getLogger("video")


#db setting
MONGODB_SERVER = '127.0.0.1'
MONGODB_PORT = 27017
DB = 'video'
COLLECTION = 'urlinfo'

#view model path
print (os.path.dirname(sina.__file__))


def main():
	"""
	download video and video information from sina.com 
	"""
	connection = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
	db = connection[DB]
	collection = db[COLLECTION]
	#query url set where status!=0
	urls = collection.find({'status':{'$ne':0}},{'url':1,'site':1})
	#set output path 
	output_dir = "../web/static/video"
	func_dict = {'sina':sina,'qq':qq,'iqiyi':iqiyi,'acfun':acfun,'cntv':cntv,'ifeng':ifeng,'bilibili':bilibili,'youku':youku,'tudou':tudou,'sohu':sohu}
	for url in urls:
		print(url)
		try:
			func = func_dict[url['site']]
			if func==sina:
				info, size = sina.download(url['url'], output_dir)
				collection.update({"url":url['url']},{"$set":{'tag':info[0],'introduction':info[1],'from':info[2],'channel':info[3],'size':size,'status':0}})
			else:
				func.download(url['url'], output_dir)
				collection.update({"url":url['url']},{"$set":{'status':0}})
			logger.info("success {url}".format(url=url['url']))
			time.sleep(random.random())
		except Exception as e:
			logger.debug(e)
			continue
		#add or change collection's field
		
	

if __name__ == '__main__':
	main()
	