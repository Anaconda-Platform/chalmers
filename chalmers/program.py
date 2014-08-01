'''
Created on Jun 23, 2014

@author: sean
'''
from chalmers import errors
from chalmers.config import dirs
from chalmers.utils.daemonize import daemonize
from glob import glob
from os import path
from subprocess import Popen, STDOUT
import logging
import multiprocessing
import os
import signal
import time
import yaml
log = logging.getLogger(__name__)


def stop_process(signum, frame):
    log.debug("Process recieved signal %s" % signum)
    raise errors.StopProcess()


def str_replace(data):
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = value % data



class Program(object):
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
        return path.join(dirs.user_data_dir, 'programs', '%s.yaml' % self.name)

    @property
    def state_filename(self):
        return path.join(dirs.user_data_dir, 'state', '%s.yaml' % self.name)


    def __init__(self, name, load=True):
        self.name = name

        self.raw_data = {}
        self.data = {}
        self.state = {}

        if load:
            self.reload()

    @classmethod
    def create(cls, name, defn, state=None):
        prog = cls(name, False)
        prog.raw_data = defn
        prog.state = state or {}
        prog.mk_data()

#         prog.save()
#         prog.save_state()

        return prog


    def save(self):
        defn_dir = path.dirname(self.definition_filename)

        if not path.isdir(defn_dir):
            os.makedirs(defn_dir)

        with open(self.definition_filename, 'w') as df:
            yaml.safe_dump(self.raw_data, df, default_flow_style=False)

    def save_state(self):
        state_dir = path.dirname(self.state_filename)

        if not path.isdir(state_dir):
            os.makedirs(state_dir)

        with open(self.state_filename, 'w') as df:
            yaml.safe_dump(self.state, df, default_flow_style=False)

    def reload(self):

        if not path.isfile(self.definition_filename):
            raise errors.ChalmersError("Program %s does not exist" % self.name)
        if path.isfile(self.state_filename):
            with open(self.state_filename) as sf:
                self.state = yaml.safe_load(sf)
        else:
            self.state = {}

        with open(self.definition_filename) as df:
            self.raw_data = yaml.safe_load(df)

        self.mk_data()

    @classmethod
    def load_group(cls, groupname):
        group_path = path.join(dirs.user_data_dir, 'groups', '%s.yaml' % groupname)
        if not path.isfile(group_path):
            return {}

        with open(group_path, 'r') as gf:
            return yaml.safe_load(gf)

    def mk_data(self):
        self.data = self.DEFAULTS.copy()
        for group in self.raw_data.get('groups', []):
            group_data = self.load_group(group)
            self.data.update(group_data)

        self.data.update(self.raw_data)

        str_replace(self.data)

        if self.data.get('redirect_stderr'):
            self.data.pop('stderr')

    def stop(self):
        if not self.is_running:
            raise errors.ChalmersError("Program is not running")
        pid = self.state.get('pid')
        os.kill(pid, signal.SIGUSR2)

        # TODO: not sure how to wait for the PID
        while self.is_running:
            time.sleep(.1)

    @property
    def is_running(self):
        """ Check For the existence of a unix pid. """
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
        self.reload()
        self.raw_data.update(*E, **F)
        self.save()

    def update_state(self, *E, **F):
        self.reload()
        self.state.update(*E, **F)
        self.save_state()

    def start(self):

        signal.signal(signal.SIGUSR2, stop_process)
        signal.signal(signal.SIGALRM, stop_process)

        self.update_state(pid=os.getpid(), paused=False)

        try:
            self.keep_alive()
        except errors.StopProcess:
            self._terminate()

        self.update_state(pid=os.getpid())


    def start_async(self, daemon=True):
        if self.is_running:
            raise errors.ChalmersError("Process is already running")

        if daemon:
            target = self._start_deamon
        else:
            target = self.start
        p = multiprocessing.Process(target=target, args=())
        p.start()
        p.join()

    def _start_deamon(self):

        if 'daemon_log' in self.data:
            hdlr = logging.FileHandler(self.data['daemon_log'])
            fmt = logging.Formatter(logging.BASIC_FORMAT)
            hdlr.setFormatter(fmt)
            logging.getLogger('chalmers').addHandler(hdlr)

        daemonize()

        self.start()

    def _terminate(self):
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

    def keep_alive(self):

        self._p0 = None

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
            self._p0 = Popen(self.data['command'], stdout=stdout, stderr=stderr, env=env)

            log.info('Program started with pid %s' % self._p0.pid)
            self.update_state(child_pid=self._p0.pid, status_message='running', exit_status=None)
            status = self._p0.wait()

            self._p0 = None

            uptime = time.time() - start

            log.info('Command Exited with status %s' % status)
            log.info(' + Uptime %s' % uptime)

            if uptime < self.data['startsecs']:
                status_message = 'Error: Program could not successfully start'
            elif status in self.data['exitcodes']:
                status_message = "Stopped: Program exited gracefully"

            self.update_state(child_pid=None, exit_status=status,
                              status_message=status_message)

    def delete(self):
        if self.is_running:
            raise errors.ChalmersError("Can not remove running program (must be stopped)")

        if path.isfile(self.definition_filename):
            os.unlink(self.definition_filename)

        if path.isfile(self.state_filename):
            os.unlink(self.state_filename)


    @classmethod
    def find_groups_for_user(cls):
        program_glob = path.join(dirs.user_data_dir, 'groups', '*.yaml')
        for filename in glob(program_glob):
            with open(filename) as gf:
                yield yaml.safe_load(gf)

    @classmethod
    def find_for_user(cls):
        program_glob = path.join(dirs.user_data_dir, 'programs', '*.yaml')
        for filename in glob(program_glob):
            basename = path.basename(filename)
            name = path.splitext(basename)[0]
            yield cls(name)



