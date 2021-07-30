#Standart library imports
import unittest
import time
import os.path
import logging

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))

# Local imports
from selenium_driver_updater.util.requests_getter import RequestsGetter
from selenium_driver_updater.util.github_viewer import GithubViewer
from selenium_driver_updater.util.exceptions import StatusCodeNotEqualException

base_dir = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(level=logging.INFO)

# pylint: disable=missing-function-docstring
class testExceptions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.requests_getter = RequestsGetter
        cls.githubviewer = GithubViewer

    def setUp(self):

        self.start_time : float = time.time()

    def tearDown(self):
        end_time = time.time() - self.start_time
        print("%.3f" % end_time)

    #@unittest.skip('Temporary not needed')
    def test01_check_StatusCodeNotEqualException(self):
        url = 'https://google.com/aboba'
        try:
            json_data = self.requests_getter.get_result_by_request(url=url)
        except Exception as e:
            self.assertTrue(e.__class__ == StatusCodeNotEqualException, e.__class__)


if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)
    