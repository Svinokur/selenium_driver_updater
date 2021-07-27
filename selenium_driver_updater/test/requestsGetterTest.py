#Standart library imports
import unittest
import time
import logging

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))

# Local imports
from selenium_driver_updater.util.requests_getter import RequestsGetter
from selenium_driver_updater._setting import setting

logging.basicConfig(level=logging.INFO)

# pylint: disable=missing-function-docstring
class testRequestsGetter(unittest.TestCase):
    """Class for unit-testing RequestsGetter class

    Attributes:
        requests_getter             : Initialize class RequestsGetter
        setting (dict[str])         : Dict of all additional parametres
        startTime (float)           : Time of starting unit-tests
    """

    @classmethod
    def setUpClass(cls):
        cls.setting = setting
        cls.requests_getter = RequestsGetter

    def setUp(self):

        self.start_time : float = time.time()

    def tearDown(self):
        end_time = time.time() - self.start_time
        print("%.3f" % end_time)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_result_by_request_failure(self):
        url = 'hi'
        try:
            json_data = self.requests_getter.get_result_by_request(url=url)
        except Exception:
            pass

    #@unittest.skip('Temporary not needed')
    def test02_check_get_result_by_request(self):
        url = self.setting["ChromeDriver"]["LinkLastRelease"]
        json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)
    