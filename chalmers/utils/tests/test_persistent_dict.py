import unittest
from chalmers.utils.persistent_dict import PersistentDict
import os

class Test(unittest.TestCase):

    def test_init(self):
        filename = 'test_filename.yaml'
        self.addCleanup(lambda : os.path.isfile(filename) and os.unlink(filename))
        d = PersistentDict(filename)
        d.update(x=1)

        self.assertEqual(d, {'x':1})

        d2 = PersistentDict(filename)

        self.assertEqual(d2, {'x':1})

    def test_update(self):
        filename = 'test_filename.yaml'
        self.addCleanup(lambda : os.path.isfile(filename) and os.unlink(filename))
        d = PersistentDict(filename)
        d.update(z=1)
        self.assertEqual(d, {'z':1})
        d.update(z=2, y=2)
        self.assertEqual(d, {'z':2, 'y':2})

        d2 = PersistentDict(filename)

        self.assertEqual(d2, d)

    def test_setitem(self):
        filename = 'test_filename.yaml'
        self.addCleanup(lambda : os.path.isfile(filename) and os.unlink(filename))
        d = PersistentDict(filename)
        d['l'] = 1
        self.assertEqual(d, {'l':1})

        d2 = PersistentDict(filename)
        self.assertEqual(d2, d)

if __name__ == '__main__':
    unittest.main()

