base_url = "http://s.wanfangdata.com.cn/Paper.aspx?q="
import logging  
logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    filename='test.log',  
                    filemode='w')  
  
logging.debug('debug message')  
logging.info('info message')  
logging.warning('warning message')  
logging.error('error message')  
logging.critical('critical message')  