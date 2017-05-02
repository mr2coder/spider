import os
import time
import random
import sys
from multiprocessing import Process,current_process
def daemon():
    p = current_process()
    print ("starting ID%d prccess%s\n" % (p.pid,p.name))
    sys.stdout.flush()
    time.sleep(3)
    print ("Exiting:%s\n" % p.name)
    sys.stdout.flush()
def main():
    p = Process(name="Daemon",target=daemon)
    p.daemon=True
    p.start()
    p.join()
if __name__=="__main__":
    main()
    time.sleep(1)