#-*- coding: utf-8 -*-
import json
import sys
sys.path.append('/home/zjun/Desktop/www/spider/web')
from mongo import mongoConnection
# import jieba
import chardet

def db_find(key):
	wanFang = mongoConnection.mongoConnection()
	result = wanFang.collection.find({},{key:1})
	return result

def paper_statistic(begin,end,key):
	key_words = db_find(key)
	key_dict = {}
	for line in key_words:
		if not isinstance(line[key],list):
			x = line[key]
			if key_dict.has_key(x):
				key_dict[x] +=1
			else:
				key_dict[x] = 1
		else:
			for x in line[key]:
				if key_dict.has_key(x):
					key_dict[x] +=1
				else:
					key_dict[x] = 1
			
	c = sorted(key_dict.iteritems(), key=lambda d:d[1],reverse=True)
	for x in c[begin:end]:
		print(x[0],x[1])
	return c[begin:end]

def sorted_by_times(ls):
	out_dict = {}
	for line in ls:
		if out_dict.has_key(line):
			out_dict[line] +=1
		else:
			out_dict[line] = 1
	c = sorted(out_dict.iteritems(), key=lambda d:d[1],reverse=True)
	return c

def institutions_sta(begin,end,key):
	inst = institutions('institutions')
	out = sorted_by_timea(inst)

def create_inst_list(db_find_out,key):
	normal_list = []
	for line in db_find_out:
		if not isinstance(line[key],list):
			normal_list.append(line[key])
		else:
			normal_list.extend(line[key])
	return normal_list


def institutions(key):
	title = '电子科技集团'
	institutions = db_find(key)
	institutions_clean = []
	institutions = create_inst_list(institutions,key)

	for institution in institutions:
		print (institution)
		new_names = clean_cetc(institution.encode("utf-8"),title)
		print (new_names)
		print ('---------')
		institutions_clean.append(new_names)
	out = sorted_by_times(institutions_clean)
	return out


def clean_cetc(institution,title):
	new_name = ''
	if_no_title_name = ''
	flag = False
	flag2 = False
	index = 0
	temp = ''
	no_title_name_flag = False
	#set separator
	separator = '所'
	institution = institution.split(';')[0]
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
	print (institution)
	n = {u'一':'1',u'二':'2',u'三':'3',u'四':'4',u'五':'5',u'六':'6',u'七':'7',u'八':'8',u'九':'9',u'十':' '}
	if title in institution:
		new_name += title
		flag = True

	if flag or no_title_name_flag:
		institution = institution+separator
	try:
		for c in institution.decode(chardet.detect(institution)['encoding']):
			if n.has_key(c):
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
	
	

def test():
	institution = '北京理工大学,北京,100081;中国电子科技集团公司第五十四研究所,河北,石家庄,050081'
	print (institution.split(',')[0])
	# institution = '中国电子科技集团公司第五十四研究所财务处'
	title = '电子科技集团'
	new_name = clean_cetc(institution,title)
	print (new_name)
	# se = jieba.cut(a, cut_all=False)
	# print "/".join(se)
	# for x in res:
	# 	se = jieba.cut(x[0], cut_all=False)
	# 	print "/".join(se)
	# n = {u'一':1,u'二':2,u'三':3,u'四':4,u'五':5,u'六':6,u'七':7,u'八':8,u'九':9}
	# for c in a.decode(chardet.detect(a)['encoding']):
	#     if n.has_key(c):
	#     	print n[c]
	#     if c <= '9' and c >= '0':
	#     	print c


	
if __name__ == '__main__':
	# res = paper_statistic(0,100,'institutions')
	# test()
	a = institutions('institutions')
	for x in a[:100]:
		print (x[0],x[1])