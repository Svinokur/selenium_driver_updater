#Standart library imports
import subprocess
import os
import traceback
import time
from typing import Tuple, Any
import re
from pathlib import Path
import stat

# Third party imports
import wget

# Local imports

from selenium_driver_updater._setting import setting

from selenium_driver_updater.util.extractor import Extractor
from selenium_driver_updater.util.github_viewer import GithubViewer
from selenium_driver_updater.util.requests_getter import RequestsGetter
from selenium_driver_updater.util.logger import logger

from selenium_driver_updater.browsers._firefoxBrowser import FirefoxBrowser

from selenium_driver_updater.util.exceptions import DriverVersionInvalidException

class GeckoDriver():
    """Class for working with Selenium geckodriver binary"""

    _repo_name = 'mozilla/geckodriver'

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
        specific_system = specific_system.replace('mac64_m1', 'macos-aarch64').replace('mac64', 'macos')
        if specific_system:
            if 'win' in specific_system:
                self.system_name = "geckodriver-v{}-" + f"{specific_system}.zip"
            else:
                self.system_name = "geckodriver-v{}-" + f"{specific_system}.tar.gz"

        self.setting['GeckoDriver']['LastReleasePlatform'] = 'geckodriver'

        #assign of filename
        specific_filename = str(kwargs.get('filename'))
        if specific_filename:
            self.filename = specific_filename + self.setting['Program']['DriversFileFormat']

        self.setting['GeckoDriver']['LastReleasePlatform'] += self.setting['Program']['DriversFileFormat']

        self.geckodriver_path : str =  self.path + self.setting['GeckoDriver']['LastReleasePlatform'] if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.info_messages = bool(kwargs.get('info_messages'))

        self.extractor = Extractor
        self.github_viewer = GithubViewer
        self.requests_getter = RequestsGetter

        kwargs.update(path=self.geckodriver_path)
        self.firefoxbrowser = FirefoxBrowser(**kwargs)

    def main(self) -> str:
        """Main function, checks for the latest version, downloads or updates geckodriver binary or
        downloads specific version of geckodriver.

        Returns:
            str

            driver_path (str) : Path where geckodriver was downloaded or updated.

        Raises:
            Except: If unexpected error raised.

        """
        driver_path : str = ''

        self.firefoxbrowser.main()

        if not self.version:

            driver_path = self.__check_if_geckodriver_is_up_to_date()

        else:

            driver_path = self.__download_driver(version=self.version)

        return driver_path

    def __get_current_version_geckodriver(self) -> str:
        """Gets current geckodriver version via command in terminal


        Returns:
            str

            driver_version (str)    : Current geckodriver version.

        Raises:

            OSError: Occurs when geckodriver maded for another CPU type

            Except: If unexpected error raised.

        """

        driver_version : str = ''
        driver_version_terminal : str = ''

        try:

            if Path(self.geckodriver_path).exists():

                with subprocess.Popen([self.geckodriver_path, '--version'], stdout=subprocess.PIPE) as process:
                    driver_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_terminal)
                driver_version = find_string[0] if len(find_string) > 0 else ''

                logger.info(f'Current version of geckodriver: {driver_version}')

        except OSError:
            message_run = f'OSError error: {traceback.format_exc()}' #probably [Errno 86] Bad CPU type in executable:
            logger.error(message_run)
            return driver_version

        return driver_version

    def __get_latest_version_geckodriver(self) -> str:
        """Gets latest geckodriver version


        Returns:
            str

            latest_version (str)    : Latest version of geckodriver

        Raises:
            Except: If unexpected error raised.

        """

        latest_version : str = ''

        repo_name = GeckoDriver._repo_name
        json_data = self.github_viewer.get_latest_release_data_by_repo_name(repo_name=repo_name)

        latest_version = json_data.get('name')

        logger.info(f'Latest version of geckodriver: {latest_version}')

        return latest_version

    def __delete_current_geckodriver_for_current_os(self) -> None:
        """Deletes geckodriver from folder

        Raises:
            Except: If unexpected error raised.

        """

        if Path(self.geckodriver_path).exists():
            logger.info(f'Deleted existing geckodriver geckodriver_path: {self.geckodriver_path}')
            Path(self.geckodriver_path).unlink()

    def __check_if_geckodriver_is_up_to_date(self) -> str:
        """Main function, checks for the latest version, downloads or updates geckodriver binary

        Returns:
            str

            driver_path (str)       : Path where geckodriver was downloaded or updated.

        Raises:
            Except: If unexpected error raised.

        """
        driver_path : str = ''

        if self.check_driver_is_up_to_date and not self.system_name:

            is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()

            if is_driver_up_to_date:
                return self.geckodriver_path

        driver_path = self.__download_driver()

        if self.check_driver_is_up_to_date and not self.system_name:

            is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()

            if not is_driver_up_to_date:
                message = f'Problem with updating geckodriver current_version: {current_version} latest_version: {latest_version}'
                logger.error(message)
                message = 'Trying to download previous latest version of geckodriver'
                logger.info(message)

                driver_path = self.__download_driver(previous_version=True)

        return driver_path

    def __compare_current_version_and_latest_version(self) -> Tuple[bool, str, str]:
        """Compares current version of geckodriver to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Returns an error message if an error occurs in the function.
            is_driver_up_to_date (bool) : If true current version of geckodriver is up to date. Defaults to False.

        Raises:
            Except: If unexpected error raised.

        """
        is_driver_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''

        current_version = self.__get_current_version_geckodriver()

        if not current_version:
            return is_driver_up_to_date, current_version, latest_version

        latest_version = self.__get_latest_version_geckodriver()

        if current_version == latest_version:
            is_driver_up_to_date = True
            message = f'Your existing geckodriver is up to date. current_version: {current_version} latest_version: {latest_version}' 
            logger.info(message)

        return is_driver_up_to_date, current_version, latest_version

    def __chmod_driver(self) -> None:
        """Tries to give geckodriver needed permissions

        Raises:
            Except: If unexpected error raised.

        """

        if Path(self.geckodriver_path).exists():

            logger.info('Trying to give geckodriver needed permissions')

            st = os.stat(self.geckodriver_path)
            os.chmod(self.geckodriver_path, st.st_mode | stat.S_IEXEC)

            logger.info('Needed rights for geckodriver were successfully issued')

    def __get_latest_previous_version_geckodriver_via_requests(self) -> str:
        """Gets previous latest geckodriver version


        Returns:
            str

            latest_version_previous (str)   : Latest previous version of geckodriver.

        Raises:
            Except: If unexpected error raised.

        """

        latest_previous_version : str = ''

        repo_name = GeckoDriver._repo_name
        json_data = self.github_viewer.get_all_releases_data_by_repo_name(repo_name=repo_name)

        latest_previous_version = latest_previous_version = json_data[1].get('name')

        logger.info(f'Latest previous version of geckodriver: {latest_previous_version}')

        return latest_previous_version

    def __check_if_version_is_valid(self, url : str) -> None:
        """Checks the specified version for existence.

        Args:
            url (str)           : Full download url of geckodriver.

        """
        archive_name : str = url.split("/")[len(url.split("/"))-1]
        is_found : bool = False
        find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], url)
        driver_version = find_string[0] if len(find_string) > 0 else ''

        json_data = self.github_viewer.get_all_releases_data_by_repo_name(GeckoDriver._repo_name)

        for data in json_data:
            if data.get('name') == driver_version:
                for asset in data.get('assets'):
                    if asset.get('name') == archive_name:
                        is_found = True
                        break
                break

        if not is_found:
            message = f'Wrong version or system_name was specified. driver_version: {driver_version} url: {url}'
            raise DriverVersionInvalidException(message)

    def __download_driver(self, version : str = '', previous_version : bool = False) -> str:
        """Function to download, delete or upgrade current geckodriver

        Args:
            version (str)               : Specific geckodriver version to download. Defaults to empty string.
            previous_version (boll)     : If true, geckodriver latest previous version will be downloaded. Defaults to False.

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

            self.__delete_current_geckodriver_for_current_os()

        if version:
            
            url = self.setting["GeckoDriver"]["LinkLastReleasePlatform"].format(version, version)
            logger.info(f'Started download geckodriver specific_version: {version}')

        elif previous_version:

            latest_previous_version = self.__get_latest_previous_version_geckodriver_via_requests()

            url = self.setting["GeckoDriver"]["LinkLastReleasePlatform"].format(latest_previous_version, latest_previous_version)
            logger.info(f'Started download geckodriver latest_previous_version: {latest_previous_version}')

        else:

            latest_version = self.__get_latest_version_geckodriver()

            url = self.setting["GeckoDriver"]["LinkLastReleasePlatform"].format(latest_version, latest_version)
            logger.info(f'Started download geckodriver latest_version: {latest_version}')

        if self.system_name:
            url = url.replace(url.split("/")[len(url.split("/"))-1], '')
            url = url + self.system_name.format(latest_version) if latest_version else url + self.system_name.format(latest_previous_version) if latest_previous_version else\
            url + self.system_name.format(version)    

            logger.info(f'Started downloading geckodriver for specific system: {self.system_name}')

        if any([version, self.system_name ,latest_previous_version]):
            self.__check_if_version_is_valid(url=url)

        archive_name = url.split("/")[len(url.split("/"))-1]
        out_path = self.path + archive_name

        if Path(out_path).exists():
            Path(out_path).unlink()

        logger.info(f'Started download geckodriver by url: {url}')

        if self.info_messages:
            archive_path = wget.download(url=url, out=out_path)
        else:
            archive_path = wget.download(url=url, out=out_path, bar=None)
        time.sleep(2)

        logger.info(f'Geckodriver was downloaded to path: {archive_path}')

        out_path = self.path

        parameters = dict(archive_path=archive_path, out_path=out_path)

        if not self.filename:

            self.extractor.extract_and_detect_archive_format(**parameters)

        else:
            filename = self.setting['GeckoDriver']['LastReleasePlatform']
            parameters.update(dict(filename=filename, filename_replace=self.filename))

            self.extractor.extract_all_zip_archive_with_specific_name(**parameters)

        if Path(archive_path).exists():
            Path(archive_path).unlink()

        driver_path = self.geckodriver_path

        logger.info(f'Geckodriver was successfully unpacked by path: {driver_path}')

        if self.chmod:

            self.__chmod_driver()

        return driver_path
        