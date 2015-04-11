import unittest

from chalmers.service.darwin_service import DarwinService
from contextlib import contextmanager
import subprocess as sp
import xml.etree.ElementTree as ET

loaded_launchd = {}

def plist_value(value):
    if value.tag == 'string':
        return value.text
    elif value.tag == 'true':
        return True
    elif value.tag == 'false':
        return False
    elif value.tag == 'array':
        return [plist_value(v) for v in value.getchildren()]
    else:
        raise Exception("unexpected tag %s" % value)

def read_plist(path):
    etree = ET.parse(path)
    elems = etree.getroot().find('dict').getchildren()
    result = {}
    for i in range(0, len(elems), 2):
        key = elems[i].text
        result[key] = plist_value(elems[i + 1])
    return result

def mock_check_output(command, *args, **kwargs):
    if command[:2] == ['launchctl', 'list']:
        if command[2] not in loaded_launchd:
            raise sp.CalledProcessError(1, 'launchctl', 'not found')
        return loaded_launchd[command[2]]

    elif command[:2] == ['launchctl', 'load']:

        plist = read_plist(command[2])
        loaded_launchd[plist['Label']] = plist
        return repr(plist)
    elif command[:2] == ['launchctl', 'remove']:
        if command[2] not in loaded_launchd:
            raise sp.CalledProcessError(1, "launchctl", "no loaded")
        del loaded_launchd[command[2]]
        return 'ok'
    else:
        raise Exception('unknown command %r' % command)

class Test(unittest.TestCase):

    @contextmanager
    def mock_launchctl(self, exists=True):
        from mock import patch
        patch1 = patch('subprocess.check_output')
        with patch1 as check_output:
            if  exists:
                check_output.side_effect = mock_check_output
            else:
                check_output.side_effect = IOError(2, "err")
            yield

    def test_install(self):

        with self.mock_launchctl(exists=True):

            service = DarwinService(False)
            self.assertFalse(service.status())
            self.assertTrue(service.install())
            self.assertTrue(service.status())
            self.assertTrue(service.uninstall())
            self.assertFalse(service.status())
            self.assertFalse(service.uninstall())



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_status']
    unittest.main()
