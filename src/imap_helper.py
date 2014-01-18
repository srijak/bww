
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

  @timeit
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
  @timeit
  def select(self, folder_name):
    # selects a folder with a dedicated connection.
    # this is why every folder specific action requires
    # a foldername
    c = self.getConn()
    ret = c.select_folder(folder_name)
    self.putConn(c)
    return ret
