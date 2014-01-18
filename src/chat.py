from gevent import monkey; monkey.patch_all()

from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from imap_helper import ImapConnection
import simplejson
import threading

class MailboxNamespace(BaseNamespace, BroadcastMixin):
    def recv_connect(self):
      self.conn = ImapConnection()
      self.lock = threading.Lock()
      folders = self.conn.login()
      self.emit("folders", folders)
      for fname in folders:
        self.spawn(self.sync_folder, fname, folders[fname][1])

      # when get new connection send back:
      # list of mailboxes

      print 'EMITTED'
    def sync_folder(self, folder, flags):
      # each folder should probably have it's own connection.
      # makes sense in terms of IDLE too.
      if u'\\Noselect' in flags:
        print "Noselect folder ", folder
        return
      print "SELECTing ", folder, flags

      self.lock.acquire()
      info = self.conn.folder_status(folder)
      self.emit("folder_info" , {'name': folder, 'data': info} )
      messages = self.conn.messages(folder, conn)
      self.lock.release()
      self.emit('messages', {'folder': folder, 'messages': messages})



class Application(object):
    def __init__(self):
        self.buffer = []
        self.request = {
        }

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/')
        if path.startswith("socket.io"):
            socketio_manage(environ, {'/mailbox': MailboxNamespace}, self.request)
        else:
            return not_found(start_response)


def not_found(start_response):
    start_response('404 Not Found', [])
    return ['<h1>Not Found</h1>']


if __name__ == '__main__':
    print 'Listening on port 18080 and on port 843 (flash policy server)'
    SocketIOServer(('0.0.0.0', 18080), Application(),
        resource="socket.io", policy_server=True,
        policy_listener=('0.0.0.0', 10843)).serve_forever()
