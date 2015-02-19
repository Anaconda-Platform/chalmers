import unittest
from chalmers.event_dispatcher import EventDispatcher
from chalmers import config, errors

from os.path import join
import tempfile
import os

class TestEventDispatcher(EventDispatcher):

    @property
    def name(self):
        return 'test'

    def dispatch_foo(self, value):
        self.foo = value

    def dispatch_error(self, value):
        raise Exception("Expected dispatch error")

class Test(unittest.TestCase):

    def setUp(self):

        self.root_config = join(tempfile.gettempdir(), 'chalmers_tests')
        config.set_relative_dirs(self.root_config)

        unittest.TestCase.setUp(self)


    def test_init(self):
        dispatcher = TestEventDispatcher()
        self.assertFalse(dispatcher.is_listening)

    def test_listen(self):

        d = TestEventDispatcher()

        if os.path.exists(d.addr):
            os.unlink(d.addr)

        self.assertFalse(d.is_listening)

        d.start_listener()

        self.assertTrue(d.is_listening)

        if os.name != 'nt':
            self.assertTrue(os.path.exists(d.addr))

        d.send('foo', 1)
        d.send('exitloop')

        d._listener_thread.join()

        self.assertFalse(d.is_listening)
        self.assertEqual(d.foo, 1)

    def test_exception(self):

        d = TestEventDispatcher()

        if os.path.exists(d.addr):
            os.unlink(d.addr)

        self.assertFalse(d.is_listening)

        d.start_listener()

        with self.assertRaises(errors.ChalmersError):
            d.send('error', 1)

        self.assertTrue(d.is_listening)

        d.send('exitloop')

        d._listener_thread.join()

        self.assertFalse(d.is_listening)




if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
