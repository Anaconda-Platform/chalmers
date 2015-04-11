from __future__ import print_function, absolute_import, unicode_literals

from multiprocessing import Process, Queue
from threading import Thread
import sys
import time
from os import path
from clyent import print_colors
from random import shuffle
from itertools import cycle

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




    def __init__(self, stream=False, color=False):
        self.stream = stream
        self.color = color

        self.processes = []
        self.programs = []

        self.queue = Queue()
        self.finished = False
        self.watched = []
        self.creating = []




    def printer_loop(self):

        colors = cycle(['blue', 'green', 'red', 'bold', 'yello'])
        color = iter(colors)
        color_map = {}

        try:
            while not self.finished:
                seen_data = False
                for name, fd in self.watched:
                    if self.color and name not in color_map:
                        color_map[name] = next(color)

                    data = fd.readline()
                    while data:
                        seen_data = True
                        if self.color:
                            print_colors("[{name!c:{color}}] ", end='', color=color_map[name], name=name)
                        else:
                            print("[{%s}] " % name, end='')

                        print(data, end='')
                        data = fd.readline()

                if not seen_data:
                    time.sleep(.1)
                if self.creating:
                    program = self.creating[-1]
                    stdout_file = program.data.get('stdout')
                    if path.isfile(stdout_file):
                        fd = open(stdout_file)
                        self.watched.append([program.name, fd])
                        self.creating.pop()

        finally:
            for _, fd in self.watched:
                try:
                    fd.close()
                except IOError: pass

    def append(self, program):
        stdout_file = program.data.get('stdout')

        if stdout_file:
            if path.isfile(stdout_file):
                fd = open(stdout_file)
                fd.seek(0, 2)
                self.watched.append([program.name, fd])
            else:
                self.creating.append(program)

        proc = Process(target=program.start, kwargs={'daemon': False})
        proc.start()
        self.processes.append(proc)
        self.programs.append(program)



    def join(self):

        if self.stream:
            self.printer = Thread(target=self.printer_loop)
            self.printer.start()

        try:
            for proc in self.processes:
                proc.join()
        finally:
            self.finished = True
