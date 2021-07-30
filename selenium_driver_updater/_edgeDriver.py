#Standart library imports
import shutil
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

from selenium_driver_updater.browsers._edgeBrowser import EdgeBrowser

from selenium_driver_updater.util.extractor import Extractor
from selenium_driver_updater.util.requests_getter import RequestsGetter
from selenium_driver_updater.util.logger import logger

from selenium_driver_updater.util.exceptions import DriverVersionInvalidException

class EdgeDriver():
    """Class for working with Selenium edgedriver binary"""

    _tmp_folder_path = 'tmp'

    def __init__(self, **kwargs):

        self.setting : Any = setting

        self.path : str = str(kwargs.get('path'))

        self.upgrade : bool = bool(kwargs.get('upgrade'))

        self.chmod : bool = bool(kwargs.get('chmod'))

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))

        self.system_name = ''
        self.filename = ''

        #assign of specific os
        specific_filename = str(kwargs.get('filename'))
        specific_system = str(kwargs.get('system_name', ''))
        if specific_system:
            self.system_name = f"edgedriver_{specific_system}.zip"

        self.setting['EdgeDriver']['LastReleasePlatform'] = 'msedgedriver'

        #assign of filename
        specific_filename = str(kwargs.get('filename'))
        if specific_filename:
            self.filename = specific_filename + self.setting['Program']['DriversFileFormat']

        self.setting['EdgeDriver']['LastReleasePlatform'] += self.setting['Program']['DriversFileFormat']

        self.edgedriver_path : str =  self.path + self.setting['EdgeDriver']['LastReleasePlatform'] if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.info_messages = bool(kwargs.get('info_messages'))

        self.extractor = Extractor
        self.requests_getter = RequestsGetter

        kwargs.update(path=self.edgedriver_path)
        self.edgebrowser = EdgeBrowser(**kwargs)

    def main(self) -> str:
        """Main function, checks for the latest version, downloads or updates edgedriver binary

        Returns:
            str

            driver_path (str)       : Path where edgedriver was downloaded or updated.

        """

        driver_path : str = ''
        self.edgebrowser.main()

        if not self.version:

            driver_path = self.__check_if_edgedriver_is_up_to_date()

        else:

            driver_path = self.__download_driver(version=self.version)

        return driver_path

    def __get_current_version_edgedriver(self) -> str:
        """Gets current edgedriver version via command in terminal


        Returns:
            str

            driver_version (str)    : Current edgedriver version.

        Raises:

            OSError: Occurs when chromedriver made for another CPU type

        """

        driver_version : str = ''
        driver_version_terminal : str = ''

        try:

            if Path(self.edgedriver_path).exists():

                with subprocess.Popen([self.edgedriver_path, '--version'], stdout=subprocess.PIPE) as process:
                    driver_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string = re.findall(str(self.setting["Program"]["wedriverVersionPattern"]), str(driver_version_terminal))
                driver_version = find_string[0] if len(find_string) > 0 else ''

                logger.info(f'Current version of edgedriver: {driver_version}')

        except OSError:
            message_run = f'OSError error: {traceback.format_exc()}' #probably [Errno 86] Bad CPU type in executable:
            logger.error(message_run)
            return driver_version

        return driver_version

    def __get_latest_version_edgedriver(self) -> str:
        """Gets latest edgedriver version


        Returns:
            str

            latest_version (str)    : Latest version of edgedriver

        """
        latest_version : str = ''
        url = str(self.setting['EdgeDriver']['LinkLastRelease'])

        json_data = self.requests_getter.get_result_by_request(url=url)

        latest_version = re.findall(str(self.setting["Program"]["wedriverVersionPattern"]), json_data)[0]

        logger.info(f'Latest version of edgedriver: {latest_version}')

        return latest_version

    def __delete_current_edgedriver_for_current_os(self) -> None:
        """Deletes edgedriver from folder"""

        if Path(self.edgedriver_path).exists():

            logger.info(f'Deleted existing edgedriver edgedriver_path: {self.edgedriver_path}')
            Path(self.edgedriver_path).unlink()

    def __check_if_edgedriver_is_up_to_date(self) -> str:
        """Checks for the latest version, downloads or updates edgedriver binary

        Returns:
            str

            driver_path (str)       : Path where edgedriver was downloaded or updated.

        """
        driver_path : str = ''

        if self.check_driver_is_up_to_date and not self.system_name:

            is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()

            if is_driver_up_to_date:
                return self.edgedriver_path

        driver_path = self.__download_driver()

        if self.check_driver_is_up_to_date and not self.system_name:

            is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()

            if not is_driver_up_to_date:
                message = ('Problem with updating edgedriver'
                            f'current_version: {current_version} latest_version: {latest_version}')
                logger.error(message)

                message = 'Trying to download previous latest version of edgedriver'
                logger.info(message)

                driver_path = self.__download_driver(previous_version=True)

        return driver_path

    def __compare_current_version_and_latest_version(self) -> Tuple[bool, str, str]:
        """Compares current version of edgedriver to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Returns an error message if an error occurs in the function.
            is_driver_up_to_date (bool) : If true current version of edgedriver is up to date. Defaults to False.

        """
        is_driver_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''

        current_version = self.__get_current_version_edgedriver()

        if not current_version:
            return is_driver_up_to_date, current_version, latest_version

        latest_version = self.__get_latest_version_edgedriver()

        if current_version == latest_version:
            is_driver_up_to_date = True
            message = f'Your existing edgedriver is up to date. current_version: {current_version} latest_version: {latest_version}' 
            logger.info(message)

        return is_driver_up_to_date, current_version, latest_version

    def __chmod_driver(self) -> None:
        """Tries to give edgedriver needed permissions"""

        if Path(self.edgedriver_path).exists():

            logger.info('Trying to give edgedriver needed permissions')

            st = os.stat(self.edgedriver_path)
            os.chmod(self.edgedriver_path, st.st_mode | stat.S_IEXEC)

            logger.info('Needed rights for edgedriver were successfully issued')

    def __get_latest_previous_version_edgedriver_via_requests(self) -> str:
        """Gets previous latest edgedriver version


        Returns:
            str

            latest_version_previous (str)   : Latest previous version of edgedriver.

        """

        latest_previous_version : str = ''

        latest_version = self.__get_latest_version_edgedriver()

        latest_version_main = int(latest_version.split('.')[0])
        latest_previous_version_main = str(latest_version_main-1)

        url = self.setting["EdgeDriver"]["LinkLatestReleaseSpecificVersion"].format(latest_previous_version_main)

        json_data = self.requests_getter.get_result_by_request(url=url)

        latest_previous_version = str(json_data.strip())

        logger.info(f'Latest previous version of edgedriver: {latest_previous_version}')

        return latest_previous_version

    def __check_if_version_is_valid(self, url : str) -> None:
        """Checks the specified version for existence.

        Args:
            url (str)           : Full download url of edgedriver.

        """
        
        archive_name : str = url.split("/")[len(url.split("/"))-1]
        find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], url)
        driver_version = find_string[0] if len(find_string) > 0 else ''

        url_test_valid = str(self.setting["EdgeDriver"]["LinkCheckVersionIsValid"]).format(driver_version)
        version_valid : str = f"{driver_version}/{archive_name}"

        json_data = self.requests_getter.get_result_by_request(url=url_test_valid)

        if not version_valid in json_data:
            message = ('Wrong version or system_name was specified.'
            f'version_valid: {version_valid} driver_version: {driver_version} url: {url}')
            raise DriverVersionInvalidException(message)

    def __download_driver(self, version : str = '', previous_version : bool = False) -> str:
        """Function to download, delete or upgrade current chromedriver

        Args:
            version (str)               : Specific chromedriver version to download. Defaults to empty string.
            previous_version (boll)     : If true, chromedriver latest previous version will be downloaded. Defaults to False.

        Returns:
            str

            file_name (str)         : Path to unzipped driver.

        """

        url : str = ''
        driver_notes_path : str = self.path + 'Driver_Notes'
        latest_previous_version : str = ''
        latest_version : str = ''

        driver_path : str = ''

        if self.upgrade:

            self.__delete_current_edgedriver_for_current_os()

        if version:

            url = str(self.setting["EdgeDriver"]["LinkLastReleaseFile"]).format(version)
            logger.info(f'Started download edgedriver specific_version: {version}')

        elif previous_version:

            latest_previous_version = self.__get_latest_previous_version_edgedriver_via_requests()

            logger.info(f'Started download edgedriver latest_previous_version: {latest_previous_version}')
            url = str(self.setting["EdgeDriver"]["LinkLastReleaseFile"]).format(latest_previous_version)

        else:

            latest_version = self.__get_latest_version_edgedriver()

            logger.info(f'Started download edgedriver latest_version: {latest_version}')
            url = str(self.setting["EdgeDriver"]["LinkLastReleaseFile"]).format(latest_version)

        if self.system_name:
            url = url.replace(url.split("/")[-1], '')
            url = url + self.system_name

            logger.info(f'Started downloading edgedriver for specific system: {self.system_name}')

        if any([version, self.system_name ,latest_previous_version]):
            self.__check_if_version_is_valid(url=url)
        
        archive_name = url.split("/")[-1]
        out_path = self.path + archive_name

        logger.info(f'Started download edgedriver by url: {url}')

        if Path(out_path).exists():
            Path(out_path).unlink()

        if self.info_messages:
            archive_path = wget.download(url=url, out=out_path)
        else:
            archive_path = wget.download(url=url, out=out_path, bar=None)
        time.sleep(2)

        logger.info(f'Edgedriver was downloaded to path: {archive_path}')

        out_path = self.path

        parameters = dict(archive_path=archive_path, out_path=out_path)

        if not self.filename:

            self.extractor.extract_and_detect_archive_format(**parameters)

        else:


            filename = str(self.setting['EdgeDriver']['LastReleasePlatform'])
            parameters.update(dict(filename=filename, filename_replace=self.filename))

            self.extractor.extract_all_zip_archive_with_specific_name(**parameters)

        if Path(archive_path).exists():
            Path(archive_path).unlink()

        if Path(driver_notes_path).exists():
            shutil.rmtree(driver_notes_path)

        driver_path = self.edgedriver_path

        logger.info(f'Edgedriver was successfully unpacked by path: {driver_path}')

        if self.chmod:

            self.__chmod_driver()

        return driver_path
        