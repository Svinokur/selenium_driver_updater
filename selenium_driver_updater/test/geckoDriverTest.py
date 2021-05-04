import unittest

import sys
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from _setting import setting
from geckoDriver import GeckoDriver
import time
import requests
import platform

base_dir = os.path.dirname(os.path.abspath(__file__))

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

    def setUp(self):
        self.path : str = os.path.abspath(base_dir) + os.path.sep + 'drivers' + os.path.sep

        self.gecko_driver = GeckoDriver(path=self.path, upgrade=True, chmod=True, 
        check_driver_is_up_to_date = True, info_messages=True, filename='geckodriver_test', version='',
        check_browser_is_up_to_date = False)
        
        self.startTime : float = time.time()
        self.setting = setting

        user_agent : str = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/35.0.1916.47 Safari/537.36'

        self.headers = {'User-Agent': user_agent}

        self.specific_version : str = '0.29.1'

        self.geckodriver_name : str = "geckodriver_test.exe" if platform.system() == 'Windows' else\
                                        "geckodriver_test"

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_get_result_by_request(self):
        url = self.setting["GeckoDriver"]["LinkLastRelease"]
        request = requests.get(url=url, headers=self.headers)
        status_code = request.status_code
        request_text = request.text
        self.assertEqual(status_code, 200, status_code)
        self.assertGreater(len(request_text), 0, request_text)

    #@unittest.skip('Temporary not needed')
    def test02_get_result_by_request(self):
        url = self.setting["GeckoDriver"]["LinkAllReleases"]
        request = requests.get(url=url, headers=self.headers)
        status_code = request.status_code
        request_text = request.text
        self.assertEqual(status_code, 200, status_code)
        self.assertGreater(len(request_text), 0, request_text)

    #@unittest.skip('Temporary not needed')
    def test03_check_get_specific_version_geckodriver_for_current_os(self):
        result, message = self.gecko_driver._GeckoDriver__delete_current_geckodriver_for_current_os()
        self.assertTrue(result, message)
        self.assertFalse(os.path.exists(self.path + self.geckodriver_name), self.path + self.geckodriver_name)

        result, message, file_name = self.gecko_driver._GeckoDriver__get_specific_version_geckodriver_for_current_os(version=self.specific_version)
        self.assertTrue(result, message)
        self.assertIsNotNone(file_name,file_name)
        self.assertGreater(len(file_name), 0, len(file_name))
        self.assertTrue(os.path.exists(self.path + self.geckodriver_name), self.path + self.geckodriver_name)

        result, message = self.gecko_driver._GeckoDriver__chmod_driver()
        self.assertTrue(result, message)

        result, message, current_version = self.gecko_driver._GeckoDriver__get_current_version_geckodriver_selenium()
        self.assertTrue(result, message)
        self.assertIsNotNone(current_version, current_version)
        self.assertGreaterEqual(len(current_version), 0, len(current_version))
        self.assertEqual(current_version, self.specific_version)
    
    #@unittest.skip('Temporary not needed')
    def test04_check_get_latest_version_gecko_driver(self):
        result, message, latest_version = self.gecko_driver._GeckoDriver__get_latest_version_geckodriver()
        self.assertTrue(result, message)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))
    
    #@unittest.skip('Temporary not needed')
    def test05_check_delete_current_geckodriver_for_current_os(self):
        result, message = self.gecko_driver._GeckoDriver__delete_current_geckodriver_for_current_os()
        self.assertTrue(result, message)
        self.assertFalse(os.path.exists(self.path + self.geckodriver_name), self.path + self.geckodriver_name)

    #@unittest.skip('Temporary not needed')
    def test06_check_get_latest_geckodriver_for_current_os(self):
        result, message, file_name = self.gecko_driver._GeckoDriver__get_latest_geckodriver_for_current_os()
        self.assertTrue(result, message)
        self.assertIsNotNone(file_name,file_name)
        self.assertGreater(len(file_name), 0, len(file_name))
        self.assertTrue(os.path.exists(self.path + self.geckodriver_name), self.path + self.geckodriver_name)

        result, message = self.gecko_driver._GeckoDriver__chmod_driver()
        self.assertTrue(result, message)

    #@unittest.skip('Temporary not needed')
    def test07_check_compare_current_version_and_latest_version(self):
        result, message, is_driver_is_up_to_date, current_version, latest_version = self.gecko_driver._GeckoDriver__compare_current_version_and_latest_version()
        self.assertTrue(result, message)
        self.assertIsNotNone(is_driver_is_up_to_date, is_driver_is_up_to_date)
        self.assertIsNotNone(current_version, current_version)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertTrue(is_driver_is_up_to_date, is_driver_is_up_to_date)
        self.assertGreater(len(current_version), 0, len(current_version))
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test08_check_get_current_version_firefox_selenium(self):
        result, message, current_version = self.gecko_driver._GeckoDriver__get_current_version_geckodriver_selenium()
        self.assertTrue(result, message)
        self.assertIsNotNone(current_version, current_version)
        self.assertGreater(len(current_version), 0, len(current_version))

    #@unittest.skip('Temporary not needed')
    def test09_check_get_latest_version_firefox_browser(self):
        result, message, latest_version = self.gecko_driver._GeckoDriver__get_latest_version_firefox_browser()
        self.assertTrue(result, message)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    @unittest.skip('Temporary could not test it on Github Workflow')
    def test10_check_get_latest_firefox_browser_for_current_os(self):
        result, message = self.gecko_driver._GeckoDriver__get_latest_firefox_browser_for_current_os()
        self.assertTrue(result, message)

    #@unittest.skip('Temporary not needed')
    @unittest.skip('Temporary could not test it on Github Workflow')
    def test11_check_compare_current_version_and_latest_version_firefox_browser(self):
        result, message, is_browser_is_up_to_date, current_version, latest_version = self.gecko_driver._GeckoDriver__compare_current_version_and_latest_version_firefox_browser()
        self.assertTrue(result, message)
        self.assertIsNotNone(is_browser_is_up_to_date, is_browser_is_up_to_date)
        self.assertIsNotNone(current_version, current_version)
        self.assertIsNotNone(latest_version, latest_version)

        self.assertTrue(is_browser_is_up_to_date, is_browser_is_up_to_date)
        
        self.assertGreater(len(current_version), 0, len(current_version))
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test12_check_geckodriver_is_up_to_date(self):
        result, message, filename = self.gecko_driver.main()
        self.assertTrue(result, message)
        self.assertGreater(len(filename), 0, len(filename))
        


if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)