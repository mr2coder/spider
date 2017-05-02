import os,sys
import pymongo
import configparser
settings_file = os.path.join( os.path.dirname(__file__),"settings.py")
class mongoConnection(object):
    def __init__(self,**kwargs):
        settings = self.__load_configuration__(settings_file)
        connection=pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        if kwargs.get("db"):
            self.db=connection[kwargs['db']]
        else:
            self.db=connection[settings['MONGODB_DB']]
            
        if kwargs.get("collection"):
            self.collection=self.db[kwargs['collection']]
        else:
            self.collection=self.db[settings['MONGODB_COLLECTION']]

    def __load_configuration__(self, config_file):
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read(config_file)
        settings = {}
        settings['MONGODB_SERVER'] = config.get('connection_settings','MONGODB_SERVER').strip("'").strip("\"")
        settings['MONGODB_PORT'] = int(config.get('connection_settings','MONGODB_PORT').strip("'").strip("\""))
        settings['MONGODB_DB'] = config.get('connection_settings','MONGODB_DB').strip("'").strip("\"")
        settings['MONGODB_COLLECTION'] = config.get('connection_settings','MONGODB_COLLECTION').strip("'").strip("\"")
        return settings


if __name__ == '__main__':
	wanFang = mongoConnection()
	num = wanFang.collection.find({},{'keywords':1})
	for x in num:
		print (x["keywords"][0])