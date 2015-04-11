from __future__ import print_function, unicode_literals

import os
import shutil
from subprocess import check_output
import sys
import time
import unittest

from chalmers.scripts import chalmers_main


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

            print("> chalmers", subcommand, " ".join(args))
            out = check_output(cmd, env=self.env)

            if isinstance(out, bytes):
                out = out.decode()

            print("   || " + "\n   || ".join(out.splitlines()))
            print("")
            return out
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
        self.cli.add('echo', 'hi')
        self.cli.start('echo', wait=False)
        time.sleep(1)
        self.cli.log('echo', '-f')

    def test_long_running_process(self):
        print('Add Long running process')
        script = script_path('long_running_process.py')
        self.cli.add('-n', 'lrp', sys.executable, script)
        self.cli.start('lrp')
        out = self.cli.list()
        self.assertIn('RUNNING', out)

        self.cli.stop('lrp')
        out = self.cli.log('lrp')
        self.assertIn('This is LRP', out)

        out = self.cli.list()
        self.assertIn('OFF', out)

        print('> done')


    def test_sigint(self):
        print('Test Sigint')
        script = script_path('long_running_process.py')
        self.cli.add('-n', 'lrp', sys.executable, script)
        self.cli.set('lrp', 'stopsignal=SIGINT')
        self.cli.start('lrp')
        out = self.cli.list()
        self.assertIn('RUNNING', out)
        self.cli.stop('lrp')
        out = self.cli.log('lrp')
        self.assertIn('This is LRP', out)
        self.assertIn('KeyboardInterrupt', out)
        out = self.cli.list()
        self.assertIn('OFF', out)

        print('> done')

    def test_spinning_process(self):
        'Add Long Spinning process'
        script = script_path('spinning_process.py')
        self.cli.add('-n', 'spinner', sys.executable, script)
        self.cli.start('spinner')

        out = self.cli.log('spinner')
        self.assertEqual(out.count('This is Spinning'), 3)
        out = self.cli.list()
        self.assertIn('ERROR', out)
        self.assertIn('Program did not successfully start', out)
        print("> done")



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
