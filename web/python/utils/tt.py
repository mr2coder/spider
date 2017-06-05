# -*- coding:utf8 -*-
# from mongo import mongoConnection

from spider import urlSpider
import requests
from lxml import html
import re,time,datetime
from multiprocessing.dummy import Pool as ThreadPool  
import argparse
import os
from iqiyi import *


#add sys.path
import logging.config
path = os.path.abspath(__file__).replace('\\','/').split('/')
#add sys.path
import sys




#==================bilibili==============

#========================iqiyi=======================
   
#=========================sina========================
def sina_url_spider():
   print("ninininini44444")
   try:
      print("ninininini44444")
      content = "朝鲜"
      thread_num = 1
      print("ninininini44444")
      patt = "http://so.video.sina.com.cn/interface/s?from=video&wd={content}&s_id=w00001&p={page}&n=20"
      start_url = patt.format(content=str(content), page='1')
      response = requests.get(start_url)
      json_data = response.json()
      total_num = json_data["total"]
      logger.info('total items:'+str(total_num))
      #get url's detail infomation
      print("ninininini44444")
      def get_info(url):
         print("ninininini4444411111")
         logger.info('Currently crawling web pages is: '+url)
         print("ninininini44444")
         response = requests.get(url)
         if response.status_code!=200: return None
         result = [{"videoname":re.compile(r'(<.*?>)').sub("",x.get("videoname")),
                  "url":x.get("url"),
                  "showtime":x.get("showtime"),
                  "videoinfo":x.get("videoinfo"),
                  "playtimes":x.get("playtimes"),
                  "spidertime":time.strftime( '%Y-%m-%d %X', time.localtime()),
                  "site":"sina",
                  "content":content,
                  "status":1 } for x in response.json()["list"]]
         print(result)
         print("1111111111111")
         return 0
      #creat all page url
      urls = [patt.format(content=content, page=str(x+1)) for x in range((int(total_num)+19)//20)]
      if 1:
         for url in urls:
            print(url)
            get_info(url) 
      else:
         pool = ThreadPool(thread_num)
         results = pool.map(get_info, urls)
      logger.info('Success: Task update finshed..')
   except Exception as e:
      logger.debug(e)


#调用爬虫入口函数
def click(content,site,socketio=None,proxy=False):
   print("ninininini222222")
   args = {}
   logger.info(content+':'+site)
   args['content'] = content
   args['site'] = site
   mongoDB = mongoConnection.mongoConnection(db='video',collection='spider')
   time_ = time.strftime( '%Y-%m-%d %X', time.localtime())
   infomation_id = mongoDB.collection.update({
      'site':site,'content':content},{'$set':{'inactive':1,'last_time':time_}})
   url_spider(args,socketio=socketio)

def auto_run():
   print("ninininini111")
   mongo = mongoConnection.mongoConnection(db='video',collection='spider')
   tasks = list(mongo.collection.find({},{'content':1,'site':1,'_id':0}))
   tasks = [(x['content'],x['site']) for x in tasks]
   for x in tasks:
      click(*x)

def main():
   print("ninininini")
   parser = argparse.ArgumentParser()
   parser.add_argument('-t','--type',dest='type')
   parser.add_argument('-c','--content',dest='content')
   parser.add_argument('-s','--site',dest='site')
   args = parser.parse_args()
   print(args)
   content = args.content
   site = args.site
   print("ninininini55555")
   if(args.type=='click'):
      click(content,site)
      print("ninininini55555111")
   elif args.type=='auto':
      auto_run()
      print("ninininini55555111")





if __name__ == '__main__':
   # content = '美国'
   # site = 'sina'
   # click(content,site)
   print('hhhh')
   logger.info('hhh')
   sina_url_spider()
   # main()