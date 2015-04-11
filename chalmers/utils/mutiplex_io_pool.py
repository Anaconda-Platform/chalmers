from __future__ import print_function, absolute_import, unicode_literals

from itertools import cycle
from multiprocessing import Process, Queue
from os import path
from threading import Thread
import time

from clyent import color

import logging
log = logging.getLogger(__name__)


class ColorPicker(object):

    light_fg_colors = ['yello', 'white']
    light_bg_colors = [43, 46, 47, 103, 107]
    dark_fg_colors = ['blue', 'red', 'green', 30]
    dark_bg_colors = [40, 41, 42, 44, 45, 100, 102, 104, 105, 106]

    def next_color(self):
        yield color(None, (6,))
        yield color(None, (7,))

        for fg in self.light_fg_colors:
            for bg in self.dark_bg_colors:
                yield color(None, (fg, bg))

        for fg in self.dark_fg_colors:
            for bg in self.light_bg_colors:
                yield color(None, (fg, bg))

    def __init__(self):
        self.color_map = {}
        self.color_iter = iter(cycle(self.next_color()))

    def __getitem__(self, name):
        if name not in self.color_map:
            self.color_map[name] = next(self.color_iter)

        return self.color_map[name]



class MultiPlexIOPool(object):
    """
    This class runs programs in a sub-process optionally it watches their 
    stdout file outputs and multiplexes the output to the current processes stdout
    """

    def __init__(self, stream=False, use_color=False):
        self.stream = stream
        self.use_color = use_color

        self.processes = []
        self.programs = []

        self.queue = Queue()
        self.finished = False
        self.watched = []
        self.creating = []




    def printer_loop(self):

        colors = ColorPicker()

        try:
            while not self.finished:
                seen_data = False
                for name, fd in self.watched:

                    data = fd.readline()
                    while data:
                        seen_data = True
                        if self.use_color:
                            with colors[name]:
                                print('[%s]' % name, end='')
                            print(" ", end='')
                        else:
                            print("[%s]" % name, end='')

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

    def start_program(self, program):
        def setup_program():
            try:
                program.start(daemon=False)
            except KeyboardInterrupt:
                log.error('Program %s is shutting down' % program.name)
        return setup_program

    def append(self, program):
        stdout_file = program.data.get('stdout')

        if stdout_file:
            if path.isfile(stdout_file):
                fd = open(stdout_file)
                fd.seek(0, 2)
                self.watched.append([program.name, fd])
            else:
                self.creating.append(program)

        proc = Process(target=self.start_program(program))
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
