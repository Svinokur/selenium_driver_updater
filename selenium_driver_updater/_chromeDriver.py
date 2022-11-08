#pylint: disable=logging-fstring-interpolation
#Standart library imports
import time
from pathlib import Path
from typing import Tuple

# Third party imports
import wget

# Local imports
from selenium_driver_updater.browsers._chromeBrowser import ChromeBrowser

from selenium_driver_updater.util.logger import logger
from selenium_driver_updater.driver_base import DriverBase

class ChromeDriver(DriverBase):
    """Class for working with Selenium chromedriver binary"""

    _tmp_folder_path = 'tmp'

    def __init__(self, **kwargs):

        DriverBase.__init__(self, **kwargs)

        self.system_name = ''

        #assign of specific os
        specific_system = str(kwargs.get('system_name', ''))
        specific_system = specific_system.replace('win64', 'win32')
        if specific_system:
            self.system_name = f"chromedriver_{specific_system}.zip"

        self.chromedriver_path = self.driver_path

        kwargs.update(path=self.chromedriver_path)
        self.chromebrowser = ChromeBrowser(**kwargs)

    def main(self) -> str:
        """Main function, checks for the latest version, downloads or updates chromedriver binary or
        downloads specific version of chromedriver.

        Returns:
            str

            driver_path (str) : Path where chromedriver was downloaded or updated.

        """
        driver_path : str = ''

        self.chromebrowser.main()

        if not self.version:

            #additional checking for main versions to equal - for example, chromedriver version main is 90 and chrome browser is still 89
            is_equal, latest_version_driver, latest_version_browser = self._compare_latest_version_main_chromedriver_and_latest_version_main_chrome_browser()

            if is_equal:

                driver_path = self._check_if_chromedriver_is_up_to_date()

            if not is_equal:

                message = (f' Problem with chromedriver latest_version_driver:'
                    f'{latest_version_driver} latest_version_browser: {latest_version_browser}\n'
                    ' It often happen when new version of chromedriver released, but new version of chrome browser is not\n'
                    ' Trying to download the latest previous version of chromedriver')
                logger.error(message)

                driver_path = self._download_driver(previous_version=True)

        else:

            driver_path = self._download_driver(version=self.version)

        return driver_path

    def _compare_latest_version_main_chromedriver_and_latest_version_main_chrome_browser(self) -> Tuple[bool, str, str]:
        """Compares latest main version of chromedriver and latest main version of chrome browser"""
        is_equal : bool = False
        latest_version_chromedriver_main : str = ''
        latest_version_browser_main : str = ''

        latest_version_chromedriver = super()._get_latest_version_driver(no_messages=True)

        latest_version_browser = self.chromebrowser._get_latest_version_chrome_browser(no_messages=True)

        latest_version_chromedriver_main = latest_version_chromedriver.split('.', maxsplit=1)[0]
        latest_version_browser_main = latest_version_browser.split('.', maxsplit=1)[0]

        if int(latest_version_chromedriver_main) <= int(latest_version_browser_main):
            is_equal = True

        return is_equal, latest_version_chromedriver_main, latest_version_browser_main

    def _check_if_chromedriver_is_up_to_date(self) -> str:
        """Сhecks for the latest version, downloads or updates chromedriver binary

        Returns:
            str

            driver_path (str) : Path where chromedriver was downloaded or updated.

        """
        driver_path : str = ''

        if self.check_driver_is_up_to_date and not self.system_name:

            is_driver_up_to_date, current_version, latest_version = super()._compare_current_version_and_latest_version()

            if is_driver_up_to_date:
                return self.chromedriver_path

        driver_path = self._download_driver()

        if self.check_driver_is_up_to_date and not self.system_name:

            is_driver_up_to_date, current_version, latest_version = super()._compare_current_version_and_latest_version()

            if not is_driver_up_to_date:

                message = (f'Problem with updating chromedriver'
                        f'current_version: {current_version} latest_version: {latest_version}')
                logger.error(message)
                message = 'Trying to download previous latest version of chromedriver'
                logger.info(message)

                driver_path = self._download_driver(previous_version=True)

        return driver_path

    def _get_latest_previous_version_chromedriver_via_requests(self) -> str:
        """Gets previous latest chromedriver version


        Returns:
            str

            latest_version_previous (str)   : Latest previous version of chromedriver.

        """

        latest_version_previous : str = ''

        url = self.setting["ChromeDriver"]["LinkLastRelease"]
        json_data = self.requests_getter.get_result_by_request(url=url)

        latest_version = str(json_data)
        latest_version_main = latest_version.split(".", maxsplit=1)[0]

        latest_version_main_previous = int(latest_version_main) - 1

        url = self.setting["ChromeDriver"]["LinkLatestReleaseSpecificVersion"].format(latest_version_main_previous)
        json_data = self.requests_getter.get_result_by_request(url=url)

        latest_version_previous = str(json_data)

        logger.info(f'Latest previous version of chromedriver: {latest_version_previous}')

        return latest_version_previous

    def _download_driver(self, version : str = '', previous_version : bool = False) -> str:
        """Function to download, delete or upgrade current chromedriver

        Args:
            version (str)               : Specific chromedriver version to download. Defaults to empty string.
            previous_version (boll)     : If true, chromedriver latest previous version will be downloaded. Defaults to False.

        Returns:
            str

            driver_path (str) : Path to unzipped driver.

        """

        url : str = ''
        latest_previous_version : str = ''
        latest_version : str = ''
        driver_path : str = ''

        if self.upgrade:

            super()._delete_current_driver_for_current_os()

        if version:

            url = self.setting["ChromeDriver"]["LinkLastReleaseFile"].format(version)
            logger.info(f'Started download chromedriver specific_version: {version}')

        elif previous_version:

            latest_previous_version = self._get_latest_previous_version_chromedriver_via_requests()

            url = self.setting["ChromeDriver"]["LinkLastReleaseFile"].format(latest_previous_version)
            logger.info(f'Started download chromedriver latest_previous_version: {latest_previous_version}')

        else:

            latest_version = super()._get_latest_version_driver()

            url = self.setting["ChromeDriver"]["LinkLastReleaseFile"].format(latest_version)
            logger.info(f'Started download chromedriver latest_version: {latest_version}')

        if self.system_name:
            url = url.replace(url.split("/")[-1], '')
            url = url + self.system_name

            logger.info(f'Started downloading chromedriver for specific system: {self.system_name}')

        if any([version, self.system_name ,latest_previous_version]):
            if 'mac64_m1' in url:
                try:
                    super()._check_if_version_is_valid(url=url)
                except:
                    logger.warning('Could not find binary with mac64_m1 name, trying to check version using different name')
                    url = url.replace('mac64_m1', 'mac_arm64')
                    super()._check_if_version_is_valid(url=url)
            else:
                super()._check_if_version_is_valid(url=url)

        archive_name = url.split("/")[-1]
        out_path = self.path + archive_name

        if Path(out_path).exists():
            Path(out_path).unlink()

        logger.info(f'Started download chromedriver by url: {url}')
        if 'mac64_m1' in url:
            try:
                archive_path = self._wget_download_driver(url, out_path)
            except:
                logger.warning('Could not find binary with mac64_m1 name, trying to download using different name')
                url_new = url.replace('mac64_m1', 'mac_arm64')

                archive_path = self._wget_download_driver(url_new, out_path)
        else:
            archive_path = self._wget_download_driver(url, out_path)
        time.sleep(2)

        logger.info(f'Chromedriver was downloaded to path: {archive_path}')

        out_path : str = self.path

        parameters = dict(archive_path=archive_path, out_path=out_path)

        if not self.filename:

            self.extractor.extract_and_detect_archive_format(**parameters)

        else:

            filename = self.setting['ChromeDriver']['LastReleasePlatform']
            parameters.update(dict(filename=filename, filename_replace=self.filename))

            self.extractor.extract_all_zip_archive_with_specific_name(**parameters)

        if Path(archive_path).exists():
            Path(archive_path).unlink()

        driver_path = self.chromedriver_path

        logger.info(f'Chromedriver was successfully unpacked by path: {driver_path}')

        if self.chmod:

            super()._chmod_driver()

        return driver_path

    def _wget_download_driver(self, url, path):
        if self.info_messages:
            archive_path = wget.download(url=url, out=path)
        else:
            archive_path = wget.download(url=url, out=path, bar=None)
        return archive_path
