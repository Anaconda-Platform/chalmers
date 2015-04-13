import logging
import os
from threading import Thread
import time


log = logging.getLogger(__name__)

class FileEcho(Thread):
    """
    Perhaps obsolete class that echos the stdout logfile
    for a program
    """

    def __init__(self, filename, stream):
        self.filename = filename
        self.stream = stream
        self._running = True
        Thread.__init__(self, name='file_echo')
        self.daemon = True

    def stop(self):
        self._running = False

    def run(self):

        with open(self.filename, 'a+', 1) as fd:
            fd.seek(0, os.SEEK_END)
            pos = fd.tell()

            while self._running:
                if pos < os.fstat(fd.fileno()).st_size:
                    fd.seek(pos)
                    data = fd.read()
                    if isinstance(data, bytes):
                        data = data.decode('utf-8')
                    pos = fd.tell()
                    try:
                        self.stream.write(data)
                    except TypeError as err:
                        log.exception(err)
                else:
                    time.sleep(1)

