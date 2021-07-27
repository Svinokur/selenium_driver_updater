#Standart library imports
import shutil
import subprocess
import os
import traceback
import time
from typing import Tuple, Any
import stat
from shutil import copyfile
from pathlib import Path
import re

# Third party imports
import wget
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

# Local imports
from selenium_driver_updater._setting import setting

from selenium_driver_updater.util.extractor import Extractor
from selenium_driver_updater.util.github_viewer import GithubViewer
from selenium_driver_updater.util.requests_getter import RequestsGetter
from selenium_driver_updater.util.logger import logger

from selenium_driver_updater.browsers._operaBrowser import OperaBrowser

from selenium_driver_updater.util.exceptions import DriverVersionInvalidException

class OperaDriver():
    """Class for working with Selenium operadriver binary"""

    _repo_name = 'operasoftware/operachromiumdriver'

    def __init__(self, **kwargs):

        self.setting : Any = setting

        self.path : str = str(kwargs.get('path'))

        self.upgrade : bool = bool(kwargs.get('upgrade'))

        self.chmod : bool = bool(kwargs.get('chmod'))

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))

        self.system_name = ''
        self.filename = ''

        #assign of specific os
        specific_system = str(kwargs.get('system_name', ''))
        specific_system = specific_system.replace('linux32', 'linux64')
        if specific_system:
            self.system_name = f"operadriver_{specific_system}.zip"

        self.setting['OperaDriver']['LastReleasePlatform'] = 'operadriver'

        #assign of filename
        specific_filename = str(kwargs.get('filename'))
        if specific_filename:
            self.filename = specific_filename + self.setting['Program']['DriversFileFormat']

        self.setting['OperaDriver']['LastReleasePlatform'] += self.setting['Program']['DriversFileFormat']

        self.operadriver_path : str =  self.path + self.setting['OperaDriver']['LastReleasePlatform'] if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.info_messages = bool(kwargs.get('info_messages'))

        self.extractor = Extractor
        self.github_viewer = GithubViewer
        self.requests_getter = RequestsGetter

        kwargs.update(path=self.operadriver_path)
        self.operabrowser = OperaBrowser(**kwargs)

    def main(self) -> str:
        """Main function, checks for the latest version, downloads or updates operadriver binary or
        downloads specific version of operadriver.

        Returns:
            str

            driver_path (str)       : Path where operadriver was downloaded or updated.

        Raises:
            Except: If unexpected error raised.

        """
        driver_path : str = ''

        self.operabrowser.main()

        if not self.version:

            driver_path = self.__check_if_operadriver_is_up_to_date()

        else:

            driver_path = self.__download_driver(version=self.version)

        return driver_path

    def __get_current_version_operadriver(self) -> str:
        """Gets current operadriver version via command in terminal


        Returns:
            str

            driver_version (str)    : Current operadriver version.

        Raises:
            SessionNotCreatedException: Occurs when current edgedriver could not start.

            WebDriverException: Occurs when current edgedriver could not start or critical error occured

            OSError: Occurs when operadriver made for another CPU type

        """

        driver_version : str = ''
        driver_version_terminal : str = ''

        try:

            if Path(self.operadriver_path).exists():

                with subprocess.Popen([self.operadriver_path, '--version'], stdout=subprocess.PIPE) as process:
                    driver_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_terminal)
                driver_version = find_string[0] if len(find_string) > 0 else ''

                logger.info(f'Current version of operadriver: {driver_version}')

        except (WebDriverException, SessionNotCreatedException, OSError):
            message_run = f'Known error: {traceback.format_exc()}' #probably [Errno 86] Bad CPU type in executable:
            logger.error(message_run)
            return driver_version

        return driver_version

    def __get_latest_version_operadriver(self) -> str:
        """Gets latest operadriver version


        Returns:
            str

            latest_version (str)    : Latest version of operadriver

        Raises:
            Except: If unexpected error raised.

        """

        latest_version : str = ''

        repo_name = OperaDriver._repo_name
        json_data = self.github_viewer.get_latest_release_data_by_repo_name(repo_name=repo_name)

        latest_version = json_data.get('name')

        logger.info(f'Latest version of operadriver: {latest_version}')

        return latest_version

    def __delete_current_operadriver_for_current_os(self) -> None:
        """Deletes operadriver from specific folder

        Raises:
            Except: If unexpected error raised.

        """

        if Path(self.operadriver_path).exists():
            logger.info(f'Deleted existing operadriver operadriver_path: {self.operadriver_path}')
            Path(self.operadriver_path).unlink()

    def __check_if_operadriver_is_up_to_date(self) -> str:
        """Main function, checks for the latest version, downloads or updates operadriver binary

        Returns:
            str

            driver_path (str)       : Path where operadriver was downloaded or updated.

        Raises:
            Except: If unexpected error raised.

        """
        driver_path : str = ''

        if self.check_driver_is_up_to_date and not self.system_name:

            is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()

            if is_driver_up_to_date:
                return self.operadriver_path

        driver_path = self.__download_driver()

        if self.check_driver_is_up_to_date and not self.system_name:

            is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()

            if not is_driver_up_to_date:
                message = ('Problem with updating operadriver'
                            f'current_version: {current_version} latest_version: {latest_version}')
                logger.error(message)
                message = 'Trying to download previous latest version of operadriver'
                logger.info(message)

                driver_path = self.__download_driver(previous_version=True)

        return driver_path

    def __compare_current_version_and_latest_version(self) -> Tuple[bool, str, str]:
        """Compares current version of operadriver to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Returns an error message if an error occurs in the function.
            is_driver_up_to_date (bool) : If true current version of operadriver is up to date. Defaults to False.

        Raises:
            Except: If unexpected error raised.

        """

        is_driver_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''

        current_version = self.__get_current_version_operadriver()

        if not current_version:
            return is_driver_up_to_date, current_version, latest_version

        latest_version = self.__get_latest_version_operadriver()

        if current_version == latest_version:
            is_driver_up_to_date = True
            message = ('Your existing operadriver is up to date.' 
                    f'current_version: {current_version} latest_version: {latest_version}')
            logger.info(message)

        return is_driver_up_to_date, current_version, latest_version

    def __rename_driver(self, archive_folder_path : str, archive_operadriver_path : str) -> None:
        """Renames operadriver if it was given

        Args:
            archive_folder_path (str)       : Path to the main folder
            archive_operadriver_path (str)  : Path to the operadriver archive

        Raises:
            Except: If unexpected error raised.

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

    def __chmod_driver(self) -> None:
        """Tries to give operadriver needed permissions

        Raises:
            Except: If unexpected error raised.

        """

        if Path(self.operadriver_path).exists():

            logger.info('Trying to give operadriver needed permissions')

            st = os.stat(self.operadriver_path)
            os.chmod(self.operadriver_path, st.st_mode | stat.S_IEXEC)

            logger.info('Needed rights for operadriver were successfully issued')

    def __get_latest_previous_version_operadriver_via_requests(self) -> str:
        """Gets previous latest operadriver version


        Returns:
            str

            latest_version_previous (str)   : Latest previous version of operadriver.

        Raises:
            Except: If unexpected error raised.

        """

        latest_previous_version : str = ''

        repo_name = OperaDriver._repo_name
        json_data = self.github_viewer.get_all_releases_data_by_repo_name(repo_name=repo_name)

        latest_previous_version = json_data[1].get('name')

        logger.info(f'Latest previous version of operadriver: {latest_previous_version}')

        return latest_previous_version

    def __check_if_version_is_valid(self, url : str) -> None:
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

    def __download_driver(self, version : str = '', previous_version : bool = False) -> str:
        """Function to download, delete or upgrade current operadriver

        Args:
            version (str)               : Specific operadriver version to download. Defaults to empty string.
            previous_version (boll)     : If true, operadriver latest previous version will be downloaded. Defaults to False.

        Returns:
            str

            driver_path (str)       : Path to unzipped driver.

        Raises:
            Except: If unexpected error raised.

        """

        url : str = ''
        latest_version : str = ''
        latest_previous_version : str = ''

        driver_path : str = ''

        if self.upgrade:

            self.__delete_current_operadriver_for_current_os()

        if version:

            url = self.setting["OperaDriver"]["LinkLastReleasePlatform"].format(version, version)

            logger.info(f'Started download operadriver specific_version: {version}')

        elif previous_version:

            latest_previous_version = self.__get_latest_previous_version_operadriver_via_requests()

            url = self.setting["OperaDriver"]["LinkLastReleasePlatform"].format(latest_previous_version, latest_previous_version)

            logger.info(f'Started download operadriver latest_previous_version: {latest_previous_version}')

        else:

            latest_version = self.__get_latest_version_operadriver()

            url = self.setting["OperaDriver"]["LinkLastReleasePlatform"].format(latest_version, latest_version)

            logger.info(f'Started download operadriver latest_version: {latest_version}')

        if self.system_name:
            url = url.replace(url.split("/")[len(url.split("/"))-1], '')
            url = url + self.system_name

            logger.info(f'Started downloading chromedriver for specific system: {self.system_name}')

        if any([version, self.system_name ,latest_previous_version]):
            self.__check_if_version_is_valid(url=url)

        archive_name = url.split("/")[len(url.split("/"))-1]
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

            self.__chmod_driver()

        return driver_path
        