
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

  @timeit
  def folder_status(self, folder_name):
    c = self.getConn()
    ret = c.folder_status(folder_name)
    self.putConn(c)
    return ret

  @timeit
  def messages(self, folder_name, c=None):
    put_back_conn = True
    if not c:
      c = self.getConn()
      put_back_conn = False
    c.select_folder(folder_name)
    ids = c.search()
    ret = c.fetch(ids, ['BODY'])

    for r in ret:
      print "-" * 80
      print r, ret[r]
      print "*" * 80


    if put_back_conn:
      self.putConn(c)
    return ret
