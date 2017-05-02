import subprocess,time
import sys,os
sys.path.append('/home/zjun/Desktop/www/spider/web/python/utils/')

popen = subprocess.Popen(
			['python', 'video_url_spider.py','-t','click','-c','美国','-s','sina'], 
			stdout = subprocess.PIPE)
#######################################################
# popen = subprocess.Popen(
# 			['python', 'patent_url_spider.py','-t','click','-c',
# 			'58e4e4881d41c87250c0a25a'], 
# 			stdout = subprocess.PIPE)
while True:
	line = popen.stdout.readline()
	print(line.decode("utf-8"))
	time.sleep(1)

# a = [1,2,3,34,4]
# b = [1,2,3]
# a = [value for index,value in enumerate(a) if index not in b]
# print(a)
