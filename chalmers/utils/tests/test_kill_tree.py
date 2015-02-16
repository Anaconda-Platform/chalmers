import unittest
from chalmers.utils.kill_tree import kill_tree
from multiprocessing import Process
import time
import os

def child_process():
        p = Process(target=time.sleep, args=(100,))
        p.start()
        p.join()

class Test(unittest.TestCase):

    def test_kills_process(self):

        p = Process(target=time.sleep, args=(100,))
        p.start()
        self.assertTrue(p.is_alive())
        kill_tree(p.pid)
        p.join(1)
        self.assertFalse(p.is_alive())

    def test_does_not_fail(self):

        p = Process(target=child_process)
        p.start()
        self.assertTrue(p.is_alive())
        time.sleep(.1)
        kill_tree(p.pid)
        p.join(1)
        self.assertFalse(p.is_alive())


if __name__ == '__main__':
    unittest.main()

