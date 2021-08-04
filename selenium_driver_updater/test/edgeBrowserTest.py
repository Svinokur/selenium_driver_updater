#pylint: disable=wrong-import-position, protected-access
#Standart library imports
import unittest
import os.path
import time
import logging
import platform


import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))

# Local imports
from selenium_driver_updater._setting import setting
from selenium_driver_updater.browsers._edgeBrowser import EdgeBrowser
from selenium_driver_updater.util.requests_getter import RequestsGetter

logging.basicConfig(level=logging.INFO)

# pylint: disable=missing-function-docstring
class testEdgeBrowser(unittest.TestCase):
    """Class for unit-testing EdgeBrowser class

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

        driver_name : str = "edgedriver_test.exe" if platform.system() == 'Windows' else\
                                        "edgedriver_test"

        path : str = str(setting["Program"]["driversPath"]) + driver_name

        cls.edgebrowser = EdgeBrowser(path=path, check_browser_is_up_to_date = True)

        cls.requests_getter = RequestsGetter

    @classmethod
    def tearDownClass(cls):
        del cls.edgebrowser

    def setUp(self):

        self.start_time : float = time.time()

    def tearDown(self):
        end_time = time.time() - self.start_time
        print("%.3f" % end_time)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_result_by_request(self):
        url = str(self.setting["EdgeBrowser"]["LinkAllLatestRelease"])
        json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))

    #@unittest.skip('Temporary not needed')
    def test02_check_get_latest_version_edge_browser(self):
        latest_version = self.edgebrowser._get_latest_version_edge_browser()
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary could not test it on Github Workflow')
    def test03_check_get_latest_edge_browser_for_current_os(self):
        self.edgebrowser._get_latest_edge_browser_for_current_os()

    #@unittest.skip('Temporary could not test it on Github Workflow')
    def test04_check_compare_current_version_and_latest_version_edge_browser(self):
        is_browser_is_up_to_date, current_version, latest_version = self.edgebrowser._compare_current_version_and_latest_version_edge_browser()
        self.assertIsNotNone(is_browser_is_up_to_date, is_browser_is_up_to_date)
        self.assertIsNotNone(current_version, current_version)
        self.assertIsNotNone(latest_version, latest_version)

        self.assertIn(is_browser_is_up_to_date, [True, False], is_browser_is_up_to_date)

        self.assertGreater(len(current_version), 0, len(current_version))
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test05_check_if_edgebrowser_is_up_to_date(self):
        self.edgebrowser.main()


if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)
    