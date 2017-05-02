import requests,sys,os
import spider
import re
from lxml import html
import logging
# from ...mongo import mongoConnection

class FormData(object):
	"""docstring for FormData"""
	def __init__(self,content=''):
		super(FormData, self).__init__()
		self.searchCondition_searchExp = content			# input content
		self.search_scope = ''								# not clear...
		self.searchCondition_dbId = 'VDB'					# not clear...
		self.resultPagination_limit = 50					# the num of paper in the same page
		self.searchCondition_searchType = 'Sino_foreign'	# not clear...
		self.wee_bizlog_modulelevel = '0200101'				# 'wee' is a front-end frame,just know about that...
		self.resultPagination_start = 1						# seem like the pagenum,not clear...

	def get_form(self):
		#return form data as requests's requirement
		result = {
			'searchCondition.searchExp':self.searchCondition_searchExp,
			'search_scope':self.search_scope,
			'searchCondition.dbId':self.searchCondition_dbId,
			'resultPagination.limit':self.resultPagination_limit,
			'searchCondition.searchType':self.searchCondition_searchType,
			'wee.bizlog.modulelevel':self.wee_bizlog_modulelevel,
			'resultPagination.start':self.resultPagination_start
		}
		return result



def test():
	#new request
	re_html = re.compile('<.*?>')
	url = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/showSearchResult-startWa.shtml'
	form = FormData('申请（专利权）人=(吉林大学) AND 发明名称=(雷达)').get_form()
	response = requests.post(url, data=form)
	doc = html.fromstring(response.text)
	total = doc.xpath('//input[@id="result_totalCount"]/@value')
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
	proxys = doc.xpath('//div[@class="item-content-body left"]/p[8]/text()')
	proxy_insititutions = doc.xpath('//div[@class="item-content-body left"]/p[9]/text()')
	logging.info(total,titles,t_ids,r_dates,o_ids,o_dates,icp_ids,insititutions,authors,proxys,proxy_insititutions)


if __name__ == '__main__':
	test()
	# print (os.path.dirname(__file__))
