import unittest
from chalmers.program import Program


class Test(unittest.TestCase):

    def test_Init(self):
        p = Program('name', load=False)
        self.assertEqual(p.name, 'name')

    def test_(self):
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
