import abc
import logging
from multiprocessing.connection import Listener, Client
import os
import socket
from threading import Thread

from chalmers import errors
from chalmers.config import dirs


log = logging.getLogger(__name__)


def get_addr(name):
    """
    Get the address to the multiprocessing.connection.Listener or Client objects in
    a platform dependent way
    
    :param name: the name of the chalmers program to connect to
    """

    if os.name == 'nt':
        return r'\\.\pipe\chalmers:%s' % name
    else:
        socdir = os.path.join(dirs.user_data_dir, 'sockets')
        if not os.path.isdir(socdir):
            os.makedirs(socdir)
        sock_path = os.path.join(socdir, '%s' % name).encode()
        return sock_path

class EventDispatcher(object):
    """
    This dispatches events listened to from the Listener
    
    """
    __metaclass__ = abc.ABCMeta
    FAMILY = 'AF_PIPE' if os.name == 'nt' else 'AF_UNIX'

    def __init__(self):
        self._running = True
        self._listener = None

    @property
    def listener(self):
        if self._listener is None:
            try:
                log.info("Listening to events from: %s" % self.addr)
                self._listener = Listener(self.addr, family=self.FAMILY)
            except socket.error as err:
                if err.errno == 48:
                    raise errors.ChalmersError("Unix socket '%s' appears to be in use. Please stop this program." % self.addr)
                else:
                    raise
        return self._listener

    def start_listener(self):

        self.listener  # Force listener to connect before running in thread
        self._listener_thread = Thread(target=self.listen)
        self._listener_thread.start()

    @abc.abstractproperty
    def name(self):
        return 'chalmers'

    @property
    def addr(self):
        return get_addr(self.name)

    def dispatch_exitloop(self):
        self._running = False

    def dispatch_ping(self):
        return os.getpid()

    def listen(self):

        l = self.listener

        try:
            while self._running:
                log.debug("Accept connection")
                c = l.accept()

                try:
                    action = c.recv()
                except EOFError:
                    c.close()
                    continue
                if isinstance(action, basestring):
                    args = ()
                    kwargs = {}
                else:
                    args = action.get('args', ())
                    kwargs = action.get('kwargs') or {}
                    action = action.get('action')

                method = getattr(self, 'dispatch_%s' % action, None)

                if method:
                    try:
                        result = method(*args, **kwargs)
                    except Exception as err:
                        log.exception(err)
                        c.send({'error':True, 'message':'Exception in action %s - %s' % (action, err)})
                        raise
                    else:
                        c.send({'error':False, 'message':'ok', 'result': result})
                else:
                    c.send({'error':True, 'message':'No action %s' % action})
                    pass
                c.close()
        finally:
            self._listener = None
            l.close()

        log.info("Exiting event loop")

def send_action(name, action, *args, **kwargs):
    addr = get_addr(name)

    c = Client(addr, family=EventDispatcher.FAMILY)

    try:
        c.send({'action': action, 'args':args, 'kwargs':kwargs})
        res = c.recv()

        if res.get('error'):
            raise errors.ChalmersError(res.get('message', 'Unknown error'))
        return res.get('result')
    finally:
        c.close()


