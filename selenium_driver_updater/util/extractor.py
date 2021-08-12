#Standart library imports
import zipfile
import os
import shutil
from shutil import copyfile
from pathlib import Path

# Third party imports
import tarfile

#Local imports
from selenium_driver_updater.util.logger import logger
from selenium_driver_updater.util.exceptions import UnknownArchiveFormatException

class Extractor():
    """Class for working with different archive types"""

    @staticmethod
    def extract_all_zip_archive(
        archive_path: str,
        out_path: str, delete_archive: bool = True
        ) -> None:
        """Extract all members in specific zip archive

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        """

        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(out_path)

        if Path(archive_path).exists() and delete_archive:
            Path(archive_path).unlink()


    @staticmethod
    def extract_all_tar_gz_archive(
        archive_path: str,
        out_path: str, delete_archive: bool = True
        ) -> None:
        """Extract all members in specific tar.gz archive

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        """

        with tarfile.open(archive_path, "r:gz") as tar_ref:
            tar_ref.extractall(out_path)

        if Path(archive_path).exists() and delete_archive:
            Path(archive_path).unlink()

    @staticmethod
    def extract_all_zip_archive_with_specific_name(
        archive_path: str, out_path: str, filename: str,
        filename_replace: str, delete_archive : bool = True
        ) -> None:
        """Extract all zip archive and replaces name for one of member

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            filename (str)          : Archive member whose name will be changed.
            filename_replace (str)  : Specific name for replacing.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        """

        driver_folder_path = out_path + 'tmp'
        message = ('Created new safety directory for replacing'
                    f'filename: {filename} filename_replace: {filename_replace}')
        logger.info(message)

        if os.path.exists(driver_folder_path):
            shutil.rmtree(driver_folder_path)

        parameters = dict(
            archive_path=archive_path,out_path=driver_folder_path, delete_archive=delete_archive
            )

        if archive_path.endswith('.tar.gz'):

            Extractor.extract_all_tar_gz_archive(**parameters)

        elif archive_path.endswith('.zip'):

            Extractor.extract_all_zip_archive(**parameters)

        else:
            message = f'Unknown archive format was specified archive_path: {archive_path}'
            raise UnknownArchiveFormatException(message)

        old_path = driver_folder_path + os.path.sep + filename
        new_path = driver_folder_path + os.path.sep + filename_replace

        os.rename(old_path, new_path)

        renamed_driver_path = out_path + filename_replace
        if Path(renamed_driver_path).exists():
            Path(renamed_driver_path).unlink()

        copyfile(new_path, renamed_driver_path)

        if Path(driver_folder_path).exists():
            shutil.rmtree(driver_folder_path)

    @staticmethod
    def extract_all_tar_bz2_archive(archive_path: str,
                                    out_path: str, delete_archive: bool = True) -> None:
        """Extract all members in specific tar.bz2 archive

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        """

        with tarfile.open(archive_path, "r:bz2") as tar_ref:
            tar_ref.extractall(out_path)

        if Path(archive_path).exists() and delete_archive:
            Path(archive_path).unlink()

    @staticmethod
    def extract_all_tar_xz_archive(archive_path: str,
                                    out_path: str, delete_archive: bool = True) -> None:
        """Extract all members in specific tar.xz archive

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        """

        with tarfile.open(archive_path, "r:xz") as tar_ref:
            tar_ref.extractall(out_path)

        if Path(archive_path).exists() and delete_archive:
            Path(archive_path).unlink()

    @staticmethod
    def extract_and_detect_archive_format(
        archive_path: str,
        out_path: str, delete_archive: bool = True
        ) -> None:
        """Extract and automatic detects archive path format

        Args:
            archive_path (str)      : Path to specific archive.
            out_path (str)          : Out path, where all members of archive will be gathered.
            delete_archive (bool)   : Delete archive after unzip or not. Defaults to True.

        """

        parameters = dict(
            archive_path=archive_path, out_path=out_path, delete_archive=delete_archive
            )

        if archive_path.endswith('.zip'):

            Extractor.extract_all_zip_archive(**parameters)

        elif archive_path.endswith('.tar.gz'):

            Extractor.extract_all_tar_gz_archive(**parameters)

        elif archive_path.endswith('.tar.bz2'):

            Extractor.extract_all_tar_bz2_archive(**parameters)

        else:
            message = f'Unknown archive format was specified archive_path: {archive_path}'
            raise UnknownArchiveFormatException(message)
        