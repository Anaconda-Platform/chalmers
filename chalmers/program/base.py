"""
Chalmers program object
"""
from __future__ import absolute_import, unicode_literals, print_function

import abc
from glob import glob
import logging
from threading import Lock, Event
from os import path
import os
import signal
from subprocess import Popen, STDOUT
import time

import yaml

from chalmers import errors
from chalmers.config import dirs
from chalmers.event_dispatcher import EventDispatcher, send_action
import sys
import psutil


log = logging.getLogger(__name__)

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
                 'stopsignal', 'startsecs' ])
              ]

    DEFAULTS = {
                'startretries': 3,
                'exitcodes': [0],
                'startsecs': 3,
                'stopwaitsecs': 10,
                'stopsignal': signal.SIGTERM,
                'log_dir': dirs.user_log_dir,

                'redirect_stderr': True,
                'stdout': '{log_dir}/{name}.stdout.log',
                'stderr': '{log_dir}/{name}.stderr.log',
                'daemon_log': '{log_dir}/{name}.daemon.log',
                }

    @abc.abstractproperty
    def is_running(self): pass

    def start_as_service(self):
        """
        Run this program in a new background process
        
        chalmers manager must be running
        """
        from ..program_manager import ProgramManager
        send_action(ProgramManager.NAME, 'start', self.name)

    @property
    def definition_filename(self):
        'The file name where the run defn is stored in'
        return path.join(dirs.user_data_dir, 'programs', '%s.yaml' % self.name)

    @property
    def state_filename(self):
        'The file name where current program state is stored'
        return path.join(dirs.user_data_dir, 'state', '%s.yaml' % self.name)

    @property
    def lock_filename(self):
        'The file name where current program state is stored'
        return path.join(dirs.user_data_dir, 'lock', '%s' % self.name)


    def __init__(self, name, load=True):
        self._name = name

        lock_dir = path.dirname(self.lock_filename)

        if not path.isdir(lock_dir):
            os.makedirs(lock_dir)

        self.file_lock = Lock()

        EventDispatcher.__init__(self)
        self.finished_event = Event()

        self.raw_data = {}
        self.data = {}
        self.state = {}
        self._p0 = None
        if load:
            self.reload()
            self.reload_state()

        self._pipe_output = False

    @property
    def pipe_output(self):
        return self._pipe_output

    @pipe_output.setter
    def pipe_output(self, value):
        self._pipe_output = value

    @property
    def name(self):
        return self._name

    @classmethod
    def create(cls, name, defn, state=None):
        """
        Create a new program object
        """
        prog = cls(name, False)
        prog.raw_data = defn
        prog.state = state or {}
        prog.mk_data()

        return prog

    @property
    def stopsignal(self):
        stopsignal = self.data['stopsignal']

        if isinstance(stopsignal, basestring) and hasattr(signal, stopsignal):
            stopsignal = getattr(signal, stopsignal)
        if not isinstance(stopsignal, int):
            log.warning("Stopsignal %s is not a valid signal for this platform" % stopsignal)
            log.warning("Signal SIGTERM (%s) will be used" % signal.SIGTERM)
        return stopsignal

    def save(self):
        """
        Save the program definition to file
        """
        defn_dir = path.dirname(self.definition_filename)

        if not path.isdir(defn_dir):
            os.makedirs(defn_dir)

        # Force check of stopsignal
        self.stopsignal

        with open(self.definition_filename, 'w') as df:
            yaml.safe_dump(self.raw_data, df, default_flow_style=False)

    def save_state(self):
        """
        Save the program state to file
        """
        state_dir = path.dirname(self.state_filename)

        if not path.isdir(state_dir):
            os.makedirs(state_dir)

        with open(self.state_filename, 'w') as df:
            log.debug("Saving state of program %s to %s" % (self.name, self.state_filename))
            yaml.safe_dump(self.state, df, default_flow_style=False)

    def reload_state(self):
        """
        Replace the state in memory with the state in the state file
        """

        log.debug("Reload state from file %s" % self.state_filename)
        if path.isfile(self.state_filename):
            with open(self.state_filename) as sf:
                self.state = yaml.safe_load(sf)

                if self.state is None:
                    log.debug("Statefile returned none")
        else:
            log.debug("Statefile does not exist")
            self.state = {}

    def reload(self):
        """
        Replace the program definition in memory with the definition 
        from the defn file
        """

        if not path.isfile(self.definition_filename):
            msg = "Program %s does not exist (no definition file %s)"
            raise errors.ProgramNotFound(msg % (self.name, self.definition_filename))

        with open(self.definition_filename) as df:
            self.raw_data = yaml.safe_load(df)

        self.mk_data()

    @classmethod
    def load_template(cls, template_name):
        """
        Load a template from file
        """

        template_path = path.join(dirs.user_data_dir, 'template', '%s.yaml' % template_name)

        if not path.isfile(template_path):
            return {}

        with open(template_path, 'r') as gf:
            return yaml.safe_load(gf)

    def mk_data(self):
        """
        Transform the 'raw_data' from the definition into
        the used data
        """
        self.data = self.DEFAULTS.copy()

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


    def update_definition(self, *E, **F):
        'Update the program definition'
        with self.file_lock:
            self.reload()
            self.raw_data.update(*E, **F)
            self.save()

    def update_state(self, *E, **F):
        'Update the program state'
        with self.file_lock:

            self.reload_state()
            self.state.update(*E, **F)
            log.debug("Update state with info: %r" % dict(*E, **F))
            self.save_state()

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

        self.update_state(pid=os.getpid())

        try:
            self.keep_alive()
        except errors.StopProcess:
            self._terminate()
        finally:
            self.update_state(pid=None, stop_time=time.time())
            self.finished_event.set()
            self._running = False
            if self._listener:
                try:
                    send_action(self.name, 'exitloop')
                except:
                    pass


    def dispatch_terminate(self, timeout=None):
        'Action for event listener'
        self._terminate()
        self._running = False
        if not self.finished_event.wait(timeout):
            raise errors.ChalmersError("Timed out waiting for program %s to finish" % self.name)

    def _terminate(self):
        """
        Terminate this process, 
        This function may only be called by the process that called 'start_sync'
        
         
        """

        stopsignal = self.stopsignal

        log.info('Stop Process Requested')
        self._terminating = True
        if self._p0:
            log.info('Sending signal %s to process %s' % (stopsignal, self._p0.pid))
            kill_tree(self._p0.pid, stopsignal)
        elif self._p0 is None:
            raise errors.ChalmersError("This process did not start this program, can not call _terminate")

    def keep_alive(self):
        """
        """
        self._p0 = False

        if self.pipe_output or self.data['redirect_stderr']:
            stderr = STDOUT
        else:
            stderr = open(self.data['stderr'], 'a+')
            stderr.seek(0, os.SEEK_END)

        if self.pipe_output:
            stdout = None
        else:
            stdout = open(self.data['stdout'], 'a+')
            stdout.seek(0, os.SEEK_END)

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

            log.info("Setting Environment: \n%s" % '\n'.join('\t%s: %r' % item for item in update_env.items()))
            log.info("Setting Working Directory: %s" % cwd)
            log.info("Running Command: %s" % ' '.join(self.data['command']))

            try:
                self._p0 = Popen(self.data['command'],
                                 stdout=stdout, stderr=stderr,
                                 env=env, cwd=cwd, bufsize=self.data.get('bufsize', 0))
            except OSError as err:
                log.exception('Program %s could not be started with popen' % self.name)
                self.update_state(child_pid=None, exit_status=1,
                                  reason='OSError running command "%s"' % self.data['command'][0])
                return
            except:
                log.exception('Exception in keep_alive')
                self.update_state(child_pid=None, exit_status=1,
                                  reason='There was an unknown exception opening command (check logs)')
                return



            log.info('Program started with pid %s' % self._p0.pid)
            self.update_state(child_pid=self._p0.pid, reason=None, exit_status=None,
                              start_time=time.time())

            try:
                status = self._p0.wait()
            except KeyboardInterrupt:
                log.error('Program %s was interrupted by user' % self.name)
                kill_tree(self._p0.pid, signal.SIGTERM)
                self.update_state(child_pid=None, exit_status=None, reason='Interrupted by user')
                raise

            self._p0 = False

            uptime = time.time() - start

            log.info('Command Exited with status %s' % status)
            log.info(' + Uptime %s' % uptime)

            if self._terminating:
                reason = "Terminated at user request"
                status = None
            elif uptime < self.data['startsecs']:
                reason = 'Program did not successfully start'
                startretries -= 1
            elif status in self.data['exitcodes']:
                reason = "Program exited gracefully"
            else:
                reason = "Program exited unexpectedly with code %s" % (status)
                startretries = initial_startretries

            self.update_state(child_pid=None, exit_status=status,
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

        if path.isfile(self.definition_filename):
            os.unlink(self.definition_filename)

        if path.isfile(self.state_filename):
            os.unlink(self.state_filename)


    @classmethod
    def find_for_user(cls):
        'Find all programs this user has defined'
        program_glob = path.join(dirs.user_data_dir, 'programs', '*.yaml')
        for filename in glob(program_glob):
            basename = path.basename(filename)
            name = path.splitext(basename)[0]
            yield cls(name)


    @classmethod
    def start_all(cls, start_paused=False):
        'Start all user defined programs'
        log.info("Starting all programs")

        for prog in cls.find_for_user():
            if not start_paused and prog.is_paused:
                log.info(" - Program %s is paused" % prog.name)
            elif not prog.is_running:
                log.info(" + Starting program %s" % prog.name)
                prog.start(daemon=True)
            else:
                log.info(" - Programs %s is already running" % prog.name)


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
        elif self.is_paused:
            return 'PAUSED'
        elif self.is_ok:
            return 'STOPPED'
        else:
            return 'ERROR'

    def log_to_daemonlog(self):
        print('log_to_daemonlog')
        logger = logging.getLogger('chalmers')
        self._log_stream = open(self.data['daemon_log'], 'a', 1)
        self._log_stream.seek(0, 2)
        hdlr = logging.StreamHandler(self._log_stream)
        hdlr.setLevel(logging.INFO)
        fmt = logging.Formatter("[%(asctime)s] %(levelname)s:%(message)s")
        hdlr.setFormatter(fmt)
        logger.setLevel(logging.INFO)
        logger.addHandler(hdlr)



    def stop(self):
        """
        Stop this program
        """

        if not self.is_running:
            raise errors.StateError("Program is not running")

        send_action(self.name, 'terminate', timeout=self.data['stopwaitsecs'])


    def restart(self):
        if self.is_running:
            print("Stopping program %s ..." % self.name, end=''); sys.stdout.flush()
            try:
                self.stop()
            except errors.StateError as err:
                log.error(err.message)
            else:
                print("stopped ")
        else:
            print("Program %s is already stopped" % self.name)

        print("Starting program %s ... " % self.name, end=''); sys.stdout.flush()
        self.reload_state()
        self.start()
        print("restarted")

    def wait_for_start(self):
        self.reload_state()
        startsecs = self.data['startsecs']
        st = time.time()

        while time.time() - self.state.get('start_time', st) < startsecs:
            time.sleep(1)
            self.reload_state()

        return not self.is_ok



def kill_tree(pid, sig):
    'Kill all processes and child processes'
    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        log.warn("Kill failed, process with pid %s does not appear to be running" % pid)
        return
    children = parent.get_children(recursive=True)
    os.kill(pid, sig)

    for child in children:
        if child.is_running():
            child.kill()
