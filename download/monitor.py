# -*- coding:utf8 -*-
import sys, os, time, atexit, string
from signal import SIGTERM

class Daemon:
  def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    #需要获取调试信息，改为stdin='/dev/stdin', stdout='/dev/stdout', stderr='/dev/stderr'，以root身份运行。
    self.stdin = stdin
    self.stdout = stdout
    self.stderr = stderr
    self.pidfile = pidfile

  def _daemonize(self):
    try:
      pid = os.fork()
      if pid > 0:
        #退出主进程
        sys.exit(0)
    except OSError as e:
      sys.stderr.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
      sys.exit(1)

    os.chdir("/")
    os.setsid()
    os.umask(0)

    #创建子进程
    try:
      pid = os.fork()
      if pid > 0:
        sys.exit(0)
    except OSError as e:
      sys.stderr.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
      sys.exit(1)

    #重定向文件描述符
    sys.stdout.flush()
    sys.stderr.flush()
    si = file(self.stdin, 'r')
    so = file(self.stdout, 'a+')
    se = file(self.stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    #创建processid文件
    atexit.register(self.delpid)
    pid = str(os.getpid())
    file(self.pidfile,'w+').write('%s\n' % pid)

  def delpid(self):
    os.remove(self.pidfile)

  def start(self):
    #检查pid文件是否存在以探测是否存在进程
    try:
      pf = file(self.pidfile,'r')
      pid = int(pf.read().strip())
      pf.close()
    except IOError:
      pid = None

    if pid:
      message = 'pidfile %s already exist. Daemon already running?\n'
      sys.stderr.write(message % self.pidfile)
      sys.exit(1)

    #启动监控
    self._daemonize()
    self._run()

  def stop(self):
    #从pid文件中获取pid
    try:
      pf = file(self.pidfile,'r')
      pid = int(pf.read().strip())
      pf.close()
    except IOError:
      pid = None

    if not pid:
      message = 'pidfile %s does not exist. Daemon not running?\n'
      sys.stderr.write(message % self.pidfile)
      return #重启不报错

    #杀进程
    try:
      while 1:
        os.kill(pid, SIGTERM)
        time.sleep(0.1)
        # os.system('/opt/modules/hadoop/hadoop-0.20.203.0/bin/hadoop-daemon.sh stop datanode')
        # os.system('/opt/modules/hadoop/hadoop-0.20.203.0/bin/hadoop-daemon.sh stop tasktracker')
    except OSError as err:
      err = str(err)
      if err.find('No such process') > 0:
        if os.path.exists(self.pidfile):
          os.remove(self.pidfile)
      else:
        print (str(err))
        sys.exit(1)

  def restart(self):
    self.stop()
    self.start()

  def _run(self):
    while True:
      datanode = os.popen('ps aux | grep "python3 sina.py" | grep -v "grep"').read().strip()
      time.sleep(1)
      # "wc -l" ,statistic how many lines of the file or the result
      tasktracker = os.popen('ps aux | grep "python3 sina.py" | grep -v "grep" | wc -l').read().strip()
      print (datanode)
      #选出进程中含有python3且含有datanode|tasktracker且不含有grep，计算出现行数。修改上面的进程监控语句以适应其他应用需求
      if datanode == '0':
        os.system('python3 sina.py')
        #修改这里的启动命令
      time.sleep(2)
      #修改这里的停留时间






if __name__ == '__main__':
        daemon = Daemon('/tmp/watch_process.pid')
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        daemon.restart()
                else:
                        print ('Unknown command')
                        sys.exit(2)
                sys.exit(0)
        else:
                print ('usage: %s start|stop|restart' % sys.argv[0])
                sys.exit(2)