import unittest

import sys
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from setting import setting
from edgeDriver import EdgeDriver
import time

base_dir = os.path.dirname(os.path.abspath(__file__))

class testEdgeDriver(unittest.TestCase): 
    """Class for unit-testing EdgeDriver class

    Attributes:
        edge_driver         : Initialize class EdgeDriver
        startTime (float)   : Time of starting unit-tests
        setting (dict[str]) : Dict of all additional parametres

    """

    def setUp(self):
        path = os.path.abspath(base_dir) + os.path.sep + 'drivers' + os.path.sep

        self.edge_driver = EdgeDriver(path=path, upgrade=True, chmod=True, 
        check_driver_is_up_to_date = True, info_messages=True, filename='edgedriver_test', version='')
        self.startTime : float = time.time()
        self.setting = setting

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_check_if_edgedriver_is_up_to_date(self):
        result, message, filename = self.edge_driver.main()
        self.assertTrue(result, message)
        self.assertGreater(len(filename), 0, len(filename))
        


if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)