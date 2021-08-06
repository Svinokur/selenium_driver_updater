#pylint: disable=logging-fstring-interpolation
#Standart library imports
import subprocess
import time
import os
import re
import platform
from typing import Tuple, Any
from pathlib import Path

# Third party imports
from bs4 import BeautifulSoup

# Selenium imports
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

# Local imports
from selenium_driver_updater._setting import setting

from selenium_driver_updater.util.requests_getter import RequestsGetter
from selenium_driver_updater.util.logger import logger

class FirefoxBrowser():
    """Class for working with Firefox browser"""

    def __init__(self, **kwargs):
        self.setting : Any = setting
        self.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date'))

        self.geckodriver_path = str(kwargs.get('path'))

        self.requests_getter = RequestsGetter

    def main(self) -> None:
        """Main function, checks for the latest version, downloads or updates firefox browser

        Raises:
            Except: If unexpected error raised.

        """

        if self.check_browser_is_up_to_date:
            self._check_if_firefox_browser_is_up_to_date()

    def _check_if_firefox_browser_is_up_to_date(self) -> None:
        """Сhecks for the latest version of firefox browser

        Raises:
            Except: If unexpected error raised.

        """

        try:

            firefoxbrowser_updater_path = str(self.setting["FirefoxBrowser"]["FirefoxBrowserUpdaterPath"])
            if not firefoxbrowser_updater_path:
                message = f'Parameter "check_browser_is_up_to_date" has not been optimized for your OS yet. Please wait for the new releases.'
                raise ValueError(message)

            if not Path(firefoxbrowser_updater_path).exists():
                message = f'firefoxbrowser_updater_path: {firefoxbrowser_updater_path} is not exists. Please report your OS information and path to {firefoxbrowser_updater_path} file in repository.'
                raise FileNotFoundError(message)

            is_browser_up_to_date, current_version, latest_version = self._compare_current_version_and_latest_version_firefox_browser()

            if not is_browser_up_to_date:

                self._get_latest_firefox_browser_for_current_os()

                is_browser_up_to_date, current_version, latest_version = self._compare_current_version_and_latest_version_firefox_browser()

                if not is_browser_up_to_date:
                    message = f'Problem with updating firefox browser current_version: {current_version} latest_version: {latest_version}'
                    logger.info(message)
        
        except (ValueError, FileNotFoundError):
            pass

    def _get_current_version_firefox_browser_selenium(self) -> str:
        """Gets current firefox browser version


        Returns:
            str

            browser_version (str)   : Current firefox browser version.

        Raises:
            SessionNotCreatedException: Occurs when current geckodriver could not start.

            WebDriverException: Occurs when current geckodriver could not start or critical error occured.

        """

        browser_version : str = ''

        try:

            browser_version = self._get_current_version_firefox_browser_selenium_via_terminal()
            if not browser_version:
                message = 'Trying to get current version of firefox browser via geckodriver'
                logger.info(message)

            if Path(self.geckodriver_path).exists() and not browser_version:

                options = FirefoxOptions()
                options.add_argument("--headless")

                with webdriver.Firefox(executable_path = self.geckodriver_path, options=options) as driver:
                    browser_version = str(driver.capabilities['browserVersion'])

            logger.info(f'Current version of firefox browser: {browser_version}')

        except (WebDriverException, SessionNotCreatedException, OSError):
            pass #[Errno 86] Bad CPU type in executable:

        return browser_version

    def _get_latest_version_firefox_browser(self) -> str:
        """Gets latest firefox browser version


        Returns:
            str

            latest_version (str)    : Latest version of firefox browser.

        Raises:
            Except: If unexpected error raised.

        """

        latest_version : str = ''

        url = self.setting["FirefoxBrowser"]["LinkAllLatestReleases"]
        json_data = self.requests_getter.get_result_by_request(url=url)

        soup = BeautifulSoup(json_data, 'html.parser')
        latest_version = soup.findAll('html')[0].attrs.get('data-latest-firefox')

        logger.info(f'Latest version of firefox browser: {latest_version}')

        return latest_version

    def _get_latest_firefox_browser_for_current_os(self) -> None:
        """Trying to update firefox browser to its latest version

        Raises:
            Except: If unexpected error raised.

        """

        try:
            is_admin : bool = bool(os.getuid() == 0)
        except Exception:
            is_admin : bool = False

        try:

            update_command : str = self.setting["FirefoxBrowser"]["FirefoxBrowserUpdater"]

            message = f'Trying to update firefox browser to the latest version.'
            logger.info(message)

            if platform.system() == 'Linux':

                if is_admin:
                    os.system(update_command)

                elif not is_admin:
                    message = 'You have not ran library with sudo privileges to update firefox browser - so updating is impossible.'
                    raise ValueError(message)

            else:

                os.system(update_command)
                time.sleep(60) #wait for the updating - too long

            message = 'Firefox browser was successfully updated to the latest version.'
            logger.info(message)
        
        except ValueError:
            pass

    def _compare_current_version_and_latest_version_firefox_browser(self) -> Tuple[bool, str, str]:
        """Compares current version of firefox browser to latest version

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

        current_version = self._get_current_version_firefox_browser_selenium()

        if not current_version:
            return True, current_version, latest_version

        latest_version = self._get_latest_version_firefox_browser()

        if current_version == latest_version:
            is_browser_up_to_date = True
            message = f"Your existing firefox browser is up to date. current_version: {current_version} latest_version: {latest_version}"
            logger.info(message)

        return is_browser_up_to_date, current_version, latest_version

    def _get_current_version_firefox_browser_selenium_via_terminal(self) -> str:
        """Gets current firefox browser version via command in terminal


        Returns:
            str

            browser_version (str)   : Current firefox browser version.

        Raises:

            Except: If unexpected error raised.

        """

        browser_version : str = ''
        browser_version_terminal : str = ''

        firefox_path = self.setting["FirefoxBrowser"]["Path"]
        if firefox_path:

            logger.info('Trying to get current version of firefox browser via terminal')

            if platform.system() == 'Windows':

                for command in firefox_path:

                    with subprocess.Popen(command, stdout=subprocess.PIPE) as process:
                        browser_version_terminal = process.communicate()[0].decode('UTF-8')

                    if 'invalid' not in browser_version_terminal.lower() or 'cannot find path' not in browser_version_terminal.lower():
                        break

            elif platform.system() == 'Darwin':

                with subprocess.Popen([firefox_path, '--version'], stdout=subprocess.PIPE) as process:
                    browser_version_terminal = process.communicate()[0].decode('UTF-8')


            find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], browser_version_terminal)
            browser_version = find_string[0] if len(find_string) > 0 else ''

        return browser_version
