import unittest

import sys
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from _setting import setting
from browsers._operaBrowser import OperaBrowser
import time
from util.requests_getter import RequestsGetter

base_dir = os.path.dirname(os.path.abspath(__file__))

import logging
logging.basicConfig(level=logging.INFO)

class testOperaBrowser(unittest.TestCase): 
    """Class for unit-testing OperaBrowser class

    Attributes:
        path (str)              : Specific path where test drivers located
        chrome_driver           : Initialize class OperaBrowser
        startTime (float)       : Time of starting unit-tests
        setting (dict[str])     : Dict of all additional parametres
        specific_version (str)  : Specific version of chromedriver to test
    """

    @classmethod
    def setUpClass(cls):
        cls.setting = setting

        path : str = os.path.abspath(base_dir) + os.path.sep + 'drivers' + os.path.sep + 'operadriver_test'

        cls.operabrowser = OperaBrowser(path=path, check_browser_is_up_to_date = True)
        cls.requests_getter = RequestsGetter
        
    @classmethod
    def tearDownClass(cls):
        del cls.operabrowser

    def setUp(self):

        self.startTime : float = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_result_by_request(self):
        url = self.setting["OperaBrowser"]["LinkAllReleases"]
        result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertTrue(result, message)
        self.assertEqual(status_code, 200, status_code)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))

    #@unittest.skip('Temporary not needed')
    def test02_check_get_latest_version_opera_browser(self):
        result, message, latest_version = self.operabrowser._OperaBrowser__get_latest_version_opera_browser()
        self.assertTrue(result, message)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary could not test it on Github Workflow')
    def test03_check_get_latest_opera_browser_for_current_os(self):
        result, message = self.operabrowser._OperaBrowser__get_latest_opera_browser_for_current_os()
        self.assertTrue(result, message)
    
    #@unittest.skip('Temporary could not test it on Github Workflow')
    def test04_check_compare_current_version_and_latest_version_opera_browser(self):
        result, message, is_browser_is_up_to_date, current_version, latest_version = self.operabrowser._OperaBrowser__compare_current_version_and_latest_version_opera_browser()
        self.assertTrue(result, message)
        self.assertIsNotNone(is_browser_is_up_to_date, is_browser_is_up_to_date)
        self.assertIsNotNone(current_version, current_version)
        self.assertIsNotNone(latest_version, latest_version)

        self.assertIn(is_browser_is_up_to_date, [True, False], is_browser_is_up_to_date)
        
        self.assertGreater(len(current_version), 0, len(current_version))
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test05_check_chromedriver_is_up_to_date(self):
        result, message = self.operabrowser.main()
        self.assertTrue(result, message)


if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)