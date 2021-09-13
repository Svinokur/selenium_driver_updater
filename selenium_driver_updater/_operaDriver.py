#pylint: disable=logging-fstring-interpolation
#Standart library imports
import shutil
import os
import time
from shutil import copyfile
from pathlib import Path
import re

# Third party imports
import wget

# Local imports
from selenium_driver_updater.util.logger import logger

from selenium_driver_updater.browsers._operaBrowser import OperaBrowser

from selenium_driver_updater.util.exceptions import DriverVersionInvalidException

from selenium_driver_updater.driver_base import DriverBase

class OperaDriver(DriverBase):
    """Class for working with Selenium operadriver binary"""

    _repo_name = 'operasoftware/operachromiumdriver'

    def __init__(self, **kwargs):

        kwargs.update(repo_name=OperaDriver._repo_name)

        DriverBase.__init__(self, **kwargs)

        self.system_name = ''

        #assign of specific os
        specific_system = str(kwargs.get('system_name', ''))
        specific_system = specific_system.replace('linux32', 'linux64')
        if specific_system:
            self.system_name = f"operadriver_{specific_system}.zip"

        self.operadriver_path = self.driver_path

        kwargs.update(path=self.operadriver_path)
        self.operabrowser = OperaBrowser(**kwargs)

    def main(self) -> str:
        """Main function, checks for the latest version, downloads or updates operadriver binary or
        downloads specific version of operadriver.

        Returns:
            str

            driver_path (str)       : Path where operadriver was downloaded or updated.

        """
        driver_path : str = ''

        self.operabrowser.main()

        if not self.version:

            driver_path = self.__check_if_operadriver_is_up_to_date()

        else:

            driver_path = self._download_driver(version=self.version)

        return driver_path

    def __check_if_operadriver_is_up_to_date(self) -> str:
        """Main function, checks for the latest version, downloads or updates operadriver binary

        Returns:
            str

            driver_path (str)       : Path where operadriver was downloaded or updated.

        """
        driver_path : str = ''

        if self.check_driver_is_up_to_date and not self.system_name:

            is_driver_up_to_date, current_version, latest_version = super()._compare_current_version_and_latest_version_github()

            if is_driver_up_to_date:
                return self.operadriver_path

        driver_path = self._download_driver()

        if self.check_driver_is_up_to_date and not self.system_name:

            is_driver_up_to_date, current_version, latest_version = super()._compare_current_version_and_latest_version_github()

            if not is_driver_up_to_date:
                message = ('Problem with updating operadriver'
                            f'current_version: {current_version} latest_version: {latest_version}')
                logger.error(message)
                message = 'Trying to download previous latest version of operadriver'
                logger.info(message)

                driver_path = self._download_driver(previous_version=True)

        return driver_path

    def __rename_driver(self, archive_folder_path : str, archive_operadriver_path : str) -> None:
        """Renames operadriver if it was given

        Args:
            archive_folder_path (str)       : Path to the main folder
            archive_operadriver_path (str)  : Path to the operadriver archive

        """
        renamed_driver_path : str = ''

        new_path = archive_folder_path + os.path.sep + self.filename

        if Path(new_path).exists():
            Path(new_path).unlink()

        os.rename(archive_operadriver_path, new_path)

        renamed_driver_path = self.path + self.filename
        if Path(renamed_driver_path).exists():
            Path(renamed_driver_path).unlink()

        copyfile(new_path, renamed_driver_path)

    def _get_latest_previous_version_operadriver_via_requests(self) -> str:
        """Gets previous latest operadriver version


        Returns:
            str

            latest_version_previous (str)   : Latest previous version of operadriver.

        """

        latest_previous_version : str = ''

        repo_name = OperaDriver._repo_name
        latest_previous_version = self.github_viewer.get_release_version_by_repo_name(repo_name=repo_name, index=1)

        logger.info(f'Latest previous version of operadriver: {latest_previous_version}')

        return latest_previous_version

    def _check_if_version_is_valid(self, url : str) -> None:
        """Checks the specified version for existence.

        Args:
            url (str)           : Full download url of operadriver.

        """
        archive_name : str = url.split("/")[len(url.split("/"))-1]
        is_found : bool = False

        find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], url)
        driver_version = 'v' + find_string[0] if len(find_string) > 0 else ''

        json_data = self.github_viewer.get_all_releases_data_by_repo_name(OperaDriver._repo_name)

        for data in json_data:
            if data.get('tag_name') == driver_version or data.get('name') == driver_version:
                for asset in data.get('assets'):
                    if asset.get('name') == archive_name:
                        is_found = True
                        break

        if not is_found:
            message = f'Wrong version or system_name was specified. driver_version: {driver_version} url: {url}'
            raise DriverVersionInvalidException(message)

    def _download_driver(self, version : str = '', previous_version : bool = False) -> str:
        """Function to download, delete or upgrade current operadriver

        Args:
            version (str)               : Specific operadriver version to download. Defaults to empty string.
            previous_version (boll)     : If true, operadriver latest previous version will be downloaded. Defaults to False.

        Returns:
            str

            driver_path (str)       : Path to unzipped driver.

        """

        url : str = ''
        latest_version : str = ''
        latest_previous_version : str = ''

        driver_path : str = ''

        if self.upgrade:

            super()._delete_current_driver_for_current_os()

        if version:

            url = self.setting["OperaDriver"]["LinkLastReleasePlatform"].format(version, version)

            logger.info(f'Started download operadriver specific_version: {version}')

        elif previous_version:

            latest_previous_version = self._get_latest_previous_version_operadriver_via_requests()

            url = self.setting["OperaDriver"]["LinkLastReleasePlatform"].format(latest_previous_version, latest_previous_version)

            logger.info(f'Started download operadriver latest_previous_version: {latest_previous_version}')

        else:

            latest_version = super()._get_latest_version_driver_github()

            url = self.setting["OperaDriver"]["LinkLastReleasePlatform"].format(latest_version, latest_version)

            logger.info(f'Started download operadriver latest_version: {latest_version}')

        if self.system_name:
            url = url.replace(url.split("/")[-1], '')
            url = url + self.system_name

            logger.info(f'Started downloading operadriver for specific system: {self.system_name}')

        if any([version, self.system_name ,latest_previous_version]):
            self._check_if_version_is_valid(url=url)

        archive_name = url.split("/")[-1]
        out_path = self.path + archive_name

        if Path(out_path).exists():
            Path(out_path).unlink()

        logger.info(f'Started download operadriver by url: {url}')

        if self.info_messages:
            archive_path = wget.download(url=url, out=out_path)
        else:
            archive_path = wget.download(url=url, out=out_path, bar=None)

        logger.info(f'Operadriver was downloaded to path: {archive_path}')

        time.sleep(2)

        out_path = self.path
        self.extractor.extract_and_detect_archive_format(archive_path=archive_path, out_path=out_path)

        platform : str = self.setting['OperaDriver']['LastReleasePlatform']

        archive_folder_path = self.path + Path(archive_path).stem + os.path.sep
        archive_operadriver_path = archive_folder_path + platform

        if not self.filename:

            copyfile(archive_operadriver_path, self.path + platform)

        else:

            self.__rename_driver(archive_folder_path=archive_folder_path,
                                                    archive_operadriver_path=archive_operadriver_path)

        if Path(archive_path).exists():
            Path(archive_path).unlink()

        if Path(archive_folder_path).exists():
            shutil.rmtree(archive_folder_path)

        driver_path = self.operadriver_path

        logger.info(f'Operadriver was successfully unpacked by path: {driver_path}')

        if self.chmod:

            super()._chmod_driver()

        return driver_path
        