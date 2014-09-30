import itertools
import logging
from multiprocessing import Process
import sys

from chalmers.event_handler import EventHandler
from chalmers.program import Program
from chalmers.utils.handlers import FormatterWrapper
import random
from contextlib import contextmanager


log = logging.getLogger(__name__)

class ProgramManager(EventHandler):

    COLOR_CODES = range(40, 48) + [100, 102, 104, 105, 106]
    random.shuffle(COLOR_CODES)
    def __init__(self, *args, **kwargs):
        EventHandler.__init__(self, *args, **kwargs)
        self.processes = []
        self.programs = []
        self.bg_colors = itertools.cycle(self.COLOR_CODES)


    @property
    def name(self):
        return 'chalmers'

    def action_start(self, name):

        p = Process(target=self.start_program,
                    name='start_program:%s' % name,

                    args=(name,),
                    kwargs={'color': next(self.bg_colors)})
        p.start()
        self.processes.append(p)

    def start_all(self):
        for prog in Program.find_for_user():
            if not prog.is_paused:
                self.action_start(prog.name)
                self.programs.append(prog)
            else:
                log.info("Not starting program %s (it is paused)" % (prog.name))

    def start_program(self, name, color=None):

        logger = logging.getLogger('chalmers')

        prefix = '[%s]'
        if color and sys.stdout.isatty():
            bg_color = next(self.bg_colors)
            prefix = '\033[97m\033[%im%s\033[49m\033[39m' % (bg_color, prefix)

        prefix += ' '


        for h in logger.handlers:
            FormatterWrapper.wrap(h, prefix=prefix % name)
        prog = Program(name)
        self.programs.append(prog)
        with self.cleanup():
            prog.start_sync()


    @contextmanager
    def cleanup(self):
        yield


