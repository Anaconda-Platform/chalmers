
import sys
import logging

class FormatterWrapper(object):

    def __init__(self, formatter, prefix='', suffix=''):
        self.prefix = prefix
        self.suffix = suffix
        self.formatter = formatter

    def format(self, record):
        result = self.formatter.format(record)
        return '%s%s%s' % (self.prefix, result, self.suffix)

    @classmethod
    def wrap(cls, handler, prefix='', suffix=''):
        old_formatter = handler.formatter or logging.Formatter()
        new_formatter = cls(old_formatter, prefix, suffix)
        handler.setFormatter(new_formatter)


class ColorFormatter(object):

    WARNING = '\033[93m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = "\033[1m"
    COLOR_MAP = {'ERROR': '%s%s[%%s]%s' % (BOLD, FAIL, ENDC),
                 'WARNING': '%s%s[%%s]%s' % (BOLD, WARNING, ENDC),
                 'DEBUG': '%s%s[%%s]%s' % (BOLD, OKBLUE, ENDC),
                 }

    def color_map(self, header, level):
        return self.COLOR_MAP.get(level, '[%s]') % header

    def __init__(self, isatty=True):
        self.isatty = isatty

    def format(self, record):
        if record.levelno == logging.INFO:
            header = None
            message = record.getMessage()
        else:
            if record.exc_info:
                err = record.exc_info[1]
                header = type(err).__name__
                if err.args:
                    message = err.args[0]
                else:
                    message = str(err)
            else:
                header = record.levelname.lower()
                message = record.getMessage()

        if header:
            if self.isatty and not sys.platform.startswith('win'):
                header = self.color_map(header, record.levelname)
            return '%s %s\n' % (header, message)
        else:
            return '%s\n' % message

class MyStreamHandler(logging.Handler):
    def __init__(self, level=logging.INFO):

        logging.Handler.__init__(self, level=logging.INFO)
        self.setFormatter(ColorFormatter(sys.stdout.isatty()))

    def emit(self, record):

        if not self.filter(record):
            return

        fmt = self.format(record)

        if record.levelno == logging.INFO:
            stream = sys.stdout
        else:
            stream = sys.stderr

        stream.write(fmt)

