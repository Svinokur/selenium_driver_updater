import traceback
import logging
from typing import Tuple
import zipfile
import os
import shutil
from shutil import copyfile
import tarfile

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

class Extractor():

    @staticmethod
    def extract_all_zip_archive(archive_path : str, out_path : str, delete_archive : bool = True) -> Tuple[bool, str]:
        """Extract all members in specific zip archive

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
        """
        result_run : bool = False
        message_run : str = '' 
        try:

            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(out_path)

            if os.path.exists(archive_path) and delete_archive:
                os.remove(archive_path)

            result_run = True

        except:

            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
    
    @staticmethod
    def extract_all_tar_gz_archive(archive_path : str, out_path : str, delete_archive : bool = True) -> Tuple[bool, str]:
        """Extract all members in specific tar.gz archive

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
        """
        result_run : bool = False
        message_run : str = '' 
        try:

            with tarfile.open(archive_path, "r:gz") as tar_ref:
                tar_ref.extractall(out_path)

            if os.path.exists(archive_path) and delete_archive:
                os.remove(archive_path)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    @staticmethod
    def extract_all_zip_archive_with_specific_name(archive_path : str, out_path : str, filename : str, filename_replace : str, delete_archive : bool = True) -> Tuple[bool, str]:
        """Extract all zip archive and replaces name for one of member

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            filename (str)          : Archive member whose name will be changed.
            filename_replace (str)  : Specific name for replacing.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
        """
        result_run : bool = False
        message_run : str = '' 
        try:

            driver_folder_path = out_path + 'tmp'
            logging.info(f'Created new safety directory for replacing filename: {filename} filename_replace: {filename_replace}')

            if os.path.exists(driver_folder_path):
                shutil.rmtree(driver_folder_path)

            if archive_path.endswith('.tar.gz'):

                result, message = Extractor.extract_all_tar_gz_archive(archive_path=archive_path, out_path=driver_folder_path, delete_archive=delete_archive)
                if not result:
                    return result, message

            elif archive_path.endswith('.zip'):

                result, message = Extractor.extract_all_zip_archive(archive_path=archive_path, out_path=driver_folder_path, delete_archive=delete_archive)
                if not result:
                    return result, message

            else:
                message = f'Unknown archive format was specified archive_path: {archive_path}'
                logging.error(message)
                return result_run, message

            old_path = driver_folder_path + os.path.sep + filename
            new_path = driver_folder_path + os.path.sep + filename_replace

            os.rename(old_path, new_path)

            renamed_driver_path = out_path + filename_replace
            if os.path.exists(renamed_driver_path):
                os.remove(renamed_driver_path)

            copyfile(new_path, renamed_driver_path)

            if os.path.exists(driver_folder_path):
                shutil.rmtree(driver_folder_path)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    @staticmethod
    def extract_all_tar_bz2_archive(archive_path : str, out_path : str, delete_archive : bool = True) -> Tuple[bool, str]:
        """Extract all members in specific tar.bz2 archive

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
        """
        result_run : bool = False
        message_run : str = '' 
        try:

            with tarfile.open(archive_path, "r:bz2") as tar_ref:
                tar_ref.extractall(out_path)

            if os.path.exists(archive_path) and delete_archive:
                os.remove(archive_path)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run