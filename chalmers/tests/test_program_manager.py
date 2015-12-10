from __future__ import unicode_literals, print_function
from os.path import join
import tempfile
import unittest

import mock

from chalmers import program_manager, config
from chalmers.program import Program
import time
import logging
import io


class Test(unittest.TestCase):

    def setUp(self):

        self.root_config = join(tempfile.mkdtemp(), 'chalmers_tests')
        config.set_relative_dirs(self.root_config)
        unittest.TestCase.setUp(self)


    @mock.patch('chalmers.program_manager.Program')
    def test_start_program(self, MockProgram):

        program_manager.start_program('name', setup_logging=True)

        MockProgram.assert_called_once_with('name')
        MockProgram().start_sync.assert_called_once_with()

    def test_manager_empty(self):

        pm = program_manager.ProgramManager()
        pm.start_all()
        self.assertEqual(pm.processes, [])

    def test_manager(self):
        prog = Program.add('name', ['echo', 'name'])

        pm = program_manager.ProgramManager(setup_logging=False)
        pm.start_all()
        self.assertEqual(len(pm.processes), 1)

        time.sleep(1)
        prog.state.reload()

        self.assertEqual(prog.text_status, 'STOPPED')
        self.assertEqual(prog.state['reason'], 'Program exited gracefully')


    @mock.patch('chalmers.program_manager.Program')
    def test_logging(self, MockProgram):

        Program.add('name', ['echo', 'name'])

        log = logging.getLogger('chalmers')
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.Formatter('%(msg)s'))
        log.addHandler(handler)

        def log_something():

            log.info('hello')

        MockProgram().start_sync.side_effect = log_something

        program_manager.start_program('name', setup_logging=True)

        MockProgram().start_sync.assert_called_once_with()

        self.assertEqual(stream.getvalue().strip(), '[name] hello')




if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_start']
    unittest.main()
