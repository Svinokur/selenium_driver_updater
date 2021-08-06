#pylint: disable=logging-fstring-interpolation
#Standart library imports
import subprocess
import time
import os
import re
from typing import Tuple, Any
from pathlib import Path
import platform

# Third party imports
from bs4 import BeautifulSoup

# Selenium imports
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

# Local imports
from selenium_driver_updater._setting import setting

from selenium_driver_updater.util.requests_getter import RequestsGetter
from selenium_driver_updater.util.logger import logger

class EdgeBrowser():
    """Class for working with Edge browser"""

    def __init__(self, **kwargs):
        self.setting : Any = setting
        self.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date'))

        self.edgedriver_path = str(kwargs.get('path'))

        self.requests_getter = RequestsGetter

    def main(self):
        """Main function, checks for the latest version, downloads or updates edge browser

        Raises:
            Except: If unexpected error raised.

        """

        if self.check_browser_is_up_to_date:
            self._check_if_edge_browser_is_up_to_date()

    def _check_if_edge_browser_is_up_to_date(self) -> None:
        """Сhecks for the latest version of edge browser

        Raises:
            Except: If unexpected error raised.

        """

        try:

            edgebrowser_updater_path = str(self.setting["EdgeBrowser"]["EdgeBrowserUpdaterPath"])
            if not edgebrowser_updater_path:
                message = 'Parameter "check_browser_is_up_to_date" has not been optimized for your OS yet. Please wait for the new releases.'
                raise ValueError(message)

            if not Path(edgebrowser_updater_path).exists():
                message = f'edgebrowser_updater_path: {edgebrowser_updater_path} is not exists. Please report your OS information and path to {edgebrowser_updater_path} file in repository.'
                raise FileNotFoundError(message)

            is_browser_up_to_date, current_version, latest_version = self._compare_current_version_and_latest_version_edge_browser()

            if not is_browser_up_to_date:

                self._get_latest_edge_browser_for_current_os()

                is_browser_up_to_date, current_version, latest_version = self._compare_current_version_and_latest_version_edge_browser()

                if not is_browser_up_to_date:
                    message = f'Problem with updating edge browser current_version: {current_version} latest_version: {latest_version}'
                    logger.info(message)

        except (ValueError, FileNotFoundError):
            pass

    def _get_current_version_edge_browser_selenium(self) -> str:
        """Gets current edge browser version


        Returns:
            str

            browser_version (str)   : Current edge browser version.

        Raises:
            SessionNotCreatedException: Occurs when current edgedriver could not start.

            WebDriverException: Occurs when current edgedriver could not start or critical error occured.

        """

        browser_version : str = ''

        try:

            browser_version = self._get_current_version_edge_browser_selenium_via_terminal()
            if not browser_version:
                message = 'Trying to get current version of edge browser via edgedriver'
                logger.info(message)

            if Path(self.edgedriver_path).exists() and not browser_version:

                desired_cap = {}

                with webdriver.Edge(executable_path = self.edgedriver_path, capabilities=desired_cap) as driver:
                    browser_version = str(driver.capabilities['browserVersion'])

            logger.info(f'Current version of edge browser: {browser_version}')

        except (WebDriverException, SessionNotCreatedException, OSError):
            pass #[Errno 86] Bad CPU type in executable:

        return browser_version

    def _get_latest_version_edge_browser(self) -> str:
        """Gets latest edge browser version


        Returns:
            str

            latest_version (str)    : Latest version of edge browser.

        Raises:
            Except: If unexpected error raised.

        """

        latest_version : str = ''

        url = self.setting["EdgeBrowser"]["LinkAllLatestRelease"]
        json_data = self.requests_getter.get_result_by_request(url=url)

        soup = BeautifulSoup(json_data, 'html.parser')
        latest_version_element = soup.findAll('h2')[0].text

        latest_version = re.findall(self.setting["Program"]["wedriverVersionPattern"], latest_version_element)[0]

        logger.info(f'Latest version of edge browser: {latest_version}')

        return latest_version

    def _get_latest_edge_browser_for_current_os(self) -> None:
        """Trying to update edge browser to its latest version

        Raises:
            Except: If unexpected error raised.

        """

        message = 'Trying to update edge browser to the latest version.'
        logger.info(message)

        os.system(self.setting["EdgeBrowser"]["EdgeBrowserUpdater"])
        time.sleep(60) #wait for the updating

        message = 'Edge browser was successfully updated to the latest version.'
        logger.info(message)

    def _compare_current_version_and_latest_version_edge_browser(self) -> Tuple[bool, str, str]:
        """Compares current version of edge browser to latest version

        Returns:
            Tuple of bool, str and str

            is_browser_up_to_date (bool)    : It true the browser is up to date. Defaults to False.
            current_version (str)           : Current version of the browser.
            latest_version (str)            : Latest version of the browser.

        Raises:
            Except: If unexpected error raised.

        """

        is_browser_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''

        current_version = self._get_current_version_edge_browser_selenium()

        if not current_version:
            return True, current_version, latest_version

        latest_version = self._get_latest_version_edge_browser()

        if current_version == latest_version:
            is_browser_up_to_date = True
            message = f"Your existing edge browser is up to date. current_version: {current_version} latest_version: {latest_version}"
            logger.info(message)

        return is_browser_up_to_date, current_version, latest_version

    def _get_current_version_edge_browser_selenium_via_terminal(self) -> str:
        """Gets current edge browser version via command in terminal


        Returns:
            str

            browser_version (str)   : Current edge browser version.

        Raises:

            Except: If unexpected error raised.

        """

        browser_version : str = ''
        browser_version_terminal : str = ''

        edgebrowser_path = self.setting["EdgeBrowser"]["Path"]
        if edgebrowser_path:

            logger.info('Trying to get current version of edge browser via terminal')


            if platform.system() == 'Darwin':

                with subprocess.Popen([edgebrowser_path, '--version'], stdout=subprocess.PIPE) as process:
                    browser_version_terminal = process.communicate()[0].decode('UTF-8')

            elif platform.system() == 'Windows':

                with subprocess.Popen(edgebrowser_path, stdout=subprocess.PIPE) as process:
                    browser_version_terminal = process.communicate()[0].decode('UTF-8')

            find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], browser_version_terminal)
            browser_version = find_string[0] if len(find_string) > 0 else ''

        return browser_version
