"""
Event listener based on unix domain sockets or win32 named pipes

"""
from __future__ import print_function

import abc
import logging
from multiprocessing.connection import Listener, Client
import os
import socket
from threading import Thread

from chalmers import errors
from chalmers import config
import sys


log = logging.getLogger(__name__)

try:
    WindowsError
except NameError:
    WindowsError = SystemError

try:
    basestring
except NameError:
    basestring = str

def get_addr(name):
    """
    Get the address to the multiprocessing.connection.Listener or Client objects in
    a platform dependent way
    
    :param name: the name of the chalmers program to connect to
    """

    if os.name == 'nt':
        return r'\\.\pipe\chalmers:%s' % name
    else:
        socdir = os.path.join(config.dirs.user_data_dir, 'sockets')
        if not os.path.isdir(socdir):
            os.makedirs(socdir)

        sock_path = os.path.join(socdir, '%s' % name)

        if sys.version_info.major < 3:
            sock_path = sock_path.encode()

        return sock_path

class EventDispatcher(object):
    """
    This dispatches events listened to from the Listener
    
    """
    __metaclass__ = abc.ABCMeta
    FAMILY = 'AF_PIPE' if os.name == 'nt' else 'AF_UNIX'

    def __init__(self):
        self._running = False
        self._listener = None

    @property
    def listener(self):
        "Return the multiprocessing Listener object"
        if self._listener is None:
            if self.FAMILY == 'AF_UNIX' and os.path.exists(self.addr):
                os.unlink(self.addr)
            try:
                log.debug("Listening to events from: %s" % self.addr)
                self._listener = Listener(self.addr, family=self.FAMILY)
            except socket.error as err:
                if err.errno == 48:
                    msg = "Unix socket '%s' appears to be in use. Please stop this program."
                    raise errors.ChalmersError(msg % self.addr)
                else:
                    raise
        return self._listener

    def start_listener(self):
        "Start listening to the listener in a new thread"
        self._running = True
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
        'Exit the listener'
        self._running = False

    def dispatch_ping(self):
        'return the pid of this process'
        return os.getpid()

    @property
    def is_listening(self):
        return self._running

    def listen(self):
        """Listen to incoming clients until
        self._running is set to False
        """
        l = self.listener
        self._running = True
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


                log.info('Dispatch action "%s"' % action)
                method = getattr(self, 'dispatch_%s' % action, None)
                if method:
                    try:
                        result = method(*args, **kwargs)
                    except Exception as err:
                        log.exception(err)
                        c.send({'error':True, 'message':'Exception in action %s - %s' % (action, err)})
                    else:
                        c.send({'error':False, 'message':'ok', 'result': result})
                else:
                    log.warn('No action %s' % action)
                    c.send({'error':True, 'message':'No action %s' % action})
                c.close()
        finally:
            self._listener = None
            l.close()

        log.info("Exiting event loop")

    def send(self, action, *args, **kwargs):
        'Dispatch an action to a Dispatcher'
        return send_action(self.name, action, *args, **kwargs)

def send_action(name, action, *args, **kwargs):
    """
    Send an action to a listener
    the listener must have a 'dispatch_{action}' method
    or this will raise a ChalmersError
    """

    addr = get_addr(name)
    try:
        c = Client(addr, family=EventDispatcher.FAMILY)
    except (socket.error, WindowsError):
        raise errors.ConnectionError("Could not connect to chalmers program %s" % name)

    try:
        c.send({'action': action, 'args':args, 'kwargs':kwargs})
        res = c.recv()

        if res.get('error'):
            raise errors.ChalmersError(res.get('message', 'Unknown error'))
        return res.get('result')
    finally:
        c.close()


