"""

"""
from __future__ import print_function, absolute_import, unicode_literals

from chalmers.utils.color_picker import ColorPicker
from chalmers.program import Program
import logging
from multiprocessing import Process, Queue
from os import path
from threading import Thread
import time


log = logging.getLogger(__name__)

SLEEP_START = 0.1
SLEEP_INC = 0.05
SLEEP_MAX = 1.0

def start_program(name):
    program = Program(name)
    # Remove base logging handlers, this is read from the log files that are
    # set up after the start method
    logger = logging.getLogger('chalmers')
    logger.handlers = []
    logger.handlers.append(logging.NullHandler())
    try:
        program.start(daemon=False)
    except KeyboardInterrupt:
        log.error('Program %s is shutting down' % program.name)

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
        sleep_time = SLEEP_START

        try:
            while not self.finished:
                seen_data = False
                for name, fd in list(self.watched):
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
                    time.sleep(sleep_time)
                    sleep_time = SLEEP_MAX if sleep_time >= SLEEP_MAX else sleep_time + SLEEP_INC
                else:
                    sleep_time = SLEEP_START

                self.manage_logs()

        finally:
            for _, fd in self.watched:
                try:
                    fd.close()
                except IOError: pass

    def manage_logs(self):
        if not self.creating:
            return
        name, filename = self.creating[-1]
        if path.isfile(filename):
            fd = open(filename)
            self.watched.append([name, fd])
            self.creating.pop()


    def add_log_streams(self, name, filename):

        if filename:
            if path.isfile(filename):
                fd = open(filename)
                fd.seek(0, 2)
                self.watched.append([name, fd])
            else:
                self.creating.append([name, filename])


    def append(self, program):

        proc = Process(target=start_program, args=(program.name,))
        self.programs.append(program)
        self.processes.append(proc)

        if self.stream:
            self.add_log_streams(program.name, program.data.get('daemon_log'))
            self.add_log_streams(program.name, program.data.get('stdout'))

        proc.start()


    def join(self):

        if self.stream:
            self.printer = Thread(target=self.printer_loop)
            self.printer.start()

        try:
            for proc in self.processes:
                proc.join()

        finally:
            self.finished = True


        log.info("All programs exited")

