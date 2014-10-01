from contextlib import contextmanager
import itertools
import logging
from multiprocessing import Process, Manager
import random
import sys

from chalmers.event_dispatcher import EventDispatcher
from chalmers.program import Program
from clyent.logs.handlers import ColorStreamHandler
from clyent.logs.formatters import FormatterWrapper
from clyent.logs.colors import color

log = logging.getLogger(__name__)

class ProgramManager(EventDispatcher):
    """
    Manages chalmers programs with multiprocessing
    
    Listens to 'start' events to start new programs
    """

    NAME = 'chalmers_manager'

    COLOR_CODES = range(40, 48) + [100, 102, 104, 105, 106]
    random.shuffle(COLOR_CODES)

    def __init__(self, exit_on_first_failure=False, use_color=None):
        EventDispatcher.__init__(self)
        self.manager = Manager()
        self.processes = []

        if use_color is None:
            use_color = sys.stdout.isatty()

        self.use_color = use_color
        self.bg_colors = itertools.cycle(color.BACKGROUND_COLORS)
        self.exit_on_first_failure = exit_on_first_failure


    @property
    def name(self):
        return self.NAME

    def dispatch_start(self, name):
        log.info("Managing Program %s" % name)
        p = Process(target=start_program,
                    name='start_program:%s' % name,

                    args=(name,),
                    kwargs={'color_id': self.use_color and next(self.bg_colors)})

        p.start()
        self.processes.append(p)

    def start_all(self):
        for prog in Program.find_for_user():
            if not prog.is_paused:
                self.dispatch_start(prog.name)
            else:
                log.info("Not starting program %s (it is paused)" % (prog.name))

    @contextmanager
    def cleanup(self, prog):
        try:
            yield
        except KeyboardInterrupt:
            log.error('KeyboardInterrupt')
        finally:
            if not prog.is_ok:
                log.info("Program manager letting program fail")


def start_program(name, color_id=None):

    logger = logging.getLogger('chalmers')

    prefix = '[%s]' % name
    if color_id is not None:
        prefix = color(prefix, [color_id, color.WHITE])

    if not logger.handlers:
        shndlr = ColorStreamHandler(color_id is not None)
        shndlr.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
        logger.addHandler(shndlr)

    for h in logger.handlers:
        FormatterWrapper.wrap(h, prefix=prefix)
    prog = Program(name)

    prog.start_sync()

