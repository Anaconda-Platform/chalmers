from contextlib import contextmanager
import tempfile
import unittest

import subprocess as sp
from os import path
import mock
# from win32api import GetUserName
# from win32com.shell import shell
# from win32serviceutil import RemoveService, StopService
import sys
class Test(unittest.TestCase):

    def setUp(self):

        modules = {
            'win32api': mock.Mock(),
            'win32com': mock.Mock(),
            'win32com.shell': mock.Mock(),
            'win32serviceutil': mock.Mock(),
            'pywintypes': mock.Mock(),
            'win32service': mock.Mock()        
        }

        sys.modules.update(modules)

        
        from chalmers.service.win32_system_service import Win32SystemService

        self.modules = modules
        self.Win32SystemService = Win32SystemService

    def test_service_name(self):
        service = self.Win32SystemService("me")
        self.assertEqual(service.service_name, 'chalmers:manager:me')

    def test_service_name(self):
        service = self.Win32SystemService("me")
        self.assertEqual(service.service_name, 'chalmers:manager:me')

    @mock.patch('getpass.getpass')
    def test_install(self, getpass):
        
        getpass.return_value = 'password'

        service = self.Win32SystemService("me")
        service.install()

        getpass.assert_called_with('Password for me: ')


if __name__ == "__main__":
    unittest.main()
