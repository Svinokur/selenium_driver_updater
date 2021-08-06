#pylint: disable=logging-fstring-interpolation, disable=broad-except
#Standart library imports
import subprocess
import os
import re
from typing import Tuple, Any

# Third party imports
import platform
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

# Local imports
from selenium_driver_updater._setting import setting

from selenium_driver_updater.browsers._chromiumChromeBrowser import ChromiumChromeBrowser

from selenium_driver_updater.util.requests_getter import RequestsGetter
from selenium_driver_updater.util.logger import logger

from selenium_driver_updater.util.exceptions import DriverVersionInvalidException

class ChromiumChromeDriver():
    """Class for working with Selenium chromedriver binary"""

    def __init__(self, **kwargs):

        self.setting : Any = setting

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))

        self.chromium_chromedriver_name = 'chromedriver'

        self.requests_getter = RequestsGetter

        self.chromium_chromebrowser = ChromiumChromeBrowser(**kwargs)

    def main(self) -> str:
        """Main function, checks for the latest version, downloads or updates chromium chromedriver binary or
        downloads specific version of chromium chromedriver.

        Returns:
            str

            driver_path (str) : Path where chromium chromedriver was downloaded or updated.

        """

        driver_path : str = ''
        try:
            is_admin : bool = bool(os.getuid() == 0)
        except Exception:
            is_admin : bool = False

        if platform.system() != 'Linux':
            message = 'chromium_chromedriver webdriver downloading/updating is only supported for Linux only. Please wait for the new releases.'
            raise OSError(message)

        if not is_admin:
            message = 'You have not ran library with sudo privileges to download or update chromium_chromedriver - so that is impossible.'
            raise ValueError(message)

        self.chromium_chromebrowser.main()

        driver_path = self._check_if_chromedriver_is_up_to_date()

        return driver_path

    def _get_latest_version_chromium_chromedriver(self) -> str:
        """Gets latest chromium_chromedriver version


        Returns:
            str

            latest_version (str)    : Latest version of chromedriver.

        """

        latest_version : str = ''

        url = self.setting["ChromeDriver"]["LinkLastRelease"]
        json_data = self.requests_getter.get_result_by_request(url=url)

        latest_version = str(json_data)

        logger.info(f'Latest version of chromium_chromedriver: {latest_version}')

        return latest_version

    def _get_current_version_chromium_chromedriver(self) -> str:
        """Gets current chromium_chromedriver version


        Returns:
            str

            driver_version (str)    : Current chromium_chromedriver version.

        Raises:
            SessionNotCreatedException: Occurs when current chromium_chromedriver could not start.

            WebDriverException: Occurs when current chromedriver could not start or critical error occured.

            OSError: Occurs when chromium_chromedriver made for another CPU type

        """

        driver_version : str = ''

        try:

            driver_version = self._get_current_version_chromium_chromedriver_via_terminal()
            if not driver_version:
                message = 'Trying to get current version of chromium_chromedriver via webdriver'
                logger.info(message)

            if not driver_version:

                chrome_options = webdriver.ChromeOptions()

                chrome_options.add_argument('--headless')

                driver = webdriver.Chrome(options = chrome_options)
                driver_version = str(driver.capabilities['chrome']['chromedriverVersion'].split(" ")[0])
                driver.close()
                driver.quit()

            logger.info(f'Current version of chromium_chromedriver: {driver_version}')

        except (OSError, WebDriverException, SessionNotCreatedException):
            pass #[Errno 86] Bad CPU type in executable:

        return driver_version

    def _get_current_version_chromium_chromedriver_via_terminal(self) -> str:
        """Gets current chromium_chromedriver version via command in terminal


        Returns:
            str

            driver_version (str)    : Current chromium_chromedriver version.

        """

        driver_version : str = ''
        driver_version_terminal : str = ''

        logger.info('Trying to get current version of chromium_chromedriver via terminal')

        with subprocess.Popen(self.chromium_chromedriver_name + ' --version', stdout=subprocess.PIPE, shell=True) as process:
            driver_version_terminal = process.communicate()[0].decode('UTF-8')

        find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_terminal)
        driver_version = find_string[0] if len(find_string) > 0 else ''

        return driver_version

    def _compare_current_version_and_latest_version(self) -> Tuple[bool, str, str]:
        """Compares current version of chromium_chromedriver to latest version

        Returns:
            Tuple of bool, str and str

            is_driver_up_to_date (bool) : It true the driver is up to date. Defaults to False.
            current_version (str)       : Current version of the driver.
            latest_version (str)        : Latest version of the driver.

        """

        is_driver_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''

        current_version = self._get_current_version_chromium_chromedriver()

        latest_version = self._get_latest_version_chromium_chromedriver()

        if current_version == latest_version:
            is_driver_up_to_date = True
            message = ('Your existing chromium_chromedriver is up to date.'
                        f'current_version: {current_version} latest_version: {latest_version}')
            logger.info(message)

        return is_driver_up_to_date, current_version, latest_version

    def _check_if_chromedriver_is_up_to_date(self) -> str:
        """Сhecks for the latest version, downloads or updates chromedriver binary

        Returns:
            str

            driver_path (str)       : Path where chromedriver was downloaded or updated.

        """
        driver_path : str = ''

        if self.check_driver_is_up_to_date:

            is_driver_up_to_date, current_version, latest_version = self._compare_current_version_and_latest_version()

            if is_driver_up_to_date:
                return ''

        driver_path = self._get_latest_chromium_chromedriver_for_current_os()

        if self.check_driver_is_up_to_date:

            is_driver_up_to_date, current_version, latest_version = self._compare_current_version_and_latest_version()

            if not is_driver_up_to_date:
                message = f'Problem with updating chromedriver current_version: {current_version} latest_version: {latest_version}'
                raise DriverVersionInvalidException(message)


        return driver_path

    def _get_latest_chromium_chromedriver_for_current_os(self) -> str:
        """Downloads latest chromium_chromedriver to specific path

        Returns:
            str

            driver_path (str)       : Path where chromedriver was downloaded or updated.

        """
        driver_path : str = ''

        message = 'Trying to update chromium_chromedriver to the latest version.'
        logger.info(message)

        os.system(self.setting["ChromiumChromeDriver"]["ChromiumChromeDriverUpdater"])

        message = 'Chromium_chromedriver was successfully updated to the latest version.'
        logger.info(message)

        return driver_path
