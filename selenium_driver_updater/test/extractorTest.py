#pylint: disable=broad-except
#Standart library imports
import unittest
import time
import os.path
import shutil
import logging
from pathlib import Path

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))

# Local imports
from selenium_driver_updater.util.extractor import Extractor

base_dir = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(level=logging.INFO)

# pylint: disable=missing-function-docstring
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

        self.start_time : float = time.time()

    def tearDown(self):
        end_time = time.time() - self.start_time
        print("%.3f" % end_time)

    #@unittest.skip('Temporary not needed')
    def test01_check_extract_all_zip_archive_failure(self):
        try:
            self.extractor.extract_all_zip_archive(archive_path= self.out_path,out_path=self.out_path)
        except Exception:
            pass

    #@unittest.skip('Temporary not needed')
    def test02_check_extract_all_tar_gz_archive_failure(self):
        try:
            self.extractor.extract_all_tar_gz_archive(archive_path= self.out_path,out_path=self.out_path)
        except Exception:
            pass

    #@unittest.skip('Temporary not needed')
    def test03_check_extract_all_zip_archive_with_specific_name_failure(self):
        try:
            self.extractor.extract_all_zip_archive_with_specific_name(archive_path= self.out_path,out_path=self.out_path, delete_archive = False,
            filename = 'geckodriver.exe', filename_replace = 'geckodriverzip')
        except Exception:
            pass

    #@unittest.skip('Temporary not needed')
    def test04_check_extract_all_tar_archive_with_specific_name_failure(self):
        try:
            Extractor.extract_all_zip_archive_with_specific_name(archive_path= self.out_path,out_path=self.out_path, delete_archive = False,
            filename = 'geckodriver', filename_replace = 'geckodrivertar')
        except Exception:
            pass

    #@unittest.skip('Temporary not needed')
    def test05_check_extract_all_zip_archive(self):
        self.extractor.extract_all_zip_archive(archive_path=self.zip_archive_path,out_path=self.out_path, delete_archive = False)

        geckodriver_path = self.out_path + 'geckodriver.exe'
        self.assertTrue(Path(geckodriver_path).exists())
        Path(geckodriver_path).unlink()
        self.assertFalse(Path(geckodriver_path).exists())

    #@unittest.skip('Temporary not needed')
    def test06_check_extract_all_tar_gz_archive(self):
        self.extractor.extract_all_tar_gz_archive(archive_path=self.tar_archive_path,out_path=self.out_path, delete_archive = False)

        geckodriver_path = self.out_path + 'geckodriver'
        self.assertTrue(Path(geckodriver_path).exists())
        Path(geckodriver_path).unlink()
        self.assertFalse(Path(geckodriver_path).exists())

    #@unittest.skip('Temporary not needed')
    def test07_check_extract_all_zip_archive_with_specific_name(self):
        self.extractor.extract_all_zip_archive_with_specific_name(archive_path=self.zip_archive_path,out_path=self.out_path, delete_archive = False,
        filename = 'geckodriver.exe', filename_replace = 'geckodriverzip')

        geckodriver_path = self.out_path + 'geckodriverzip'
        self.assertTrue(Path(geckodriver_path).exists())
        Path(geckodriver_path).unlink()
        self.assertFalse(Path(geckodriver_path).exists())

    #@unittest.skip('Temporary not needed')
    def test08_check_extract_all_tar_archive_with_specific_name(self):
        Extractor.extract_all_zip_archive_with_specific_name(archive_path=self.tar_archive_path,out_path=self.out_path, delete_archive = False,
        filename = 'geckodriver', filename_replace = 'geckodrivertar')

        geckodriver_path = self.out_path + 'geckodrivertar'
        self.assertTrue(Path(geckodriver_path).exists())
        Path(geckodriver_path).unlink()
        self.assertFalse(Path(geckodriver_path).exists())

    #@unittest.skip('Temporary not needed')
    def test09_check_extract_all_tar_bz2_archive(self):
        Extractor.extract_all_tar_bz2_archive(archive_path=self.tar_bz2_archive_path,out_path=self.out_path, delete_archive = False)

        phantom_path = self.out_path + 'phantomjs-2.1.1-linux-x86_64'
        self.assertTrue(Path(phantom_path).exists())
        shutil.rmtree(phantom_path)
        self.assertFalse(Path(phantom_path).exists())


if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)
    