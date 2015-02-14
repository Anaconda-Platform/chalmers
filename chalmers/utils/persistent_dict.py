import yaml
import os
from contextlib import contextmanager

class PersistentDict(dict):
    """
    A class that persists a dict to a file  
    """
    def __init__(self, filename):
        self._filename = os.path.abspath(filename)
        self._load()

    @property
    def filename(self):
        return self._filename

    def exists(self):
        return os.path.exists(self._filename)

    def reload(self):
        self._load()
        self._store()

    def delete(self):
        if os.path.isfile(self._filename):
            os.unlink(self._filename)

    def _load(self):
        if os.path.isfile(self._filename):
            with open(self._filename) as fd:
                dict.clear(self)
                data = yaml.safe_load(fd)
                if data:
                    dict.update(self, data)

    def _store(self):
        dir = os.path.dirname(self._filename)
        if dir and not os.path.isdir(dir):
            os.makedirs(dir)

        with open(self._filename, 'w') as fd:
            yaml.safe_dump(dict(self), fd)

    @contextmanager
    def _transact(self):
        self._load()
        yield
        self._store()

    #===============================================================================
    # Overload std dict setter methods
    #===============================================================================

    def __setitem__(self, *args, **kwargs):
        with self._transact():
            return dict.__setitem__(self, *args, **kwargs)

    def update(self, *args, **kwargs):
        with self._transact():
            return dict.update(self, *args, **kwargs)

    def setdefault(self, *args, **kwargs):
        with self._transact():
            return dict.setdefault(self, *args, **kwargs)

    def pop(self, *args, **kwargs):
        with self._transact():
            return dict.pop(self, *args, **kwargs)

    def popitem(self, *args, **kwargs):
        with self._transact():
            return dict.popitem(self, *args, **kwargs)

    def clear(self):
        with self._transact():
            return dict.clar(self)
