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
from selenium_driver_updater.browsers._chromiumChromeBrowser import ChromiumChromeBrowser
from selenium_driver_updater.util.requests_getter import RequestsGetter

logging.basicConfig(level=logging.INFO)

# pylint: disable=missing-function-docstring
class testChromiumChromeBrowser(unittest.TestCase):
    """Class for unit-testing ChromiumChromeBrowser class

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
        cls.chromium_chromebrowser = ChromiumChromeBrowser(check_browser_is_up_to_date = True)
        cls.requests_getter = RequestsGetter

    @classmethod
    def tearDownClass(cls):
        del cls.chromium_chromebrowser

    def setUp(self):

        self.start_time : float = time.time()

    def tearDown(self):
        end_time = time.time() - self.start_time
        print("%.3f" % end_time)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_result_by_request(self):
        url = self.setting["ChromeBrowser"]["LinkAllLatestRelease"]
        json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))

    #@unittest.skip('Temporary not needed')
    def test02_check_get_current_version_chromiumbrowser_selenium(self):
        current_version = self.chromium_chromebrowser._ChromiumChromeBrowser__get_current_version_chromiumbrowser_selenium()
        self.assertIsNotNone(current_version, current_version)
        self.assertGreaterEqual(len(current_version), 0, len(current_version))

    #@unittest.skip('Temporary not needed')
    def test03_check_get_latest_version_chromiumbrowser(self):
        latest_version = self.chromium_chromebrowser._ChromiumChromeBrowser__get_latest_version_chromiumbrowser()
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test04_check_get_latest_chromium_browser_for_current_os(self):
        self.chromium_chromebrowser._ChromiumChromeBrowser__get_latest_chromium_browser_for_current_os()

    #@unittest.skip('Temporary not needed')
    def test05_check_chromedriver_is_up_to_date(self):
        self.chromium_chromebrowser.main()


if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)
    