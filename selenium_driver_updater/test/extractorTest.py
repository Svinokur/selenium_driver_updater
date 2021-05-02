import unittest

import sys
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from util.extractor import Extractor
import time
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

class testExtractor(unittest.TestCase): 
    """Class for unit-testing Extractor class

    Attributes:
        extractor                   : Initialize class Extractor
        out_path (str)              : Specific path where test archive located
        zip_archive_path (str)      : Path to test zip archive
        tar_archive_path (str)      : Path to test tar archive
        startTime (float)           : Time of starting unit-tests
    """

    def setUp(self):
        self.extractor = Extractor
        self.out_path : str = base_dir + os.path.sep + 'archive' + os.path.sep
        self.zip_archive_path : str = base_dir + os.path.sep + 'archive' + os.path.sep + 'geckodriver-v0.29.0-win64.zip'
        self.tar_archive_path : str = base_dir + os.path.sep + 'archive' + os.path.sep + 'geckodriver-v0.29.1-macos-aarch64.tar.gz'
        self.startTime : float = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_check_extract_all_zip_archive(self):
        result, message = Extractor.extract_all_zip_archive(archive_path=self.zip_archive_path,out_path=self.out_path, delete_archive = False)
        self.assertTrue(result, message)

        geckodriver_path = self.out_path + 'geckodriver.exe'
        self.assertTrue(os.path.exists(geckodriver_path))
        os.remove(geckodriver_path)
        self.assertFalse(os.path.exists(geckodriver_path))
    
    #@unittest.skip('Temporary not needed')
    def test02_check_extract_all_tar_gz_archive(self):
        result, message = Extractor.extract_all_tar_gz_archive(archive_path=self.tar_archive_path,out_path=self.out_path, delete_archive = False)
        self.assertTrue(result, message)

        geckodriver_path = self.out_path + 'geckodriver'
        self.assertTrue(os.path.exists(geckodriver_path))
        os.remove(geckodriver_path)
        self.assertFalse(os.path.exists(geckodriver_path))
    
    #@unittest.skip('Temporary not needed')
    def test03_check_extract_all_zip_archive_with_specific_name(self):
        result, message = Extractor.extract_all_zip_archive_with_specific_name(archive_path=self.zip_archive_path,out_path=self.out_path, delete_archive = False,
        filename = 'geckodriver.exe', filename_replace = 'geckodriverzip')
        self.assertTrue(result, message)

        geckodriver_path = self.out_path + 'geckodriverzip'
        self.assertTrue(os.path.exists(geckodriver_path))
        os.remove(geckodriver_path)
        self.assertFalse(os.path.exists(geckodriver_path))
    
    #@unittest.skip('Temporary not needed')
    def test04_check_extract_all_tar_archive_with_specific_name(self):
        result, message = Extractor.extract_all_zip_archive_with_specific_name(archive_path=self.tar_archive_path,out_path=self.out_path, delete_archive = False,
        filename = 'geckodriver', filename_replace = 'geckodrivertar')
        self.assertTrue(result, message)

        geckodriver_path = self.out_path + 'geckodrivertar'
        self.assertTrue(os.path.exists(geckodriver_path))
        os.remove(geckodriver_path)
        self.assertFalse(os.path.exists(geckodriver_path))
    
    
if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)