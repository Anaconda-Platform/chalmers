import os
from os.path import join
import signal
from subprocess import check_call, Popen
import tempfile
import unittest

import mock

from chalmers import config
from chalmers.program.base import ProgramBase


class TestProgram(ProgramBase):

    def _send_signal(self, pid, signal):
        pass

    @property
    def is_running(self):
        return getattr(self, '_test_is_running', False)

    def start_as_service(self):
        pass

class TestBase(unittest.TestCase):

    def setUp(self):

        self.root_config = join(tempfile.gettempdir(), 'chalmers_tests')
        config.set_relative_dirs(self.root_config)
        unittest.TestCase.setUp(self)

    def test_init(self):

        p = TestProgram('name', load=False)
        self.addCleanup(p.delete)
        self.assertEqual(p.name, 'name')

    def test_create(self):
        p = TestProgram.create('name', {})
        self.addCleanup(p.delete)
        expected_keys = {u'stdout', u'redirect_stderr', u'stopwaitsecs', u'startsecs',
                         u'stopsignal', u'name', u'log_dir', u'startretries',
                         u'daemon_log', u'exitcodes'}

        self.assertEqual(set(p.data.keys()), expected_keys)
        self.assertEqual(p.state, {})

    def test_stopsignal(self):
        p = TestProgram('name')
        self.addCleanup(p.delete)
        self.assertEqual(p.stopsignal, signal.SIGTERM)

        p.raw_data.update(stopsignal='foobar')
        p.mk_data()
        self.assertEqual(p.stopsignal, signal.SIGTERM)

        p.raw_data.update(stopsignal='SIGINT')
        p.mk_data()
        self.assertEqual(p.stopsignal, signal.SIGINT)

        p.raw_data.update(stopsignal=signal.SIGINT)
        p.mk_data()
        self.assertEqual(p.stopsignal, signal.SIGINT)

    def test_is_ok(self):

        p = TestProgram('name')
        self.addCleanup(p.delete)

        self.assertTrue(p.is_ok)
        p.state.update(exit_status=None)
        self.assertTrue(p.is_ok)

        p.state.update(exit_status=0)
        self.assertTrue(p.is_ok)

        p.state.update(exit_status=1)
        self.assertFalse(p.is_ok)

    def test_text_status(self):

        p = TestProgram('name')
        self.addCleanup(lambda : (setattr(p, '_test_is_running', False), p.delete()))
        self.assertEqual(p.text_status, 'STOPPED')

        p.state.update(paused=True)
        self.assertEqual(p.text_status, 'OFF')

        p.state.update(exit_status=1)
        self.assertEqual(p.text_status, 'ERROR')

        p._test_is_running = True
        self.assertEqual(p.text_status, 'RUNNING')

    def test_setup_output(self):

        p = TestProgram('name')

        if os.path.isfile(p.data['stdout']):
            os.unlink(p.data['stdout'])

        with p.setup_output() as (out, err):
            check_call(['echo', 'hello'], stdout=out, stderr=err)

        with open(p.data['stdout']) as fd:
            output = fd.read()

        self.assertEqual(output.strip(), 'hello')

        with p.setup_output() as (out, err):
            check_call(['echo', 'hello'], stdout=out, stderr=err)

        with open(p.data['stdout']) as fd:
            output = fd.read()

        self.assertEqual(output.split(), ['hello', 'hello'])

    def test_keep_alive_bad_command(self):

        p = TestProgram('name')

        if os.path.isfile(p.data['stdout']):
            os.unlink(p.data['stdout'])

        p.raw_data.update(command=['bad_command'])
        p.mk_data()

        p.keep_alive()

        self.assertEqual(p.state['child_pid'], None)
        self.assertNotEqual(p.state['exit_status'], 0)
        self.assertEqual(p.state['reason'], 'OSError running command "bad_command"')
        self.assertEqual(p.text_status, 'ERROR')


    def test_keep_alive_short(self):

        p = TestProgram('name')

        if os.path.isfile(p.data['stdout']):
            os.unlink(p.data['stdout'])

        p.raw_data.update(command=['echo', 'hi'])
        p.mk_data()

        p.keep_alive()

        self.assertEqual(p.state['child_pid'], None)
        self.assertEqual(p.state['exit_status'], 0)
        self.assertEqual(p.state['reason'], 'Program exited gracefully')
        self.assertEqual(p.text_status, 'STOPPED')

    def test_keep_alive_short_errors(self):

        p = TestProgram('name')

        if os.path.isfile(p.data['stdout']):
            os.unlink(p.data['stdout'])

        p.raw_data.update(command=['echo', 'hi'], exitcodes=[99])
        p.mk_data()

        p.keep_alive()

        self.assertEqual(p.state['child_pid'], None)
        self.assertEqual(p.state['exit_status'], 0)
        self.assertEqual(p.state['reason'], 'Program did not successfully start')
        self.assertEqual(p.text_status, 'ERROR')

    @mock.patch('chalmers.program.base.Popen')
    def test_keep_alive_terminating(self, MockPopen):

        p = TestProgram('name')

        def side_effect(*args, **kwargs):
            p._terminating = True
            return Popen(*args, **kwargs)

        MockPopen.side_effect = side_effect
        if os.path.isfile(p.data['stdout']):
            os.unlink(p.data['stdout'])

        p.raw_data.update(command=['echo', 'hi'])
        p.mk_data()

        p.keep_alive()

        self.assertEqual(p.state['child_pid'], None)
        self.assertEqual(p.state['exit_status'], None)
        self.assertEqual(p.state['reason'], 'Terminated at user request')
        self.assertEqual(p.text_status, 'STOPPED')

    def test_start_sync(self):

        p = TestProgram('name')
        p.keep_alive = lambda: None
        p.start_sync()





if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
