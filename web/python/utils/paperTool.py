import sys,pprint
from mongo import mongoConnection

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
			if key_dict.get(x):
				key_dict[x] +=1
			else:
				key_dict[x] = 1
		else:
			for x in line[key]:
				if key_dict.get(x):
					key_dict[x] +=1
				else:
					key_dict[x] = 1
			
	c = sorted(key_dict.items(), key=lambda d:d[1],reverse=True)
	# for x in c[begin:end]:
	# 	print x[0],x[1]
	return c[begin:min(end,len(c))]

def sorted_by_times(ls):
	out_dict = {}
	for line in ls:
		if out_dict.get(line):
			out_dict[line] +=1
		else:
			out_dict[line] = 1
	c = sorted(out_dict.items(), key=lambda d:d[1],reverse=True)
	return c

		
def get_count(**kwargs):
	#default collection:paper_new
	#get collection's item num
	wanFang = mongoConnection.mongoConnection(**kwargs)
	result = wanFang.collection.count()
	return result

def get_collections(**kwargs):
	wanFang = mongoConnection.mongoConnection(**kwargs)
	collections =  wanFang.db.collection_names()
	collections.remove('system.indexes')
	data = [{'collection':x,'count':wanFang.db[x].count()} for x in collections]
	return data

if __name__ == '__main__':
	pprint.pprint(sys.path)
	print (get_collections())