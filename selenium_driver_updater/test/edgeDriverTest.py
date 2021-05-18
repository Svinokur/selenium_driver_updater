import unittest

import sys
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from _setting import setting
from _edgeDriver import EdgeDriver
from util.requests_getter import RequestsGetter
import time
import platform

base_dir = os.path.dirname(os.path.abspath(__file__))

import logging
logging.basicConfig(level=logging.INFO)

class testEdgeDriver(unittest.TestCase): 
    """Class for unit-testing EdgeDriver class

    Attributes:
        path (str)              : Specific path where test drivers located
        edge_driver             : Initialize class EdgeDriver
        startTime (float)       : Time of starting unit-tests
        setting (dict[str])     : Dict of all additional parametres
        headers                 : Needed headers for requests
        specific_version (str)  : Specific version of edgedriver to test
    """

    @classmethod
    def setUpClass(cls):
        cls.setting = setting

        path : str = os.path.abspath(base_dir) + os.path.sep + 'drivers' + os.path.sep

        cls.edgedriver = EdgeDriver(path=path, upgrade=True, chmod=True, 
        check_driver_is_up_to_date = True, info_messages=True, filename='edgedriver_test', version='',
        check_browser_is_up_to_date = False)

        cls.edgedriver_failure = EdgeDriver(path='failure', upgrade=True, chmod=True, 
        check_driver_is_up_to_date = True, info_messages=True, filename='edgedriver1_test', version='blablabla',
        check_browser_is_up_to_date = False)

        cls.requests_getter = RequestsGetter
        
    @classmethod
    def tearDownClass(cls):
        del cls.edgedriver
        del cls.edgedriver_failure

    def setUp(self):
        self.path : str = os.path.abspath(base_dir) + os.path.sep + 'drivers' + os.path.sep
        
        self.startTime : float = time.time()

        self.specific_version : str = '90.0.818.49'
        self.specific_version_failure : str = 'blablablanotversion'

        self.edgedriver_name : str = "edgedriver_test.exe" if platform.system() == 'Windows' else\
                                        "edgedriver_test"

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_current_version_edge_selenium_failure(self):
        result, message, current_version = self.edgedriver_failure._EdgeDriver__get_current_version_edgedriver_selenium()
        self.assertTrue(result, message)
        self.assertGreaterEqual(len(message), 0, len(message))
        self.assertEqual(len(current_version), 0, len(current_version))

    #@unittest.skip('Temporary not needed')
    def test02_check_get_specific_version_edgedriver_for_current_os_failure(self):
        result, message, file_name = self.edgedriver_failure._EdgeDriver__get_specific_version_edgedriver_for_current_os(version=self.specific_version_failure)
        self.assertFalse(result, result)
        self.assertGreater(len(message), 0, len(message))
        self.assertEqual(len(file_name), 0, len(file_name))

    #@unittest.skip('Temporary not needed')
    def test03_check_compare_current_version_and_latest_version_failure(self):
        result, message, is_driver_is_up_to_date, current_version, latest_version = self.edgedriver_failure._EdgeDriver__compare_current_version_and_latest_version()
        self.assertTrue(result, message)
        self.assertGreaterEqual(len(message), 0, len(message))
        self.assertFalse(is_driver_is_up_to_date, is_driver_is_up_to_date)
        self.assertEqual(len(current_version), 0, len(current_version))
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test04_check_if_edgedriver_is_up_to_date_failure(self):
        result, message, filename = self.edgedriver_failure.main()
        self.assertFalse(result, result)
        self.assertGreater(len(message), 0, len(message))
        self.assertEqual(len(filename), 0, len(filename))

    #@unittest.skip('Temporary not needed')
    def test05_check_get_result_by_request(self):
        url = self.setting["EdgeDriver"]["LinkLastRelease"]
        result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertTrue(result, message)
        self.assertEqual(status_code, 200, status_code)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))

    #@unittest.skip('Temporary not needed')
    def test06_check_get_result_by_request(self):
        url = self.setting["EdgeBrowser"]["LinkAllLatestRelease"]
        result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertTrue(result, message)
        self.assertEqual(status_code, 200, status_code)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))

    #@unittest.skip('Temporary not needed')
    def test07_check_get_current_version_edge_selenium(self):
        result, message, current_version = self.edgedriver._EdgeDriver__get_current_version_edgedriver_selenium()
        self.assertTrue(result, message)
        self.assertIsNotNone(current_version, current_version)
        self.assertGreaterEqual(len(current_version), 0, len(current_version))

    #@unittest.skip('Temporary not needed')
    def test08_check_get_specific_version_edgedriver_for_current_os(self):
        result, message = self.edgedriver._EdgeDriver__delete_current_edgedriver_for_current_os()
        self.assertTrue(result, message)
        self.assertFalse(os.path.exists(self.path + self.edgedriver_name), self.path + self.edgedriver_name)

        result, message, file_name = self.edgedriver._EdgeDriver__get_specific_version_edgedriver_for_current_os(version=self.specific_version)
        self.assertTrue(result, message)
        self.assertIsNotNone(file_name,file_name)
        self.assertGreater(len(file_name), 0, len(file_name))
        self.assertTrue(os.path.exists(self.path + self.edgedriver_name), self.path + self.edgedriver_name)

        result, message = self.edgedriver._EdgeDriver__chmod_driver()
        self.assertTrue(result, message)

        result, message, current_version = self.edgedriver._EdgeDriver__get_current_version_edgedriver_selenium()
        self.assertTrue(result, message)
        self.assertIsNotNone(current_version, current_version)
        self.assertGreaterEqual(len(current_version), 0, len(current_version))
        self.assertEqual(current_version, self.specific_version)
    
    #@unittest.skip('Temporary not needed')
    def test09_check_get_latest_version_edge_driver(self):
        result, message, latest_version = self.edgedriver._EdgeDriver__get_latest_version_edgedriver()
        self.assertTrue(result, message)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))
    
    #@unittest.skip('Temporary not needed')
    def test10_check_delete_current_edgedriver_for_current_os(self):
        result, message = self.edgedriver._EdgeDriver__delete_current_edgedriver_for_current_os()
        self.assertTrue(result, message)
        self.assertFalse(os.path.exists(self.path + self.edgedriver_name), self.path + self.edgedriver_name)

    #@unittest.skip('Temporary not needed')
    def test11_check_get_latest_edgedriver_for_current_os(self):
        result, message, latest_version = self.edgedriver._EdgeDriver__get_latest_version_edgedriver()
        self.assertTrue(result, message)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))

        result, message, file_name = self.edgedriver._EdgeDriver__get_latest_edgedriver_for_current_os()
        self.assertTrue(result, message)
        self.assertIsNotNone(file_name,file_name)
        self.assertGreater(len(file_name), 0, len(file_name))
        self.assertTrue(os.path.exists(self.path + self.edgedriver_name), self.path + self.edgedriver_name)

        result, message = self.edgedriver._EdgeDriver__chmod_driver()
        self.assertTrue(result, message)

    #@unittest.skip('Temporary not needed')
    def test12_check_compare_current_version_and_latest_version(self):
        result, message, is_driver_is_up_to_date, current_version, latest_version = self.edgedriver._EdgeDriver__compare_current_version_and_latest_version()
        self.assertTrue(result, message)
        self.assertIsNotNone(is_driver_is_up_to_date, is_driver_is_up_to_date)
        self.assertIsNotNone(current_version, current_version)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertTrue(is_driver_is_up_to_date, is_driver_is_up_to_date)
        self.assertGreater(len(current_version), 0, len(current_version))
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test13_check_get_current_version_edge_selenium(self):
        result, message, current_version = self.edgedriver._EdgeDriver__get_current_version_edgedriver_selenium()
        self.assertTrue(result, message)
        self.assertIsNotNone(current_version, current_version)
        self.assertGreater(len(current_version), 0, len(current_version))

    #@unittest.skip('Temporary not needed')
    def test14_check_get_latest_version_edge_browser(self):
        result, message, latest_version = self.edgedriver._EdgeDriver__get_latest_version_edge_browser()
        self.assertTrue(result, message)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))
    
    #@unittest.skip('Temporary could not test it on Github Workflow')
    def test15_check_get_latest_edge_browser_for_current_os(self):
        result, message = self.edgedriver._EdgeDriver__get_latest_edge_browser_for_current_os()
        self.assertTrue(result, message)
    
    #@unittest.skip('Temporary could not test it on Github Workflow')
    def test16_check_compare_current_version_and_latest_version_edge_browser(self):
        result, message, is_browser_is_up_to_date, current_version, latest_version = self.edgedriver._EdgeDriver__compare_current_version_and_latest_version_edge_browser()
        self.assertTrue(result, message)
        self.assertIsNotNone(is_browser_is_up_to_date, is_browser_is_up_to_date)
        self.assertIsNotNone(current_version, current_version)
        self.assertIsNotNone(latest_version, latest_version)

        self.assertIn(is_browser_is_up_to_date, [True, False], is_browser_is_up_to_date)
        
        self.assertGreater(len(current_version), 0, len(current_version))
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test17_check_if_edgedriver_is_up_to_date(self):
        result, message, filename = self.edgedriver.main()
        self.assertTrue(result, message)
        self.assertGreater(len(filename), 0, len(filename))
        
if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)