import unittest

import sys
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from driverUpdater import DriverUpdater
from _setting import setting
import time
import os
from util.requests_getter import RequestsGetter

base_dir = os.path.dirname(os.path.abspath(__file__))

import logging
logging.basicConfig(level=logging.INFO)

class testDriverUpdater(unittest.TestCase): 
    """Class for unit-testing DriverUpdater class

    Attributes:
        startTime (float) : Time of starting unit-tests
    """

    @classmethod
    def setUpClass(cls):
        cls.setting = setting

        cls.driver_updater = DriverUpdater
        cls.requests_getter = RequestsGetter

    def setUp(self):
        self.startTime : float = time.time()

        self.path = base_dir
        self.driver_name = 'chromedriver'

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_check_all_input_parameteres_failure(self):
        result, message = self.driver_updater._DriverUpdater__check_all_input_parameteres(path=self.path + 'hahaha', driver_name=self.driver_name, filename='hi')
        self.assertFalse(result, message)
        self.assertGreater(len(message), 0, len(message))

    #@unittest.skip('Temporary not needed')
    def test02_check_enviroment_and_variables_failure(self):
        result, message = self.driver_updater._DriverUpdater__check_enviroment_and_variables(path=self.path + 'hahaha', driver_name=self.driver_name, enable_library_update_check=True, filename='hi')
        self.assertFalse(result, message)
        self.assertGreater(len(message), 0, len(message))
    
    #@unittest.skip('Temporary not needed')
    def test03_check_get_result_by_request(self):
        url = self.setting["PyPi"]["urlProjectJson"]
        result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertTrue(result, message)
        self.assertEqual(status_code, 200, status_code)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))
    
    #@unittest.skip('Temporary not needed')
    def test04_check_library_is_up_to_date(self):
        result, message = self.driver_updater._DriverUpdater__check_library_is_up_to_date()
        self.assertTrue(result, message)
    
    #@unittest.skip('Temporary not needed')
    def test05_check_is_python_version_compatible_for_library(self):
        result, message = self.driver_updater._DriverUpdater__check_is_python_version_compatible_for_library()
        self.assertTrue(result, message)

    #@unittest.skip('Temporary not needed')
    def test06_check_all_input_parameteres(self):
        result, message = self.driver_updater._DriverUpdater__check_all_input_parameteres(path=self.path, driver_name=self.driver_name, filename=self.driver_name)
        self.assertTrue(result, message)

    #@unittest.skip('Temporary not needed')
    def test07_check_enviroment_and_variables(self):
        result, message = self.driver_updater._DriverUpdater__check_enviroment_and_variables(path=self.path, driver_name=self.driver_name, enable_library_update_check=True, filename=self.driver_name)
        self.assertTrue(result, message)
    
    
if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)