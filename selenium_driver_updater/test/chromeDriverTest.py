import unittest

import sys
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from _setting import setting
from chromeDriver import ChromeDriver
import time
import requests
#from ..chromeDriver import ChromeDriver

base_dir = os.path.dirname(os.path.abspath(__file__))

class testChromeDriver(unittest.TestCase): 
    """Class for unit-testing ChromeDriver class

    Attributes:
        chrome_driver       : Initialize class ChromeDriver
        startTime (float)   : Time of starting unit-tests
        setting (dict[str]) : Dict of all additional parametres

    """

    def setUp(self):
        path = os.path.abspath(base_dir) + os.path.sep + 'drivers' + os.path.sep
        
        self.chrome_driver = ChromeDriver(path=path, upgrade=True, chmod=True, 
        check_driver_is_up_to_date = True, info_messages=True, filename='chromedriver_test', version='', 
        check_browser_is_up_to_date = False)

        self.startTime : float = time.time()
        self.setting = setting

        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/35.0.1916.47 Safari/537.36'

        self.headers = {'User-Agent': user_agent}

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_get_result_by_request(self):
        request = requests.get(self.setting["ChromeDriver"]["LinkLastRelease"], headers=self.headers)
        status_code = request.status_code
        request_text = request.text
        self.assertEqual(status_code, 200, status_code)
        self.assertGreater(len(request_text), 0, request_text)

    #@unittest.skip('Temporary not needed')
    def test02_get_result_by_request(self):
        request = requests.get(self.setting["ChromeBrowser"]["LinkAllLatestRelease"], headers=self.headers)
        status_code = request.status_code
        request_text = request.text
        self.assertEqual(status_code, 200, status_code)
        self.assertGreater(len(request_text), 0, request_text)

    #@unittest.skip('Temporary not needed')
    def test03_check_if_chromedriver_is_up_to_date(self):
        result, message, filename = self.chrome_driver.main()
        self.assertTrue(result, message)
        self.assertGreater(len(filename), 0, len(filename))
        


if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)