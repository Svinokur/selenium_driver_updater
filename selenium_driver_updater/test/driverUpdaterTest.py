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
from driverUpdater import info

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
        cls.info = info

    def setUp(self):
        self.startTime : float = time.time()

        self.path = base_dir
        self.driver_name = 'chromedriver'
        self.system_name = 'linux64'

        self.driver_name_failure = 'chromedriverabobus'
        self.system_name_failure = 'linux6412312'

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_check_all_input_parameteres_failure(self):
        result, message = self.driver_updater._DriverUpdater__check_all_input_parameteres()
        self.assertFalse(result, message)
        self.assertGreater(len(message), 0, len(message))

    #@unittest.skip('Temporary not needed')
    def test02_check_enviroment_and_variables_failure(self):
        result, message = self.driver_updater._DriverUpdater__check_enviroment_and_variables()
        self.assertFalse(result, message)
        self.assertGreater(len(message), 0, len(message))

    #@unittest.skip('Temporary not needed')
    def test03_check_driver_name_is_valid_failure(self):
        result, message = self.driver_updater._DriverUpdater__check_driver_name_is_valid(driver_name=self.driver_name_failure)
        self.assertFalse(result, message)
        self.assertGreater(len(message), 0, len(message))

    #@unittest.skip('Temporary not needed')
    def test04_check_system_name_is_valid_failure(self):
        result, message = self.driver_updater._DriverUpdater__check_system_name_is_valid(system_name=self.system_name_failure)
        self.assertFalse(result, message)
        self.assertGreater(len(message), 0, len(message))

    #@unittest.skip('Temporary not needed')
    def test05_check_parameter_type_is_valid(self):
        result, message = self.driver_updater._DriverUpdater__check_parameter_type_is_valid(parameter='aboba', needed_type=list, parameter_name='driver_name')
        self.assertFalse(result, message)
        self.assertGreater(len(message), 0, len(message))
    
    #@unittest.skip('Temporary not needed')
    def test06_check_get_result_by_request(self):
        url = str(self.setting["PyPi"]["urlProjectJson"])
        result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertTrue(result, message)
        self.assertEqual(status_code, 200, status_code)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))
    
    #@unittest.skip('Temporary not needed')
    def test07_check_library_is_up_to_date(self):
        info._path = base_dir
        info._driver_name = 'chromedriver'
        info._system_name = 'macos'

        result, message = self.driver_updater._DriverUpdater__check_library_is_up_to_date()
        self.assertTrue(result, message)
    
    #@unittest.skip('Temporary not needed')
    def test08_check_is_python_version_compatible_for_library(self):
        result, message = self.driver_updater._DriverUpdater__check_is_python_version_compatible_for_library()
        self.assertTrue(result, message)

    #@unittest.skip('Temporary not needed')
    def test09_check_all_input_parameteres(self):
        result, message = self.driver_updater._DriverUpdater__check_all_input_parameteres()
        self.assertTrue(result, message)

    #@unittest.skip('Temporary not needed')
    def test10_check_enviroment_and_variables(self):
        result, message = self.driver_updater._DriverUpdater__check_enviroment_and_variables()
        self.assertTrue(result, message)
        
    #@unittest.skip('Temporary not needed')
    def test11_check_driver_name_is_valid(self):
        result, message = self.driver_updater._DriverUpdater__check_driver_name_is_valid(driver_name=self.driver_name)
        self.assertTrue(result, message)

    #@unittest.skip('Temporary not needed')
    def test12_check_system_name_is_valid(self):
        result, message = self.driver_updater._DriverUpdater__check_system_name_is_valid(system_name=self.system_name)
        self.assertTrue(result, message)

    #@unittest.skip('Temporary not needed')
    def test13_check_parameter_type_is_valid(self):
        result, message = self.driver_updater._DriverUpdater__check_parameter_type_is_valid(parameter=self.driver_name, needed_type=str, parameter_name='driver_name')
        self.assertTrue(result, message)
    
    
if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)