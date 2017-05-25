# -*- coding: utf-8 -*-
from you_get.common import *
from you_get.extractors import sina,qq,iqiyi,acfun,cntv,ifeng,bilibili,youku,tudou,sohu
import pymongo
import time,random




#db setting
MONGODB_SERVER = '127.0.0.1'
MONGODB_PORT = 27017
DB = 'video'
COLLECTION = 'urlinfo' 


def export_video():
	connection = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
	db = connection[DB]
	collection = db[COLLECTION]
	info = collection.find({"content":"金正恩"})
	print (type(info))
	output_dir = "../../../../web/static/video/"
	for x in info:
		print(x['videoname']+".txt")
		f=open(output_dir+x['videoname']+".txt",'w')

		print (x)
		x = str(x)
		print (type(x))
		
		f.write(x)
	f.close()





if __name__ == '__main__':
	export_video()  
