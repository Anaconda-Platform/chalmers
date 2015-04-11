from __future__ import print_function, unicode_literals
import io
import logging
import os
import shutil
import unittest

import mock
import yaml

from chalmers import config, errors
from chalmers.scripts import chalmers_main


class ChalmersCli(object):
    def __init__(self):
        self.script = chalmers_main.__file__
        if self.script.endswith('.pyc') or self.script.endswith('.pyo'):
            self.script = self.script[:-1]
        self.env = os.environ.copy()
        self.root = 'test_config'
        self.env['CHALMERS_ROOT'] = self.root
        config.set_relative_dirs(self.root)

        logging.getLogger('cli-logger').addHandler(logging.NullHandler())


    def __getattr__(self, subcommand):

        def run_subcommand(*args):
            cmd = ['-q', '--no-color', subcommand]
            cmd.extend(args)

            out = io.StringIO()

            log = logging.getLogger('chalmers')
            log.setLevel(logging.ERROR)
            del log.handlers[:]

            with mock.patch('sys.stdout', out), mock.patch('chalmers.scripts.chalmers_main.setup_logging'):
                chalmers_main.main(cmd, False)

            return out.getvalue()

        return run_subcommand


class Test(unittest.TestCase):

    def setUp(self):
        self.cli = ChalmersCli()
        if os.path.isdir(self.cli.root):
            shutil.rmtree(self.cli.root)
        unittest.TestCase.setUp(self)

    def tearDown(self):
        if os.path.isdir(self.cli.root):
            shutil.rmtree(self.cli.root)
        unittest.TestCase.tearDown(self)

    def test_add_show(self):
        self.cli.add('echo', 'hi', '--off', '--off')
        self.assertEqual(self.cli.show('echo', '--cmd').strip(), 'echo hi')
        self.assertEqual(self.cli.show('echo', '--cmd').strip(), 'echo hi')


    def test_cant_add_twice(self):
        self.cli.add('echo', 'hi', '--off')
        with self.assertRaises(errors.ChalmersError):
            self.cli.add('echo', 'hi', '--off')

    def test_add_remove(self):
        self.cli.add('echo', 'hi', '--off')
        self.cli.remove('echo')

    def test_cant_remove_non_existent(self):

        with self.assertRaises(SystemExit):
            self.cli.remove('echo')

    def test_cant_start_non_existent(self):

        with self.assertRaises(SystemExit):
            self.cli.start('echo')


    def test_list_no_programs(self):

        out = self.cli.list()
        self.assertEqual(out.strip(), "No programs added")

    def test_list(self):

        out = self.cli.add('echo', 'hi', '--off')
        out = self.cli.list()
        self.assertEqual(out.split(), ['echo', 'OFF'])

    def test_pause(self):

        out = self.cli.add('echo', 'hi', '--off')

        out = self.cli.list()
        self.assertEqual(out.split(), ['echo', 'OFF'])

        out = self.cli.on('echo')

        out = self.cli.list()
        self.assertEqual(out.split(), ['echo', 'STOPPED'])

        out = self.cli.off('echo')

        out = self.cli.list()
        self.assertEqual(out.split(), ['echo', 'OFF'])

    def test_show(self):

        self.cli.add('echo', 'hi', '--off')
        out = self.cli.show('echo')

    def test_set(self):

        self.cli.add('echo', 'hi', '--off')
        out = self.cli.set('echo', 'x=1')
        self.assertEqual(out.strip(), "Set 'x' to 1 for program echo\ndone")
        out = self.cli.show('echo', '--def')
        with open(out.strip()) as fd:
            data = yaml.load(fd)

        self.assertEqual(data['x'], 1)

    def test_start(self):

        self.cli.add('echo', 'This is the output', '--off')
        out = self.cli.start('echo', '-w')

    def test_log(self):

        self.cli.add('echo', 'This is the output', '--off')
        out = self.cli.start('echo', '-w')
        out = self.cli.log('echo')
        self.assertIn('This is the output', out)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
