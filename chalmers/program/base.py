"""
Chalmers program object
"""
from __future__ import absolute_import, unicode_literals, print_function

import abc
from contextlib import contextmanager
from glob import glob
import logging
from os import path
import os
import signal
from subprocess import Popen, STDOUT
import sys
from threading import Event
import time

import psutil
import yaml

from chalmers import config
from chalmers import errors
from chalmers.event_dispatcher import EventDispatcher, send_action
from chalmers.utils.file_echo import FileEcho
from chalmers.utils.kill_tree import kill_tree
from chalmers.utils.persistent_dict import PersistentDict


log = logging.getLogger(__name__)

# Python 3
try:
    unicode
except NameError:
    unicode = str

try:
    basestring
except NameError:
    basestring = str


def safe_makedir(filepath):
    dirname = os.path.dirname(filepath)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

def str_replace(data):
    """
    String substitution of `data` dict
    """
    for key, value in data.items():
        if isinstance(value, (str, unicode)):
            data[key] = value.format(**data)

class ProgramBase(EventDispatcher):
    """
    Object that represents a long running process
    
    This program option may represent a program that is 
    running in another process
    or a program that is running in the current process.
    """
    __metaclass__ = abc.ABCMeta


    OPTIONS = [('Primary Options',
                ['name', 'command', 'templates']),
               ('Output',
                ['stdout', 'stderr', 'daemon_log', 'redirect_stderr']),
               ('Process Controll',
                ['retries', 'exitcodes', 'stopwaitsecs',
                 'stopsignal', 'startsecs', 'cwd' ])
              ]
    @property
    def default_data(self):
        return {
                'startretries': 3,
                'exitcodes': [0],
                'startsecs': 3,
                'stopwaitsecs': 10,
                'stopsignal': signal.SIGTERM,
                'log_dir': config.dirs.user_log_dir,

                'redirect_stderr': True,
                'stdout': '{log_dir}/{name}.stdout.log',
                'stderr': '{log_dir}/{name}.stderr.log',
                'daemon_log': '{log_dir}/{name}.daemon.log',
                }

    #===============================================================================
    # Abstract Properties
    #===============================================================================

    @abc.abstractproperty
    def is_running(self): pass

    @abc.abstractmethod
    def _send_signal(self, pid, signal):
        pass

    @abc.abstractmethod
    def start_as_service(self):
        """
        Run this program in a new background process
        
        chalmers manager must be running
        """
        pass

    def handle_signals(self):
        '''
        Can optionally override to handle signals
        '''
        pass

    preexec_fn = None

    def __init__(self, name, load=True, force=False):
        self._name = name

        EventDispatcher.__init__(self)
        self.finished_event = Event()

        defn_filename = path.join(config.dirs.user_data_dir, 'programs', '%s.yaml' % self.name)
        state_filename = path.join(config.dirs.user_data_dir, 'state', '%s.yaml' % self.name)

        try:
            self.state = PersistentDict(state_filename)
        except yaml.error.YAMLError:
            log.error("Yaml parser error. could not parse state file %s" % state_filename)
            if force:
                log.warn("Removing state file and continuing")
                os.unlink(state_filename)
                self.state = PersistentDict(state_filename)
            else:
                msg = "Invalid state file. run `chalmers stop --force` to clear the state file"
                raise errors.ChalmersError(msg)

        try:
            self.raw_data = PersistentDict(defn_filename)
        except yaml.error.YAMLError:
            log.error("Yaml parser error. could not parse definition file %s" % defn_filename)
            if force:
                self.raw_data = PersistentDict(defn_filename, load=False)
            else:
                msg = "Invalid definition file. Run `chalmers edit %s` to fix the definition file"
                raise errors.ChalmersError(msg % (defn_filename))


        self.data = {}
        self.mk_data()

        self._p0 = None
        self.pipe_output = False

    def exists(self):
        return self.raw_data.exists()

    @property
    def name(self):
        return self._name

    @property
    def stopsignal(self):
        stopsignal = self.data['stopsignal']

        if isinstance(stopsignal, basestring) and hasattr(signal, stopsignal):
            stopsignal = getattr(signal, stopsignal)
        if not isinstance(stopsignal, int):
            log.warning("Stopsignal %s is not a valid signal for this platform" % stopsignal)
            log.warning("Signal SIGTERM (%s) will be used" % signal.SIGTERM)
            return signal.SIGTERM
        return stopsignal

    @classmethod
    def load_template(cls, template_name):
        """
        Load a template from file
        """

        template_path = path.join(config.dirs.user_data_dir, 'template', '%s.yaml' % template_name)

        if not path.isfile(template_path):
            return {}

        with open(template_path, 'r') as gf:
            return yaml.safe_load(gf)

    def mk_data(self):
        """
        Transform the 'raw_data' from the definition into
        the used data
        """
        self.data = self.default_data.copy()

        raw_data = self.raw_data or {}

        if 'name' not in raw_data:
            raw_data['name'] = self.name

        for template in raw_data.get('extends', []):
            template_data = self.load_template(template)
            self.data.update(template_data)

        self.data.update(raw_data)

        str_replace(self.data)

        if self.data.get('redirect_stderr'):
            self.data.pop('stderr')

    @property
    def is_paused(self):
        return self.state.get('paused')

    def start(self, daemon=True):
        """
        Start this process 
        :param daemon: if true, start the process as a background process
        
        this will fail if the process is already running
        """
        if self.is_running:
            raise errors.StateError("Process is already running")

        if not daemon:
            self.start_sync()
        else:
            self.start_as_service()

    def start_sync(self):
        """
        Syncronously run this program in this process
        """

        if 'daemon_log' in self.data:
            self.log_to_daemonlog()

        self.start_listener()

        self.state.update(pid=os.getpid())

        try:
            self.keep_alive()
        except errors.StopProcess:
            self._stop()
        finally:
            self.state.update(pid=None, stop_time=time.time())
            self.finished_event.set()
            self._running = False
            if self._listener:
                try:
                    send_action(self.name, 'exitloop')
                except:
                    pass
            if 'daemon_log' in self.data:
                self.stop_daemonlog()


    def dispatch_terminate(self, timeout=None):
        'Action for event listener'
        children = self._stop()
        if not self.finished_event.wait(timeout):
            if self._p0:
                log.info('Process did not stop within %s seconds' % (timeout))
                log.info('Hard killing process %s' % (self._p0.pid))
                kill_tree(self._p0.pid)

            if not self.finished_event.wait(timeout):
                raise errors.ChalmersError("Timed out waiting for program %s to finish" % self.name)
        else:
            for child in children:
                if child.is_running():
                    child.kill()

    def _stop(self):
        """
        Terminate this process, 
        This function may only be called by the process that called 'start_sync'
        
         
        """
        self._running = False
        self._terminating = True

        if not self._p0:
            log.info("_p0 is none")

        try:
            parent = psutil.Process(self._p0.pid)
        except psutil.NoSuchProcess:
            log.info("psutil.NoSuchProcess %s" % self._p0.pid)
            return

        children = parent.get_children(recursive=True)

        log.info('Sending signal %s to process %s' % (self.stopsignal, self._p0.pid))
        self._send_signal(self._p0.pid, self.stopsignal)

        return children


    @contextmanager
    def setup_output(self):
        if self.pipe_output:
            self.data['redirect_stderr'] = True
        if self.data['redirect_stderr']:
            stderr = STDOUT
        elif self.data.get('stderr'):
            safe_makedir(self.data['stderr'])
            stderr = open(self.data['stderr'], 'a+', 1)
            stderr.seek(0, os.SEEK_END)
        else:
            stderr = None

        if self.data.get('stdout'):
            safe_makedir(self.data['stdout'])
            stdout = open(self.data['stdout'], 'a+', 1)
            stdout.seek(0, os.SEEK_END)
        else:
            stdout = None

        if self.pipe_output:  # TODO: this may no longer be useful
            self._echo = FileEcho(self.data['stdout'], sys.stdout)
            self._echo.start()
        else:
            self._echo = None

        try:
            yield stdout, stderr
        finally:
            if self._echo:
                self._echo.stop()

            if hasattr(stdout, 'close'):
                stdout.close()

            if hasattr(stderr, 'close'):
                stdout.close()

    def keep_alive(self):
        """
        """
        self._p0 = False

        self.handle_signals()

        with self.setup_output() as (stdout, stderr):

            self._terminating = False
            startretries = self.data.get('startretries', 3)
            initial_startretries = self.data.get('startretries', 3)

            while startretries:
                start = time.time()
                if startretries != initial_startretries:
                    log.info('Retry command (%i retries remain)' % startretries)
                env = os.environ.copy()
                update_env = {k:str(v) for (k, v) in self.data.get('env', {}).items()}
                env.update(update_env)
                cwd = self.data.get('cwd') or os.path.abspath(os.curdir)

                env_str = '\n'.join('\t%s: %r' % item for item in update_env.items())

                if env_str:
                    log.info("Setting Environment: \n%s" % env_str)

                if cwd:
                    log.info("Setting Working Directory: %s" % cwd)

                log.info("Running Command: %s" % ' '.join(self.data['command']))
                try:
                    self._p0 = Popen(self.data['command'],
                                     stdout=stdout, stderr=stderr,
                                     env=env, cwd=cwd, bufsize=self.data.get('bufsize', 0),
                                     preexec_fn=self.preexec_fn)
                except OSError as err:
                    log.exception('Program %s could not be started with popen' % self.name)
                    self.state.update(child_pid=None, exit_status=1,
                                      reason='OSError running command "%s"' % self.data['command'][0])
                    return
                except:
                    log.exception('Exception in keep_alive')
                    self.steate.update(child_pid=None, exit_status=1,
                                      reason='There was an unknown exception opening command (check logs)')
                    return

                log.info('Program started with pid %s' % self._p0.pid)
                self.state.update(child_pid=self._p0.pid, reason=None, exit_status=None,
                                  start_time=time.time())

                try:
                    status = self._p0.wait()
                except KeyboardInterrupt:
                    log.error('Program %s was interrupted by user' % self.name)
                    kill_tree(self._p0.pid)
                    self.state.update(child_pid=None, exit_status=None, reason='Interrupted by user')
                    raise
                except BaseException as err:
                    log.error('Program %s was interrupted' % self.name)
                    kill_tree(self._p0.pid)
                    self.state.update(child_pid=None, exit_status=None, reason='Python BaseException')
                    log.exception(err)
                    raise

                self._p0 = False

                uptime = time.time() - start

                log.info('Command Exited with status %s' % status)
                log.info(' + Uptime %s' % uptime)

                if self._terminating:
                    reason = "Terminated at user request"
                    status = None
                elif status in self.data['exitcodes']:
                    reason = "Program exited gracefully"
                elif uptime < self.data['startsecs']:
                    reason = 'Program did not successfully start'
                    startretries -= 1
                else:
                    reason = "Program exited unexpectedly with code %s" % (status)
                    startretries = initial_startretries

                self.state.update(child_pid=None, exit_status=status,
                                  reason=reason)

                if self._terminating:
                    break
                if status in self.data['exitcodes']:
                    break

        log.debug("Exiting keep alive function")

    def delete(self):
        """
        Remove this program definition
        """
        if self.is_running:
            raise errors.ChalmersError("Can not remove running program (must be stopped)")

        self.state.delete()
        self.raw_data.delete()

    @property
    def is_ok(self):
        if self.is_running:
            return True
        elif self.state.get('exit_status') is None:
            return True
        elif self.state.get('exit_status') in self.data['exitcodes']:
            return True
        return False


    @property
    def text_status(self):
        'A text status of the current program'

        if self.is_running:
            return 'RUNNING'
        elif self.is_ok:
            if self.is_paused:
                return 'OFF'
            else:
                return 'STOPPED'
        else:
            return 'ERROR'

    def log_to_daemonlog(self):
        logger = logging.getLogger('chalmers')
        safe_makedir(self.data['daemon_log'])
        self._log_stream = open(self.data['daemon_log'], 'a', 1)
        self._log_stream.seek(0, 2)
        self._daemonlog_hdlr = hdlr = logging.StreamHandler(self._log_stream)
        hdlr.setLevel(logging.INFO)
        fmt = logging.Formatter("[%(asctime)s] %(levelname)s:%(message)s")
        hdlr.setFormatter(fmt)
        logger.setLevel(logging.INFO)
        logger.addHandler(hdlr)

    def stop_daemonlog(self):

        logger = logging.getLogger('chalmers')
        logger.removeHandler(self._daemonlog_hdlr)
        try:
            self._log_stream.close()
        except IOError:
            # Ignore:
            # close() called during concurrent operation on the same file object.
            pass



    def stop(self, force=False):
        """
        Stop this program
        """

        if not self.is_running:
            raise errors.StateError("Program is not running")

        if force:
            if self.state.get('pid'):
                log.debug("Force killing chalmers monitor process pid=%s" % self.state.get('pid'))
                try:
                    kill_tree(self.state.get('pid'))
                except psutil.NoSuchProcess:
                    pass
            if self.state.get('child_pid'):
                log.debug("Force killing chalmers child process pid=%s" % self.state.get('child_pid'))
                try:
                    kill_tree(self.state.get('child_pid'))
                except psutil.NoSuchProcess:
                    pass
        else:
            send_action(self.name, 'terminate', timeout=self.data['stopwaitsecs'])


    def wait_for_start(self):
        """
        Wait for program to start, 
        returns True if the program started successfully
        """
        time.sleep(.5)
        self.state.reload()
        startsecs = self.data['startsecs']
        st = time.time()
        while time.time() - self.state.get('start_time', st) < startsecs:
            time.sleep(1)
            self.state.reload()

        return not self.is_ok

    #===============================================================================
    # Class methods
    #===============================================================================

    @classmethod
    def create(cls, name, defn, state=None):
        """
        Create a new program object
        """
        prog = cls(name, False)
        prog.raw_data.update(defn)
        prog.state.update(state or {})
        prog.mk_data()

        return prog

    @classmethod
    def find_for_user(cls, force=False):
        'Find all programs this user has defined'
        program_glob = path.join(config.dirs.user_data_dir, 'programs', '*.yaml')
        for filename in glob(program_glob):
            basename = path.basename(filename)
            name = path.splitext(basename)[0]
            yield cls(name, force=force)


