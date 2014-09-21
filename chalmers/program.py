"""
Chalmers program object
"""
from __future__ import absolute_import, unicode_literals, print_function

from glob import glob
import logging
from os import path
import os
import signal
from subprocess import Popen, STDOUT
import time

import yaml

from chalmers import errors
from chalmers.config import dirs
from chalmers.utils.daemonize import daemonize

log = logging.getLogger(__name__)

'/Users/sean/Documents/workspace/chalmers'

def stop_process(signum, frame):
    """
    Signal handler to raise StopProcess exception
    """
    log.debug("Process recieved signal %s" % signum)
    raise errors.StopProcess()


def str_replace(data):
    """
    String substitution of `data` dict
    """
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = value % data

class Program(object):
    """
    Object that represents a long running process
    
    This program option may represent a program that is 
    running in another process
    or a program that is running in the current process.
    """

    OPTIONS = [('Primary Options',
                ['name', 'command', 'groups']),
               ('Output',
                ['stdout', 'stderr', 'daemon_log', 'redirect_stderr']),
               ('Process Controll',
                ['retries', 'exitcodes', 'stopwaitsecs',
                 'stopsignal', 'startsecs' ])
              ]

    DEFAULTS = {
                'retries': 3,
                'exitcodes': [0],
                'startsecs': 10,
                'stopwaitsecs': 10,
                'stopsignal': signal.SIGTERM,
                'log_dir': dirs.user_log_dir,

                'redirect_stderr': False,
                'stdout': '%(log_dir)s/%(name)s.stdout.log',
                'stderr': '%(log_dir)s/%(name)s.stderr.log',
                'daemon_log': '%(log_dir)s/%(name)s.daemon.log',
                }

    @property
    def definition_filename(self):
        'The file name where the run defn is stored in'
        return path.join(dirs.user_data_dir, 'programs', '%s.yaml' % self.name)

    @property
    def state_filename(self):
        'The file name where current program state is stored'
        return path.join(dirs.user_data_dir, 'state', '%s.yaml' % self.name)


    def __init__(self, name, load=True):
        self.name = name

        self.raw_data = {}
        self.data = {}
        self.state = {}
        self._p0 = None
        if load:
            self.reload()
            self.reload_state()


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


    def save(self):
        """
        Save the program definition to file
        """
        defn_dir = path.dirname(self.definition_filename)

        if not path.isdir(defn_dir):
            os.makedirs(defn_dir)

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

        if path.isfile(self.state_filename):
            with open(self.state_filename) as sf:
                self.state = yaml.safe_load(sf)
        else:
            self.state = {}

    def reload(self):
        """
        Replace the program definition in memory with the definition 
        from the defn file
        """

        if not path.isfile(self.definition_filename):
            raise errors.ProgramNotFound("Program %s does not exist (no definition file)" % self.name)

        with open(self.definition_filename) as df:
            self.raw_data = yaml.safe_load(df)

        self.mk_data()

    @classmethod
    def load_template(cls, groupname):
        """
        Load a template from file
        """

        group_path = path.join(dirs.user_data_dir, 'template', '%s.yaml' % groupname)

        if not path.isfile(group_path):
            return {}

        with open(group_path, 'r') as gf:
            return yaml.safe_load(gf)

    def mk_data(self):
        """
        Transform the 'raw_data' from the definition into
        the used data
        """
        self.data = self.DEFAULTS.copy()
        for template in self.raw_data.get('extends', []):
            group_data = self.load_template(template)
            self.data.update(group_data)

        self.data.update(self.raw_data)

        str_replace(self.data)

        if self.data.get('redirect_stderr'):
            self.data.pop('stderr')

    def stop(self):
        """
        Stop this program
        
        Sends SIGUSR2 signal to the program's PID
        """

        if not self.is_running:
            raise errors.StateError("Program is not running")
        pid = self.state.get('pid')
        os.kill(pid, signal.SIGUSR2)

        # TODO: not sure how to wait for the PID
        while self.is_running:
            time.sleep(.1)

        self.update_state(pid=None, paused=True)

    @property
    def is_paused(self):
        return self.state.get('paused')

    @property
    def is_running(self):
        "Check For the existence of a pid"
        pid = self.state.get('pid')
        if not pid:
            return False
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    def update_definition(self, *E, **F):
        'Update the program definition'
        self.reload()
        self.raw_data.update(*E, **F)
        self.save()

    def update_state(self, *E, **F):
        'Update the program state'
        self.reload_state()
        self.state.update(*E, **F)
        self.save_state()


    def start(self, daemon=True):
        """
        Start this process 
        :param daemon: if true, start the process as a background process
        
        this will fail if the process is already running
        """
        if self.is_running:
            raise errors.StateError("Process is already running")

        if daemon:
            start = self.start_deamon
        else:
            start = self.start_sync
        start()

    def start_sync(self):
        """
        Syncronously run this program in this process
        """
        signal.signal(signal.SIGUSR2, stop_process)
        signal.signal(signal.SIGALRM, stop_process)

        self.update_state(pid=os.getpid(), paused=False)

        try:
            self.keep_alive()
        except errors.StopProcess:
            self._terminate()

        self.update_state(pid=os.getpid())


    def start_deamon(self):
        """
        Run this program in a new background process
        """

        if 'daemon_log' in self.data:
            hdlr = logging.FileHandler(self.data['daemon_log'])
            fmt = logging.Formatter(logging.BASIC_FORMAT)
            hdlr.setFormatter(fmt)
            logging.getLogger('chalmers').addHandler(hdlr)

        daemonize(self.start_sync)

    def _terminate(self):
        """
        Terminate this process, 
        This function may only be called by the process that called 'start_sync'
        
         
        """
        log.info('Stop Process Requested')
        if self._p0:
            log.info('Sending signal %s to process %s' % (self.data['stopsignal'], self._p0.pid))
            self._p0.send_signal(self.data['stopsignal'])
            if self.data['stopwaitsecs']:
                signal.alarm(self.data['stopwaitsecs'])

            try:
                status = self._p0.wait()
                log.info('Command Exited with status %s' % status)
                status_message = 'Stopped: At user request'
            except errors.StopProcess:
                log.info('Process %s did not exit within %s seconds sending SIGKILL' % (self._p0.pid, self.data['stopwaitsecs']))
                self._p0.send_signal(signal.SIGKILL)
                status = '?'
                status_message = 'Stopped: Terminate timed out: sent SIGKILL'

            self.update_state(exit_status=status, status_message=status_message, paused=True, pid=None, child_pid=None)
        elif self._p0 is None:
            raise errors.ChalmersError("This process did not start this program, can not call _terminate")

    def keep_alive(self):
        """
        """
        self._p0 = False

        if self.data['redirect_stderr']:
            stderr = STDOUT
        else:
            stderr = open(self.data['stderr'], 'a')

        stdout = open(self.data['stdout'], 'a')

        for i in range(self.data['retries'] + 1):
            start = time.time()
            if i:
                log.info('Retry command (%i of %i)' % (i, self.data['retries']))
            env = os.environ.copy()
            env.update(self.data.get('env', {}))
            log.info("Running Command: %s" % ' '.join(self.data['command']))
            self._p0 = Popen(self.data['command'], stdout=stdout, stderr=stderr, env=env)

            log.info('Program started with pid %s' % self._p0.pid)
            self.update_state(child_pid=self._p0.pid, status_message='running', exit_status=None)
            status = self._p0.wait()

            self._p0 = False

            uptime = time.time() - start

            log.info('Command Exited with status %s' % status)
            log.info(' + Uptime %s' % uptime)

            if uptime < self.data['startsecs']:
                status_message = 'Error: Program could not successfully start'
            elif status in self.data['exitcodes']:
                status_message = "Stopped: Program exited gracefully"

            self.update_state(child_pid=None, exit_status=status,
                              status_message=status_message)

            if status in self.data['exitcodes']:
                break

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
    def find_groups_for_user(cls):
        """
        Groups
        """
        program_glob = path.join(dirs.user_data_dir, 'groups', '*.yaml')
        for filename in glob(program_glob):
            with open(filename) as gf:
                yield yaml.safe_load(gf)

    @classmethod
    def find_for_user(cls):
        'Find all programs this user has defined'
        program_glob = path.join(dirs.user_data_dir, 'programs', '*.yaml')
        for filename in glob(program_glob):
            basename = path.basename(filename)
            name = path.splitext(basename)[0]
            yield cls(name)


    @classmethod
    def start_all(cls):
        log.info("Starting all programs")

        for prog in cls.find_for_user():
            if prog.is_paused:
                log.info(" - Program %s is paused" % prog.name)
            elif not prog.is_running:
                log.info(" + Starting program %s" % prog.name)
                prog.start(daemon=True)
            else:
                log.info(" - Programs %s is already running" % prog.name)


    @property
    def text_status(self):
        'A text status of the current program'
        exit_message = self.data.get('exit_message', 'Stopped')
        text_status = 'Running' if self.is_running else exit_message
        return text_status




