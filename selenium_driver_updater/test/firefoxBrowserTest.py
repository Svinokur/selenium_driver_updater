import unittest

import sys
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from _setting import setting
from browsers._firefoxBrowser import FirefoxBrowser

base_dir = os.path.dirname(os.path.abspath(__file__))

import time
import logging
logging.basicConfig(level=logging.INFO)

class testFirefoxBrowser(unittest.TestCase): 
    """Class for unit-testing FirefoxBrowser class

    Attributes:
        path (str)              : Specific path where test drivers located
        chrome_driver           : Initialize class ChromeDriver
        startTime (float)       : Time of starting unit-tests
        setting (dict[str])     : Dict of all additional parametres
        specific_version (str)  : Specific version of chromedriver to test
    """

    @classmethod
    def setUpClass(cls):
        cls.setting = setting

        path : str = os.path.abspath(base_dir) + os.path.sep + 'drivers' + os.path.sep + 'geckodriver'

        cls.firefoxbrowser = FirefoxBrowser(path=path, check_browser_is_up_to_date = True)
        
    @classmethod
    def tearDownClass(cls):
        del cls.firefoxbrowser

    def setUp(self):

        self.startTime : float = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_latest_version_firefox_browser(self):
        result, message, latest_version = self.firefoxbrowser._FirefoxBrowser__get_latest_version_firefox_browser()
        self.assertTrue(result, message)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))
    
    #@unittest.skip('Temporary could not test it on Github Workflow')
    def test02_check_get_latest_firefox_browser_for_current_os(self):
        result, message = self.firefoxbrowser._FirefoxBrowser__get_latest_firefox_browser_for_current_os()
        self.assertTrue(result, message)
    
    #@unittest.skip('Temporary could not test it on Github Workflow')
    def test03_check_compare_current_version_and_latest_version_firefox_browser(self):
        result, message, is_browser_is_up_to_date, current_version, latest_version = self.firefoxbrowser._FirefoxBrowser__compare_current_version_and_latest_version_firefox_browser()
        self.assertTrue(result, message)
        self.assertIsNotNone(is_browser_is_up_to_date, is_browser_is_up_to_date)
        self.assertIsNotNone(current_version, current_version)
        self.assertIsNotNone(latest_version, latest_version)

        self.assertIn(is_browser_is_up_to_date, [True, False], is_browser_is_up_to_date)
        
        self.assertGreater(len(current_version), 0, len(current_version))
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test04_check_geckodriver_is_up_to_date(self):
        result, message = self.firefoxbrowser.main()
        self.assertTrue(result, message)


if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)