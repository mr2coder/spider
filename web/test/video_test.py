# -*- coding:utf8 -*-
import sys,time,datetime
from pprint import pprint
sys.path.append("..")
import pymongo
import python.video.models as models
MONGODB_SERVER = '127.0.0.1'
MONGODB_PORT = 27017
DB = 'video'
COLLECTION = 'urlinfo'

# pprint (sys.path)

def test_sina_url_spider():
	models.sina_url_spider("金正恩")

def test_api_play_info():
	pass

def test_video_gragh():
	connection = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
	db = connection[DB]
	collection = db[COLLECTION]
	content = '金正恩'
	site = 'sina'
	info = collection.find({'content':content,'site':site},{'spidertime':1})
	info = [str(x['spidertime'].split(' ')[0]) for x in info]
	import collections
	info = dict(collections.Counter(info))
	oneday = datetime.timedelta(days=1) 
	now = datetime.date.today()
	yday = now-oneday*2
	x = [str(now-oneday*x) for x in range(30)]
	x.reverse()
	print (info,now,yday)
	print (x)

def test_bilibili_url_spider():
	doc = models.bilibili_url_spider("时间")
	return doc

def test_video_detail():
	content = '半岛局势'
	site = 'bilibili'
	mongo = mongoConnection.mongoConnection(db='video',collection='urlinfo')
	info = mongo.collection.find({'content':content,'site':site},{'_id':0})
	info = [x for x in info]
	print (info)



if __name__ == '__main__':
    test_video_detail()
