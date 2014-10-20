from threading import Thread
import os
import time

class FileEcho(Thread):

    def __init__(self, filename, stream):
        self.filename = filename
        self.stream = stream
        self.fd = open(filename, 'a+', 0)
        self.fd.seek(0, os.SEEK_END)
        self.pos = self.fd.tell()
        self._running = True

        Thread.__init__(self, name='file_echo')
        self.daemon = True

    def stop(self):
        self._running = False

    def run(self):
        while self._running:
            if self.pos <= os.fstat(self.fd.fileno()).st_size:
                self.fd.seek(self.pos)
                data = self.fd.read()
                self.pos = self.fd.tell()
                self.stream.write(data)
            else:
                time.sleep(1)

