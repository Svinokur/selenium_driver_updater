#Standart library imports
import traceback
import logging
import zipfile
import os
import shutil
from shutil import copyfile
from typing import Tuple
from pathlib import Path

# Third party imports
import tarfile

class Extractor():
    """Class for working with different archive types"""

    @staticmethod
    def extract_all_zip_archive(
        archive_path: str,
        out_path: str, delete_archive: bool = True
        ) -> Tuple[bool, str]:
        """Extract all members in specific zip archive

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        Returns:
            Tuple of bool and str

            result_run (bool) : True if function passed correctly, False otherwise.
            message_run (str) : Returns an error message if an error occurs in the function.
        """
        result_run: bool = False
        message_run: str = ''
        try:

            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(out_path)

            if Path(archive_path).exists() and delete_archive:
                Path(archive_path).unlink()

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    @staticmethod
    def extract_all_tar_gz_archive(
        archive_path: str,
        out_path: str, delete_archive: bool = True
        ) -> Tuple[bool, str]:
        """Extract all members in specific tar.gz archive

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        Returns:
            Tuple of bool and str

            result_run (bool) : True if function passed correctly, False otherwise.
            message_run (str) : Returns an error message if an error occurs in the function.
        """
        result_run: bool = False
        message_run: str = ''
        try:

            with tarfile.open(archive_path, "r:gz") as tar_ref:
                tar_ref.extractall(out_path)

            if Path(archive_path).exists() and delete_archive:
                Path(archive_path).unlink()

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    @staticmethod
    def extract_all_zip_archive_with_specific_name(
        archive_path: str, out_path: str, filename: str,
        filename_replace: str, delete_archive : bool = True
        ) -> Tuple[bool, str]:
        """Extract all zip archive and replaces name for one of member

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            filename (str)          : Archive member whose name will be changed.
            filename_replace (str)  : Specific name for replacing.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        Returns:
            Tuple of bool and str

            result_run (bool) : True if function passed correctly, False otherwise.
            message_run (str) : Returns error message if error was caused.
        """
        result_run: bool = False
        message_run: str = ''
        try:

            driver_folder_path = out_path + 'tmp'
            message = ('Created new safety directory for replacing'
                        f'filename: {filename} filename_replace: {filename_replace}')
            logging.info(message)

            if os.path.exists(driver_folder_path):
                shutil.rmtree(driver_folder_path)

            parameters = dict(
                archive_path=archive_path,out_path=driver_folder_path, delete_archive=delete_archive
                )

            if archive_path.endswith('.tar.gz'):

                result, message = Extractor.extract_all_tar_gz_archive(**parameters)
                if not result:
                    return result, message

            elif archive_path.endswith('.zip'):

                result, message = Extractor.extract_all_zip_archive(**parameters)
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
            if Path(renamed_driver_path).exists():
                Path(renamed_driver_path).unlink()

            copyfile(new_path, renamed_driver_path)

            if Path(driver_folder_path).exists():
                shutil.rmtree(driver_folder_path)

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    @staticmethod
    def extract_all_tar_bz2_archive(archive_path: str,
                                    out_path: str, delete_archive: bool = True) -> Tuple[bool, str]:
        """Extract all members in specific tar.bz2 archive

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        Returns:
            Tuple of bool and str

            result_run (bool) : True if function passed correctly, False otherwise.
            message_run (str) : Returns an error message if an error occurs in the function.
        """
        result_run: bool = False
        message_run: str = ''
        try:

            with tarfile.open(archive_path, "r:bz2") as tar_ref:
                tar_ref.extractall(out_path)

            if Path(archive_path).exists() and delete_archive:
                Path(archive_path).unlink()

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    @staticmethod
    def extract_and_detect_archive_format(
        archive_path: str,
        out_path: str, delete_archive: bool = True
        ) -> Tuple[bool, str]:
        """Extract and automatic detects archive path format

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        Returns:
            Tuple of bool and str

            result_run (bool) : True if function passed correctly, False otherwise.
            message_run (str) : Returns an error message if an error occurs in the function.
        """
        result_run: bool = False
        message_run: str = ''
        try:

            parameters = dict(
                archive_path=archive_path, out_path=out_path, delete_archive=delete_archive
                )

            if archive_path.endswith('.zip'):

                result, message = Extractor.extract_all_zip_archive(**parameters)
                if not result:
                    logging.error(message)
                    return result, message

            elif archive_path.endswith('.tar.gz'):

                result, message = Extractor.extract_all_tar_gz_archive(**parameters)
                if not result:
                    logging.error(message)
                    return result, message

            elif archive_path.endswith('.tar.bz2'):

                result, message = Extractor.extract_all_tar_bz2_archive(**parameters)
                if not result:
                    logging.error(message)
                    return result, message

            else:
                message = f'Unknown archive format was specified archive_path: {archive_path}'
                logging.error(message)
                return result_run, message

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
        