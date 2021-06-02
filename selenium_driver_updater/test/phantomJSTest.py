import unittest

import sys
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from _setting import setting
from _phantomJS import PhantomJS
import time
import platform
from util.requests_getter import RequestsGetter

base_dir = os.path.dirname(os.path.abspath(__file__))

import logging
logging.basicConfig(level=logging.INFO)

class testPhantomJS(unittest.TestCase): 
    """Class for unit-testing PhantomJS class

    Attributes:
        path (str)              : Specific path where test drivers located
        phantomjs               : Initialize class PhantomJS
        startTime (float)       : Time of starting unit-tests
        setting (dict[str])     : Dict of all additional parametres
        specific_version (str)  : Specific version of chromedriver to test
    """

    @classmethod
    def setUpClass(cls):
        cls.setting = setting

        path : str = os.path.abspath(base_dir) + os.path.sep + 'drivers' + os.path.sep

        cls.phantomjs = PhantomJS(path=path, upgrade=True, chmod=True, 
        check_driver_is_up_to_date = True, info_messages=True, filename='phantomjs_test', version='')

        cls.phantomjs_failure = PhantomJS(path='failure', upgrade=True, chmod=True, 
        check_driver_is_up_to_date = True, info_messages=True, filename='phatomjs1_test', version='blablabla')

        cls.requests_getter = RequestsGetter
        
    @classmethod
    def tearDownClass(cls):
        del cls.phantomjs
        del cls.phantomjs_failure

    def setUp(self):

        self.path : str = os.path.abspath(base_dir) + os.path.sep + 'drivers' + os.path.sep

        self.startTime : float = time.time()

        self.specific_version : str = '2.1.1'
        self.specific_version_failure : str = 'blablablanotversion'

        self.phantomjs_name : str = "phantomjs_test.exe" if platform.system() == 'Windows' else\
                                        "phantomjs_test"

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_current_version_phantomjs(self):
        result, message, current_version = self.phantomjs_failure._PhantomJS__get_current_version_phantomjs()
        self.assertTrue(result, message)
        self.assertGreaterEqual(len(message), 0, len(message))
        self.assertEqual(len(current_version), 0, len(current_version))

    #@unittest.skip('Temporary not needed')
    def test02_check_download_driver(self):
        result, message, current_version = self.phantomjs_failure._PhantomJS__download_driver(version=self.specific_version_failure)
        self.assertFalse(result, message)
        self.assertGreaterEqual(len(message), 0, len(message))
        self.assertEqual(len(current_version), 0, len(current_version))

    #@unittest.skip('Temporary not needed')
    def test03_check_compare_current_version_and_latest_version_failure(self):
        result, message, is_driver_is_up_to_date, current_version, latest_version = self.phantomjs_failure._PhantomJS__compare_current_version_and_latest_version_phantomjs()
        self.assertTrue(result, message)
        self.assertGreaterEqual(len(message), 0, len(message))
        self.assertFalse(is_driver_is_up_to_date, is_driver_is_up_to_date)
        self.assertEqual(len(current_version), 0, len(current_version))
        self.assertEqual(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test04_check_phantomjs_is_up_to_date_failure(self):
        result, message, filename = self.phantomjs_failure.main()
        self.assertFalse(result, result)
        self.assertGreater(len(message), 0, len(message))
        self.assertEqual(len(filename), 0, len(filename))

    #@unittest.skip('Temporary not needed')
    def test05_check_get_latest_version_phantomjs(self):
        result, message, latest_version = self.phantomjs._PhantomJS__get_latest_version_phantomjs()
        self.assertTrue(result, message)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))

        url = self.setting["PhantomJS"]["LinkLastReleaseFile"].format(latest_version)
        result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url, return_text = False)
        self.assertTrue(result, message)
        self.assertEqual(status_code, 200, status_code)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))

    #@unittest.skip('Temporary not needed')
    def test06_check_download_driver_specific_version(self):
        result, message = self.phantomjs._PhantomJS__delete_current_phantomjs_for_current_os()
        self.assertTrue(result, message)
        self.assertFalse(os.path.exists(self.path + self.phantomjs_name), self.path + self.phantomjs_name)

        result, message, file_name = self.phantomjs._PhantomJS__download_driver(version=self.specific_version)
        self.assertTrue(result, message)
        self.assertIsNotNone(file_name,file_name)
        self.assertGreater(len(file_name), 0, len(file_name))
        self.assertTrue(os.path.exists(self.path + self.phantomjs_name), self.path + self.phantomjs_name)

        result, message = self.phantomjs._PhantomJS__chmod_driver()
        self.assertTrue(result, message)

        result, message, current_version = self.phantomjs._PhantomJS__get_current_version_phantomjs()
        self.assertTrue(result, message)
        self.assertIsNotNone(current_version, current_version)
        self.assertGreaterEqual(len(current_version), 0, len(current_version))
        self.assertEqual(current_version, self.specific_version)

    #@unittest.skip('Temporary not needed')
    def test06_check_download_driver_latest_previous_version(self):
        result, message = self.phantomjs._PhantomJS__delete_current_phantomjs_for_current_os()
        self.assertTrue(result, message)
        self.assertFalse(os.path.exists(self.path + self.phantomjs_name), self.path + self.phantomjs_name)

        result, message, file_name = self.phantomjs._PhantomJS__download_driver(previous_version=True)
        self.assertTrue(result, message)
        self.assertIsNotNone(file_name,file_name)
        self.assertGreater(len(file_name), 0, len(file_name))
        self.assertTrue(os.path.exists(self.path + self.phantomjs_name), self.path + self.phantomjs_name)

        result, message = self.phantomjs._PhantomJS__chmod_driver()
        self.assertTrue(result, message)

        result, message, current_version = self.phantomjs._PhantomJS__get_current_version_phantomjs()
        self.assertTrue(result, message)
        self.assertIsNotNone(current_version, current_version)
        self.assertGreaterEqual(len(current_version), 0, len(current_version))


    #@unittest.skip('Temporary not needed')
    def test07_check_download_driver(self):
        result, message, latest_version = self.phantomjs._PhantomJS__get_latest_version_phantomjs()
        self.assertTrue(result, message)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))

        result, message, file_name = self.phantomjs._PhantomJS__download_driver()
        self.assertTrue(result, message)
        self.assertIsNotNone(file_name,file_name)
        self.assertGreater(len(file_name), 0, len(file_name))
        self.assertTrue(os.path.exists(self.path + self.phantomjs_name), self.path + self.phantomjs_name)

        result, message = self.phantomjs._PhantomJS__chmod_driver()
        self.assertTrue(result, message)

    #@unittest.skip('Temporary not needed')
    def test08_check_phantomjs_is_up_to_date_failure(self):
        result, message, filename = self.phantomjs.main()
        self.assertTrue(result, result)
        self.assertEqual(len(message), 0, len(message))
        self.assertGreater(len(filename), 0, len(filename))

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)