from __future__ import print_function, absolute_import, unicode_literals
import yaml
import os
from contextlib import contextmanager
from chalmers import errors

class PersistentDict(dict):
    """
    A class that persists a dict to a file  
    """
    def __init__(self, filename, load=True):
        self._filename = os.path.abspath(filename)
        if load: self._load()
        self._transact = False

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


    def _mk_lockfile(self):
        lockfile = self._filename + '.lock'
        try:
            if self.exists():
                os.link(self._filename, lockfile)
            else:
                os.mkdir(lockfile)
        except OSError as err:
            if err.errno == 17:
                msg = ("The file '%s' is locked by another process.\n"
                       "If this process is not running, "
                       "you can manually remove the lockfile\n\trm '%s'" % (self._filename, lockfile))
                raise errors.ChalmersError(msg)
            raise

    def _rm_lockfile(self):
        lockfile = self._filename + '.lock'
        if os.path.isdir(lockfile):
            os.rmdir(lockfile)
        elif os.path.isfile(lockfile):
            os.unlink(lockfile)

    @contextmanager
    def file_lock(self):

        transact = self._transact
        self._transact = True

        if not transact:
            self._mk_lockfile()

        try:
            yield transact
        finally:
            if not transact:
                self._rm_lockfile()

        self._transact = transact

    @contextmanager
    def transaction(self):
        # TODO: lock the file while the transation is going on
        # with self.file_lock() as transact:

        # Tell dict that a transation is going on
        transact = self._transact
        self._transact = True

        # don't load if already in a transation state
        if not transact:
            self._load()

        yield

        # don't store if already in a transation state
        # this means that the transaction context can be nested
        if not transact:
            self._store()

        # Restore previous state
        self._transact = transact


    #===============================================================================
    # Overload std dict setter methods
    #===============================================================================

    def __setitem__(self, *args, **kwargs):
        with self.transaction():
            return dict.__setitem__(self, *args, **kwargs)

    def update(self, *args, **kwargs):
        with self.transaction():
            return dict.update(self, *args, **kwargs)

    def setdefault(self, *args, **kwargs):
        with self.transaction():
            return dict.setdefault(self, *args, **kwargs)

    def pop(self, *args, **kwargs):
        with self.transaction():
            return dict.pop(self, *args, **kwargs)

    def popitem(self, *args, **kwargs):
        with self.transaction():
            return dict.popitem(self, *args, **kwargs)

    def clear(self):
        with self.transaction():
            return dict.clar(self)
