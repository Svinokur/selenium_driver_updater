#pylint: disable=broad-except,wrong-import-position, protected-access
#Standart library imports
import unittest
import time
import logging

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))

# Local imports
from selenium_driver_updater._setting import setting
from selenium_driver_updater._chromiumChromeDriver import ChromiumChromeDriver
from selenium_driver_updater.util.requests_getter import RequestsGetter


logging.basicConfig(level=logging.INFO)

# pylint: disable=missing-function-docstring
class testChromiumChromeDriver(unittest.TestCase):
    """Class for unit-testing ChromiumChromeDriver class

    Attributes:
        chromium_chromedriver   : Initialize class ChromiumChromeDriver
        startTime (float)       : Time of starting unit-tests
    """

    @classmethod
    def setUpClass(cls):

        cls.setting = setting

        cls.chromium_chromedriver = ChromiumChromeDriver(check_driver_is_up_to_date = True, check_browser_is_up_to_date = False)

        cls.requests_getter = RequestsGetter

    @classmethod
    def tearDownClass(cls):
        del cls.chromium_chromedriver

    def setUp(self):

        self.start_time : float = time.time()

    def tearDown(self):
        end_time = time.time() - self.start_time
        print("%.3f" % end_time)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_result_by_request(self):
        url = str(self.setting["ChromeDriver"]["LinkLastRelease"])
        json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))

    #@unittest.skip('Temporary not needed')
    def test02_check_get_current_version_chromium_chromedriver(self):
        current_version = self.chromium_chromedriver._get_current_version_chromium_chromedriver()
        self.assertIsNotNone(current_version, current_version)
        self.assertGreaterEqual(len(current_version), 0, len(current_version))

    #@unittest.skip('Temporary not needed')
    def test03_check_get_latest_version_chromium_chromedriver(self):
        latest_version = self.chromium_chromedriver._get_latest_version_chromium_chromedriver()
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test04_check_get_latest_chromium_chromedriver_for_current_os(self):
        driver_path = self.chromium_chromedriver._get_latest_chromium_chromedriver_for_current_os()
        self.assertIsNotNone(driver_path, driver_path)
        self.assertGreaterEqual(len(driver_path), 0, len(driver_path))

    #@unittest.skip('Temporary not needed')
    def test05_check_compare_current_version_and_latest_version(self):
        is_driver_is_up_to_date, current_version, latest_version = self.chromium_chromedriver._compare_current_version_and_latest_version()
        self.assertIsNotNone(is_driver_is_up_to_date, is_driver_is_up_to_date)
        self.assertIsNotNone(current_version, current_version)
        self.assertIsNotNone(latest_version, latest_version)

        self.assertTrue(is_driver_is_up_to_date, is_driver_is_up_to_date)

        self.assertGreater(len(current_version), 0, len(current_version))
        self.assertGreater(len(latest_version), 0, len(latest_version))

     #@unittest.skip('Temporary not needed')
    def test06_check_chromedriver_is_up_to_date(self):
        filename = self.chromium_chromedriver.main()
        self.assertGreaterEqual(len(filename), 0, len(filename))

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)
    