
from gevent import monkey; monkey.patch_all()
from gevent.queue import Queue
from timeit import timeit
from imapclient import IMAPClient

MAX_CONNECTIONS = 2

class ImapConnection(object):
  def __init__(self, server="imap.gmail.com", username="vfct3st@gmail.com", passwd="GWxE6kBs436wa7tyedyU"):
    self.server = server
    self.username = username
    self.passwd = passwd
    self.pool = Queue()
    self.size = 0

  def login(self):
   return self.folders()
  def _login(self):
    conn = IMAPClient(self.server, use_uid=True, ssl=True)
    conn.login(self.username, self.passwd)
    return conn

  def getConn(self):
    if (self.size >= MAX_CONNECTIONS):
      return self.pool.get()
    else:
      self.size += 1
      try:
        c = self._login()
      except:
        self.size -= 1
        raise
      return c
