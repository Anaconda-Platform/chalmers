import unittest
from chalmers import utils
import io

class Test(unittest.TestCase):


    def test_try_eval(self):
        self.assertEqual(utils.try_eval('hello'), 'hello')
        self.assertEqual(utils.try_eval('~1"'), '~1"')

    def test_set_nested_key_1(self):
        dct = {}
        utils.set_nested_key(dct, 'key', 'value')
        self.assertEqual(dct, {'key':'value'})

    def test_set_nested_key_2(self):
        dct = {}
        utils.set_nested_key(dct, 'key.key', 'value')
        self.assertEqual(dct, {'key':{'key':'value'}})

    def test_print_opts(self):

        stream = io.StringIO()
        utils.print_opts('category', {'foo':'bar', 'baz':1}, ['foo'], file=stream)

        expected = "\ncategory\n--------\n         foo: 'bar'\n"
        self.assertEqual(stream.getvalue(), expected)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
