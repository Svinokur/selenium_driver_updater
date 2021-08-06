#pylint: disable=broad-except,wrong-import-position, protected-access
#Standart library imports
import time
import unittest
import os.path
import logging

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))

# Local imports
from selenium_driver_updater._setting import setting
from selenium_driver_updater._safari_driver import SafariDriver
from selenium_driver_updater.util.requests_getter import RequestsGetter

logging.basicConfig(level=logging.INFO)

# pylint: disable=missing-function-docstring
class testSafariDriver(unittest.TestCase):
    """Class for unit-testing safaridriver class

    Attributes:
        path (str)              : Specific path where test drivers located
        safari_driver            : Initialize class SafariDriver
        startTime (float)       : Time of starting unit-tests
        setting (dict[str])     : Dict of all additional parametres
        specific_version (str)  : Specific version of chromedriver to test
    """

    @classmethod
    def setUpClass(cls):
        cls.setting = setting

        path : str = str(setting["Program"]["driversPath"])

        parametres = dict(driver_name='safaridriver', path=path, upgrade=True, chmod=True,
        check_driver_is_up_to_date = True, info_messages=True, version='',
        check_browser_is_up_to_date = False)

        cls.safari_driver = SafariDriver(**parametres)

        parametres.update(path='failure', filename='safaridriver1', version='blablabla')

        cls.safari_driver_failure = SafariDriver(**parametres)

        cls.requests_getter = RequestsGetter

    @classmethod
    def tearDownClass(cls):
        del cls.safari_driver
        del cls.safari_driver_failure

    def setUp(self):

        self.start_time : float = time.time()

    def tearDown(self):
        end_time = time.time() - self.start_time
        print("%.3f" % end_time)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_current_version_chrome_selenium_failure(self):
        current_version = self.safari_driver_failure._get_current_version_driver()
        self.assertEqual(len(current_version), 0, len(current_version))

    #@unittest.skip('Temporary not needed')
    def test02_check_compare_current_version_and_latest_version_safaridriver(self):
        self.safari_driver._compare_current_version_and_latest_version_safaridriver()

    #@unittest.skip('Temporary not needed')
    def test03_check_get_latest_version_safaridriver(self):
        latest_version = self.safari_driver._get_latest_version_safaridriver()
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test03_check_safaridriver(self):
        driver_path = self.safari_driver.main()
        self.assertIsNotNone(driver_path, driver_path)
        self.assertGreater(len(driver_path), 0, len(driver_path))


if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)
