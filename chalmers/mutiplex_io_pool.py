from __future__ import print_function, absolute_import, unicode_literals

from multiprocessing import Process, Queue
from threading import Thread
import sys

class stdq(object):
    def __init__(self, name, queue, out):
        self.queue = queue
        self.out = out
        self.name = name

    def write(self, data):
        self.out.write('X %r' % repr(data))
        import traceback
        self.out.write('-- traceback.print_stack --\n')
        traceback.print_stack(file=self.out)
        self.out.write('-- traceback.print_stack --\n')
        afd
        if data:
            self.out.write('X %r' % repr(data))
            self.queue.put([self.name, data])
        # self.out.write(data)

    def flush(self):
        pass

def iotarget(name, target):
    def iotarget_inner(*args, **kwargs):
        queue = kwargs.pop('queue')
        stdout = sys.stdout
        sys.stdout = stdq(name, queue, stdout)
        return target(*args, **kwargs)
    return iotarget_inner

class MultiPlexIOPool(object):




    def __init__(self):
        self.processes = []

        self.queue = Queue()
        self.finished = False

        self.printer = Thread(target=self.printer_loop)
        self.printer.daemon = True
        self.printer.start()
        self.queue.put(['main', 'staring io loop\n'])



    def printer_loop(self):
        while not self.finished:
            name, data = self.queue.get()
            if data:
                end = '' if data.endswith('\n') else '\n'
                print('[%s] %s' % (name, data), end=end)


    def append(self, name, target, *args, **kwargs):


        if sys.stdout.isatty():
            target = iotarget(name, target)
            kwargs['queue'] = self.queue

        proc = Process(target=target, args=args, kwargs=kwargs)
        proc.start()
        self.processes.append(proc)

    def join(self):
        for proc in self.processes:
            proc.join()
        self.finished = True
