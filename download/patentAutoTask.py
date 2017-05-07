import sys,os
import pymongo
import time,datetime
path = os.path.abspath(__file__).replace('\\','/').split('/')
sys.path.append('/'.join(path[:-2])+'/web/python/utils')
import patent_url_spider as spider

#add sys.path
import logging.config
path = os.path.abspath(__file__).replace('\\','/').split('/')
logfile = os.path.join( '/'.join(path[:-2]),"logger.conf")
logging.config.fileConfig(logfile)
logger = logging.getLogger("patent")


#db setting
MONGODB_SERVER = '127.0.0.1'
MONGODB_PORT = 27017
DB = 'patent'
COLLECTION = 'spider'



def update_patent():
	now_time = time.strftime( '%Y-%m-%d %X', time.localtime())
	temp = time.strptime(now_time,'%Y-%m-%d %X')
	now = datetime.datetime(temp[0],temp[1],temp[2])
	connection = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
	db = connection[DB]
	collection = db[COLLECTION]
	#query url set where status!=0
	urls = collection.find({'status':{'$ne':0}})
	for url in urls:
		try:
			temp = time.strptime(url['last_time'],'%Y-%m-%d %X')
			last_time = datetime.datetime(temp[0],temp[1],temp[2])
			time_gap = (now-last_time).days
			continue
			if url['status']!=0 and url['feq']=='once':
				spider.click(url['content'],url['site'])
				collection.update({'site':url['site'],'content':url['content']},{'$set':{'inactive':1,'last_time':now_time,'status':0}})
			elif url['status']!=0 and urls['feq']=='week' and time_gap==7:
				spider.click(url['content'],url['site'])
				collection.update({'site':url['site'],'content':url['content']},{'$set':{'inactive':1,'last_time':now_time}})
			elif url['status']!=0 and urls['feq']=='month' and time_gap==30:
				spider.click(url['content'],url['site'])
				collection.update({'site':url['site'],'content':url['content']},{'$set':{'inactive':1,'last_time':now_time}})
			elif url['status']!=0 and urls['feq']=='day' and time_gap==1:
				spider.click(url['content'],url['site'])
				collection.update({'site':url['site'],'content':url['content']},{'$set':{'inactive':1,'last_time':now_time}})
		except Exception as e:
			logger.debug("update faile: content:{},site:{}"%(url['content'],url['site']))
			logger.debug(e)
		


def run():
	pass


if __name__ == '__main__':
	update_patent()