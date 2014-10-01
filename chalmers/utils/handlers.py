
import sys
import logging
from chalmers.utils.colors import color
import traceback

class FormatterWrapper(object):

    def __init__(self, formatter, prefix='', suffix=''):
        self.prefix = prefix
        self.suffix = suffix
        self.formatter = formatter

    def format(self, record):
        result = self.formatter.format(record)
        if not isinstance(result, list):
            result = [result]

        if self.prefix:
            result.insert(0, self.prefix)
        if self.suffix:
            result.append(self.suffix)
        return result

    @classmethod
    def wrap(cls, handler, prefix='', suffix=''):
        old_formatter = handler.formatter or logging.Formatter()
        new_formatter = cls(old_formatter, prefix, suffix)
        handler.setFormatter(new_formatter)


class ColorFormatter(object):

    COLOR_MAP = {'ERROR': (color.BOLD, color.RED),
                 'WARNING': (color.BOLD, color.YELLO),
                 'DEBUG': (color.BOLD, color.BLUE),
                 }

    def color_map(self, header, level):
        header = '[%s]' % header
        if level in self.COLOR_MAP:
            return color(header, self.COLOR_MAP[level])
        else:
            return header

    def __init__(self, isatty=True, short_tb=()):
        self.isatty = isatty
        self.short_tb = short_tb

    def format(self, record):
        if record.levelno == logging.INFO:
            header = None
            message = record.getMessage()
        else:
            if record.exc_info:
                err = record.exc_info[1]
                header = type(err).__name__
                result = [self.color_map(header, record.levelname)]

                if hasattr(err, 'message'):
                    result.append(str(err.message))
                elif err.args:
                    result.append(str(err.args[0]))

                if not isinstance(err, self.short_tb):
                    message = ''.join(traceback.format_exception(*record.exc_info))
                    result.append('\n' + message)
                return result
#                 else:
#                     message = str(err)
            else:
                header = record.levelname.lower()
                message = record.getMessage()

        if header:
            header = self.color_map(header, record.levelname)
            return [header, '%s' % message]
        else:
            return message

class MyStreamHandler(logging.Handler):
    def __init__(self, color=None, level=logging.INFO, short_tb=()):

        logging.Handler.__init__(self, level=level)

        if color is None:
            color = sys.stdout.isatty()

        self.setFormatter(ColorFormatter(color, short_tb=short_tb))

    def emit(self, record):

        if not self.filter(record):
            return

        fmt = self.format(record)

        if record.levelno == logging.INFO:
            stream = sys.stdout
        else:
            stream = sys.stderr

        if isinstance(fmt, (list, tuple)):
            for item in fmt:
                if isinstance(item, color):
                    with item(stream) as text:
                        stream.write(text)
                else:
                    stream.write(item)
                stream.write(' ')
        else:
            stream.write(fmt)

        stream.write('\n')

def main():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    h = MyStreamHandler(True, logging.DEBUG)
    logger.addHandler(h)

    logger.debug("DEBUG")
    logger.info("INFO")
    logger.warn("WARN")
    logger.error("ERROR")

    FormatterWrapper.wrap(h, prefix=color('prefix |', [color.WHITE, color.BACKGROUND_COLORS[0]]))

    logger.debug("DEBUG")
    logger.info("INFO")
    logger.warn("WARN")
    logger.error("ERROR")

if __name__ == '__main__':
    main()
