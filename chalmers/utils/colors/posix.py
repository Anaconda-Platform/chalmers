from contextlib import contextmanager


class PosixColor(object):
    WHITE = 97
    YELLO = 93
    BLUE = 94
    GREEN = 92
    RED = 91
    BOLD = 1

    DEFAULT = 0

    BACKGROUND_COLORS = range(40, 48) + [100, 102, 104, 105, 106]

    def __init__(self, text, colors):
        self.text = text
        self.colors = colors

    @contextmanager
    def __call__(self, stream):
        for c in self.colors:
            stream.write('\033[%im' % c)
        try:
            yield self.text
        finally:
            stream.write('\033[%im' % self.DEFAULT)

