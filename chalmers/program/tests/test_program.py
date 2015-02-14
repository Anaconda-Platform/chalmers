from os.path import join
import tempfile
import unittest

from chalmers import config
from chalmers.program.base import ProgramBase


class TestProgram(ProgramBase):

    def _send_signal(self, pid, signal):
        pass

    @property
    def is_running(self):
        pass

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
        expected_keys = [u'stdout', u'redirect_stderr', u'stopwaitsecs', u'startsecs',
                         u'stopsignal', u'name', u'log_dir', u'startretries',
                         u'daemon_log', u'exitcodes']
        self.assertEqual(p.data.keys(), expected_keys)
        self.assertEqual(p.state, {})





if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
