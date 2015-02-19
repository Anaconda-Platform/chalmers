import os
from os.path import join
import tempfile
import unittest

from chalmers import config

if os.name == 'posix':
    from chalmers.program.posix import PosixProgram

@unittest.skipUnless(os.name == 'posix', 'Theses tests only run on posix systems')
class TestPosix(unittest.TestCase):

    def setUp(self):

        self.root_config = join(tempfile.gettempdir(), 'chalmers_tests')
        config.set_relative_dirs(self.root_config)
        unittest.TestCase.setUp(self)

    def test_init(self):

        p = PosixProgram('name', load=False)
        self.addCleanup(p.delete)
        self.assertEqual(p.name, 'name')

    def test_create(self):

        p = PosixProgram.create('name', {})
        self.addCleanup(p.delete)
        expected_keys = {u'stdout', u'redirect_stderr', u'stopwaitsecs', u'startsecs',
                         u'stopsignal', u'name', u'log_dir', u'startretries',
                         u'daemon_log', u'exitcodes'}
        self.assertEqual(set(p.data.keys()), expected_keys)
        self.assertEqual(p.state, {})





if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
