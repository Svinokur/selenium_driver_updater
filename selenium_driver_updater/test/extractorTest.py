import unittest

import sys
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from util.extractor import Extractor
import time
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

import shutil

import logging
logging.basicConfig(level=logging.INFO)

from pathlib import Path

class testExtractor(unittest.TestCase): 
    """Class for unit-testing Extractor class

    Attributes:
        extractor                   : Initialize class Extractor
        out_path (str)              : Specific path where test archive located
        zip_archive_path (str)      : Path to test zip archive
        tar_archive_path (str)      : Path to test tar archive
        startTime (float)           : Time of starting unit-tests
    """

    @classmethod
    def setUpClass(cls):
        cls.extractor = Extractor

    def setUp(self):
        self.out_path : str = base_dir + os.path.sep + 'archive' + os.path.sep
        self.zip_archive_path : str = self.out_path + 'geckodriver-v0.29.0-win64.zip'
        self.tar_archive_path : str = self.out_path + 'geckodriver-v0.29.1-macos-aarch64.tar.gz'
        self.tar_bz2_archive_path : str = self.out_path + 'phantomjs-2.1.1-linux-x86_64.tar.bz2'
        self.startTime : float = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_check_extract_all_zip_archive_failure(self):
        result, message = self.extractor.extract_all_zip_archive(archive_path= self.out_path,out_path=self.out_path)
        self.assertFalse(result, message)
        self.assertGreater(len(message), 0, len(message))

    #@unittest.skip('Temporary not needed')
    def test02_check_extract_all_tar_gz_archive_failure(self):
        result, message = self.extractor.extract_all_tar_gz_archive(archive_path= self.out_path,out_path=self.out_path)
        self.assertFalse(result, message)
        self.assertGreater(len(message), 0, len(message))

    #@unittest.skip('Temporary not needed')
    def test03_check_extract_all_zip_archive_with_specific_name_failure(self):
        result, message = self.extractor.extract_all_zip_archive_with_specific_name(archive_path= self.out_path,out_path=self.out_path, delete_archive = False,
        filename = 'geckodriver.exe', filename_replace = 'geckodriverzip')
        self.assertFalse(result, message)
        self.assertGreater(len(message), 0, len(message))

    #@unittest.skip('Temporary not needed')
    def test04_check_extract_all_tar_archive_with_specific_name_failure(self):
        result, message = Extractor.extract_all_zip_archive_with_specific_name(archive_path= self.out_path,out_path=self.out_path, delete_archive = False,
        filename = 'geckodriver', filename_replace = 'geckodrivertar')
        self.assertFalse(result, message)
        self.assertGreater(len(message), 0, len(message))

    #@unittest.skip('Temporary not needed')
    def test05_check_extract_all_zip_archive(self):
        result, message = self.extractor.extract_all_zip_archive(archive_path=self.zip_archive_path,out_path=self.out_path, delete_archive = False)
        self.assertTrue(result, message)

        geckodriver_path = self.out_path + 'geckodriver.exe'
        self.assertTrue(Path(geckodriver_path).exists())
        Path(geckodriver_path).unlink()
        self.assertFalse(Path(geckodriver_path).exists())
    
    #@unittest.skip('Temporary not needed')
    def test06_check_extract_all_tar_gz_archive(self):
        result, message = self.extractor.extract_all_tar_gz_archive(archive_path=self.tar_archive_path,out_path=self.out_path, delete_archive = False)
        self.assertTrue(result, message)

        geckodriver_path = self.out_path + 'geckodriver'
        self.assertTrue(Path(geckodriver_path).exists())
        Path(geckodriver_path).unlink()
        self.assertFalse(Path(geckodriver_path).exists())
    
    #@unittest.skip('Temporary not needed')
    def test07_check_extract_all_zip_archive_with_specific_name(self):
        result, message = self.extractor.extract_all_zip_archive_with_specific_name(archive_path=self.zip_archive_path,out_path=self.out_path, delete_archive = False,
        filename = 'geckodriver.exe', filename_replace = 'geckodriverzip')
        self.assertTrue(result, message)

        geckodriver_path = self.out_path + 'geckodriverzip'
        self.assertTrue(Path(geckodriver_path).exists())
        Path(geckodriver_path).unlink()
        self.assertFalse(Path(geckodriver_path).exists())
    
    #@unittest.skip('Temporary not needed')
    def test08_check_extract_all_tar_archive_with_specific_name(self):
        result, message = Extractor.extract_all_zip_archive_with_specific_name(archive_path=self.tar_archive_path,out_path=self.out_path, delete_archive = False,
        filename = 'geckodriver', filename_replace = 'geckodrivertar')
        self.assertTrue(result, message)

        geckodriver_path = self.out_path + 'geckodrivertar'
        self.assertTrue(Path(geckodriver_path).exists())
        Path(geckodriver_path).unlink()
        self.assertFalse(Path(geckodriver_path).exists())

    #@unittest.skip('Temporary not needed')
    def test09_check_extract_all_tar_bz2_archive(self):
        result, message = Extractor.extract_all_tar_bz2_archive(archive_path=self.tar_bz2_archive_path,out_path=self.out_path, delete_archive = False)
        self.assertTrue(result, message)

        phantom_path = self.out_path + 'phantomjs-2.1.1-linux-x86_64'
        self.assertTrue(Path(phantom_path).exists())
        shutil.rmtree(phantom_path)
        self.assertFalse(Path(phantom_path).exists())
    
    
if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)