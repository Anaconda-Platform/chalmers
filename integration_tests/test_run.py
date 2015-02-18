import io
import logging
import os
import shutil
from subprocess import Popen, check_output, PIPE, CalledProcessError
import sys
import unittest

import mock
import yaml

from chalmers import config, errors
from chalmers.scripts import chalmers_main
import time

class ChalmersCli(object):
    def __init__(self):
        self.script = chalmers_main.__file__
        if self.script.endswith('.pyc') or self.script.endswith('.pyo'):
            self.script = self.script[:-1]
        self.env = os.environ.copy()
        self.root = 'test_config'
        self.env['CHALMERS_ROOT'] = self.root


    def __getattr__(self, subcommand):

        def run_subcommand(*args, **kwargs):
            cmd = [sys.executable, self.script, '-q', '--no-color', subcommand]
            cmd.extend(args)

            return check_output(cmd, env=self.env)
            
        return run_subcommand



def script_path(name):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'scripts', name))

class Test(unittest.TestCase):

    def setUp(self):
        self.cli = ChalmersCli()

        if os.path.isdir(self.cli.root):
            shutil.rmtree(self.cli.root)

        unittest.TestCase.setUp(self)

    def test_simple(self):
        print 'Add echo'
        self.cli.add('echo', 'hi')
        print 'Start'
        self.cli.start('echo', wait=False)
        time.sleep(1)
        print 'Log'
        self.cli.log('echo', '-f')
        print 'Done'

    def test_long_running_process(self):
        print 'Add Long running process'
        script = script_path('long_running_process.py')
        print self.cli.add('-n', 'lrp', sys.executable, script)
        print 'Start'
        print self.cli.start('lrp')
        print 'list'
        out = self.cli.list()
        print out
        self.assertIn('RUNNING', out)

        print self.cli.stop('lrp')
        print 'log'
        out = self.cli.log('lrp')
        print out
        self.assertIn('This is LRP', out)

        out = self.cli.list()
        print out
        self.assertIn('PAUSED', out)

        print 'Done'


    def test_sigint(self):
        print 'Add Long running process'
        script = script_path('long_running_process.py')
        print self.cli.add('-n', 'lrp', sys.executable, script)
        print self.cli.set('lrp', 'stopsignal=SIGINT')
        print '>start'
        print self.cli.start('lrp')
        print '>list'
        out = self.cli.list()
        print out
        self.assertIn('RUNNING', out)
        print '>stop'
        print self.cli.stop('lrp')
        print '>log'
        out = self.cli.log('lrp')
        print out
        self.assertIn('This is LRP', out)
        print '>list'
        out = self.cli.list()
        print out
        self.assertIn('PAUSED', out)

        print '>done'

    def test_spinning_process(self):
        'Add Long Spinning process'
        script = script_path('spinning_process.py')
        print self.cli.add('-n', 'spinner', sys.executable, script)
        print 'Start'
        print self.cli.start('spinner')

        print 'log'
        out = self.cli.log('spinner')
        print out
        self.assertEqual(out.count('This is Spinning'), 3)
        print 'Done'

        out = self.cli.list()
        print out
        self.assertIn('ERROR', out)
        self.assertIn('Program did not successfully start', out)




if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
