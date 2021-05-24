import unittest

import sys
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from util.requests_getter import RequestsGetter
from _setting import setting

import time

import logging
logging.basicConfig(level=logging.INFO)

class testRequestsGetter(unittest.TestCase): 
    """Class for unit-testing RequestsGetter class

    Attributes:
        requests_getter             : Initialize class RequestsGetter
        setting (dict[str])     : Dict of all additional parametres
        startTime (float)           : Time of starting unit-tests
    """

    @classmethod
    def setUpClass(cls):
        cls.setting = setting
        cls.requests_getter = RequestsGetter

    def setUp(self):

        self.startTime : float = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_result_by_request_failure(self):
        url = 'hi'
        result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertFalse(result, json_data)
        self.assertGreater(len(message), 0, len(message))
        self.assertNotEqual(status_code, 200, status_code)
    
    #@unittest.skip('Temporary not needed')
    def test02_check_get_result_by_request(self):
        url = self.setting["ChromeDriver"]["LinkLastRelease"]
        result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertTrue(result, message)
        self.assertEqual(status_code, 200, status_code)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)