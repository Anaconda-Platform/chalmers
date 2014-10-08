
try:
    from _version import __version__
except ImportError:
    __version__ = '0.3'

import signal

defaults = {
            'retries': 3,
            'exitcodes': [0],
            'startsecs': 10,
            'stopwaitsecs': 10,
            'stopsignal': signal.SIGTERM,
            }

def make_program_data(data):
    new_data = defaults.copy()
    new_data.update(data)
    return new_data
