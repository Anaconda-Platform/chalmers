import os
from os.path import join
import tempfile
import unittest

from chalmers import config

if os.name == 'nt':
    from chalmers.program.nt import NTProgram

@unittest.skipUnless(os.name == 'nt', 'Theses tests only run on win32 systems')
class TestNT(unittest.TestCase):
    
    def setUp(self):

        self.root_config = join(tempfile.gettempdir(), 'chalmers_tests')
        config.set_relative_dirs(self.root_config)
        unittest.TestCase.setUp(self)

    def test_init(self):
        p = NTProgram('foo')
        self.addCleanup(p.delete)

    def test_is_running(self):
        p = NTProgram('foo')
        self.addCleanup(p.delete)

        p.state['pid'] = os.getpid()

        self.assertTrue(p.is_running)

        p.state['pid'] = None

if __name__ == "__main__":
    unittest.main()


