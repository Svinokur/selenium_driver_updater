#Standart library imports
import unittest
import os.path
import logging
import time
import platform
from pathlib import Path

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

# Local imports
from _setting import setting
from _geckoDriver import GeckoDriver
from util.requests_getter import RequestsGetter

logging.basicConfig(level=logging.INFO)

# pylint: disable=missing-function-docstring
class testGeckoDriver(unittest.TestCase): 
    """Class for unit-testing GeckoDriver class

    Attributes:
        path (str)              : Specific path where test drivers located
        gecko_driver            : Initialize class GeckoDriver
        startTime (float)       : Time of starting unit-tests
        setting (dict[str])     : Dict of all additional parametres
        headers                 : Needed headers for requests
        specific_version (str)  : Specific version of geckodriver to test
    """

    @classmethod
    def setUpClass(cls):
        cls.setting = setting

        path : str = str(setting["Program"]["driversPath"])

        parametres = dict(path=path, upgrade=True, chmod=True, 
        check_driver_is_up_to_date = True, info_messages=True, filename='geckodriver_test', version='',
        check_browser_is_up_to_date = False)

        cls.gecko_driver = GeckoDriver(**parametres)

        parametres.update(path='failure', filename='geckodriver1_test', version='blablablanotversion')

        cls.gecko_driver_failure = GeckoDriver(**parametres)

        cls.requests_getter = RequestsGetter

    @classmethod
    def tearDownClass(cls):
        del cls.gecko_driver
        del cls.gecko_driver_failure

    def setUp(self):
        self.path : str = str(setting["Program"]["driversPath"])

        self.start_time : float = time.time()

        self.specific_version : str = '0.29.1'
        self.specific_version_failure : str = 'blablablanotversion'

        self.geckodriver_name : str = "geckodriver_test.exe" if platform.system() == 'Windows' else\
                                        "geckodriver_test"

        self.geckodriver_path = self.path + self.geckodriver_name

    def tearDown(self):
        end_time = time.time() - self.start_time
        print("%.3f" % end_time)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_current_version_geckodriver_selenium_failure(self):
        result, message, current_version = self.gecko_driver_failure._GeckoDriver__get_current_version_geckodriver()
        self.assertTrue(result, message)
        self.assertGreaterEqual(len(message), 0, len(message))
        self.assertEqual(len(current_version), 0, len(current_version))

    #@unittest.skip('Temporary not needed')
    def test02_check_download_driver(self):
        result, message, file_name = self.gecko_driver_failure._GeckoDriver__download_driver(version=self.specific_version_failure)
        self.assertFalse(result, result)
        self.assertGreater(len(message), 0, len(message))
        self.assertEqual(len(file_name), 0, len(file_name))

    #@unittest.skip('Temporary not needed')
    def test03_check_compare_current_version_and_latest_version_failure(self):
        result, message, is_driver_is_up_to_date, current_version, latest_version = self.gecko_driver_failure._GeckoDriver__compare_current_version_and_latest_version()
        self.assertTrue(result, message)
        self.assertGreaterEqual(len(message), 0, len(message))
        self.assertFalse(is_driver_is_up_to_date, is_driver_is_up_to_date)
        self.assertEqual(len(current_version), 0, len(current_version))
        self.assertEqual(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test04_check_geckodriver_is_up_to_date_failure(self):
        result, message, filename = self.gecko_driver_failure.main()
        self.assertFalse(result, result)
        self.assertGreater(len(message), 0, len(message))
        self.assertEqual(len(filename), 0, len(filename))

    #@unittest.skip('Temporary not needed')
    def test05_check_if_version_is_valid_failure(self):
        url = 'blablablanoturl'
        version_url = self.specific_version_failure
        result, message = self.gecko_driver_failure._GeckoDriver__check_if_version_is_valid(url=url,version_url=version_url)
        self.assertFalse(result, result)
        self.assertGreater(len(message), 0, len(message))

    #@unittest.skip('Temporary not needed')
    def test06_check_get_result_by_request(self):
        url = self.setting["GeckoDriver"]["LinkLastRelease"]
        result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertTrue(result, message)
        self.assertEqual(status_code, 200, status_code)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))

    #@unittest.skip('Temporary not needed')
    def test07_check_download_driver_specific_version(self):
        result, message = self.gecko_driver._GeckoDriver__delete_current_geckodriver_for_current_os()
        self.assertTrue(result, message)
        self.assertFalse(Path(self.geckodriver_path).exists(), self.geckodriver_path)

        result, message, file_name = self.gecko_driver._GeckoDriver__download_driver(version=self.specific_version)
        self.assertTrue(result, message)
        self.assertIsNotNone(file_name,file_name)
        self.assertGreater(len(file_name), 0, len(file_name))
        self.assertTrue(Path(self.geckodriver_path).exists(), self.geckodriver_path)

        result, message = self.gecko_driver._GeckoDriver__chmod_driver()
        self.assertTrue(result, message)

        result, message, current_version = self.gecko_driver._GeckoDriver__get_current_version_geckodriver()
        self.assertTrue(result, message)
        self.assertIsNotNone(current_version, current_version)
        self.assertGreaterEqual(len(current_version), 0, len(current_version))
        self.assertEqual(current_version, self.specific_version)

    @unittest.skip('Temporary not needed')
    def test08_check_download_driver_latest_previous_version(self):
        result, message = self.gecko_driver._GeckoDriver__delete_current_geckodriver_for_current_os()
        self.assertTrue(result, message)
        self.assertFalse(Path(self.geckodriver_path).exists(), self.geckodriver_path)

        result, message, file_name = self.gecko_driver._GeckoDriver__download_driver(previous_version=True)
        self.assertTrue(result, message)
        self.assertIsNotNone(file_name,file_name)
        self.assertGreater(len(file_name), 0, len(file_name))
        self.assertTrue(Path(self.geckodriver_path).exists(), self.geckodriver_path)

        result, message = self.gecko_driver._GeckoDriver__chmod_driver()
        self.assertTrue(result, message)

        result, message, current_version = self.gecko_driver._GeckoDriver__get_current_version_geckodriver()
        self.assertTrue(result, message)
        self.assertIsNotNone(current_version, current_version)
        self.assertGreaterEqual(len(current_version), 0, len(current_version))

    #@unittest.skip('Temporary not needed')
    def test09_check_get_latest_version_gecko_driver(self):
        result, message, latest_version = self.gecko_driver._GeckoDriver__get_latest_version_geckodriver()
        self.assertTrue(result, message)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test10_check_delete_current_geckodriver_for_current_os(self):
        result, message = self.gecko_driver._GeckoDriver__delete_current_geckodriver_for_current_os()
        self.assertTrue(result, message)
        self.assertFalse(Path(self.geckodriver_path).exists(), self.geckodriver_path)

    #@unittest.skip('Temporary not needed')
    def test11_check_download_driver(self):
        result, message, file_name = self.gecko_driver._GeckoDriver__download_driver()
        self.assertTrue(result, message)
        self.assertIsNotNone(file_name,file_name)
        self.assertGreater(len(file_name), 0, len(file_name))
        self.assertTrue(Path(self.geckodriver_path).exists(), self.geckodriver_path)

        result, message = self.gecko_driver._GeckoDriver__chmod_driver()
        self.assertTrue(result, message)

    #@unittest.skip('Temporary not needed')
    def test12_check_compare_current_version_and_latest_version(self):
        result, message, is_driver_is_up_to_date, current_version, latest_version = self.gecko_driver._GeckoDriver__compare_current_version_and_latest_version()
        self.assertTrue(result, message)
        self.assertIsNotNone(is_driver_is_up_to_date, is_driver_is_up_to_date)
        self.assertIsNotNone(current_version, current_version)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertTrue(is_driver_is_up_to_date, is_driver_is_up_to_date)
        self.assertGreater(len(current_version), 0, len(current_version))
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test13_check_get_current_version_firefox_selenium(self):
        result, message, current_version = self.gecko_driver._GeckoDriver__get_current_version_geckodriver()
        self.assertTrue(result, message)
        self.assertIsNotNone(current_version, current_version)
        self.assertGreater(len(current_version), 0, len(current_version))

    #@unittest.skip('Temporary not needed')
    def test14_check_geckodriver_is_up_to_date(self):
        result, message, filename = self.gecko_driver.main()
        self.assertTrue(result, message)
        self.assertGreater(len(filename), 0, len(filename))

    ##@unittest.skip('Temporary not needed')
    def test15_check_if_version_is_valid(self):
        url = self.setting["GeckoDriver"]["LinkLastReleasePlatform"].format(self.specific_version, self.specific_version)

        result, message = self.gecko_driver._GeckoDriver__check_if_version_is_valid(url=url,version_url=self.specific_version)
        self.assertTrue(result, result)
        self.assertEqual(len(message), 0, len(message))


if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)
    