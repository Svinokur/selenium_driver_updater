#Standart library imports
import unittest
import os.path
import time
import logging

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))

# Local imports
from selenium_driver_updater.driverUpdater import DriverUpdater
from selenium_driver_updater.driverUpdater import _info

from selenium_driver_updater._setting import setting
from selenium_driver_updater.util.requests_getter import RequestsGetter

base_dir = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(level=logging.INFO)

# pylint: disable=missing-function-docstring
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
        cls.info = _info

    def setUp(self):
        self.start_time : float = time.time()

        self.path = base_dir
        self.driver_name = 'chromedriver'
        self.system_name = 'linux64'

        self.driver_name_failure = 'chromedriverabobus'
        self.system_name_failure = 'linux6412312'

    def tearDown(self):
        end_time = time.time() - self.start_time
        print("%.3f" % end_time)

    #@unittest.skip('Temporary not needed')
    def test01_check_all_input_parameteres_failure(self):
        try:
            self.driver_updater._DriverUpdater__check_all_input_parameteres()
        except Exception as e:
            self.assertTrue(e.__class__ == ValueError, e.__class__)

    #@unittest.skip('Temporary not needed')
    def test02_check_enviroment_and_variables_failure(self):
        try:
            self.driver_updater._DriverUpdater__check_enviroment_and_variables()
        except Exception as e:
            self.assertTrue(e.__class__ == ValueError, e.__class__)

    #@unittest.skip('Temporary not needed')
    def test03_check_driver_name_is_valid_failure(self):
        try:
            self.driver_updater._DriverUpdater__check_driver_name_is_valid(driver_name=self.driver_name_failure)
        except Exception as e:
            self.assertTrue(e.__class__ == ValueError, e.__class__)

    #@unittest.skip('Temporary not needed')
    def test04_check_system_name_is_valid_failure(self):
        try:
            self.driver_updater._DriverUpdater__check_system_name_is_valid(system_name=self.system_name_failure)
        except Exception as e:
            self.assertTrue(e.__class__ == ValueError, e.__class__)

    #@unittest.skip('Temporary not needed')
    def test05_check_parameter_type_is_valid(self):
        try:
            self.driver_updater._DriverUpdater__check_parameter_type_is_valid(parameter='aboba', needed_type=list, parameter_name='driver_name')
        except Exception as e:
            self.assertTrue(e.__class__ == TypeError, e.__class__)

    #@unittest.skip('Temporary not needed')
    def test06_check_get_result_by_request(self):
        url = str(self.setting["PyPi"]["urlProjectJson"])
        json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))

    #@unittest.skip('Temporary not needed')
    def test07_check_library_is_up_to_date(self):
        self.info.path = base_dir
        self.info.driver_name = 'chromedriver'
        self.info.system_name = 'mac64'

        self.driver_updater._DriverUpdater__check_library_is_up_to_date()

    #@unittest.skip('Temporary not needed')
    def test08_check_is_python_version_compatible_for_library(self):
        self.driver_updater._DriverUpdater__check_is_python_version_compatible_for_library()

    #@unittest.skip('Temporary not needed')
    def test09_check_all_input_parameteres(self):
        self.driver_updater._DriverUpdater__check_all_input_parameteres()

    #@unittest.skip('Temporary not needed')
    def test10_check_enviroment_and_variables(self):
        self.driver_updater._DriverUpdater__check_enviroment_and_variables()

    #@unittest.skip('Temporary not needed')
    def test11_check_driver_name_is_valid(self):
        self.driver_updater._DriverUpdater__check_driver_name_is_valid(driver_name=self.driver_name)

    #@unittest.skip('Temporary not needed')
    def test12_check_system_name_is_valid(self):
        self.driver_updater._DriverUpdater__check_system_name_is_valid(system_name=self.system_name)

    #@unittest.skip('Temporary not needed')
    def test13_check_parameter_type_is_valid(self):
        self.driver_updater._DriverUpdater__check_parameter_type_is_valid(parameter=self.driver_name, needed_type=str, parameter_name='driver_name')


if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)
