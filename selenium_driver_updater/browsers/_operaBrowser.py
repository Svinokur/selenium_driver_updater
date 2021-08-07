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
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

# Local imports
from selenium_driver_updater._setting import setting

from selenium_driver_updater.util.requests_getter import RequestsGetter
from selenium_driver_updater.util.logger import logger

class OperaBrowser():
    """Class for working with Opera browser"""

    def __init__(self, **kwargs):
        self.setting : Any = setting
        self.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date'))

        self.operadriver_path = str(kwargs.get('path'))

        self.requests_getter = RequestsGetter

    def main(self) -> None:
        """Main function, checks for the latest version, downloads or updates opera browser"""

        if self.check_browser_is_up_to_date:
            self._check_if_opera_browser_is_up_to_date()

    def _check_if_opera_browser_is_up_to_date(self) -> None:
        """Сhecks for the latest version of opera browser

        Raises:
            Except: If unexpected error raised.

        """

        try:

            operabrowser_updater_path = str(self.setting["OperaBrowser"]["OperaBrowserUpdaterPath"])
            if not operabrowser_updater_path:
                message = f'Parameter "check_browser_is_up_to_date" has not been optimized for your OS yet. Please wait for the new releases.'
                raise ValueError(message)

            if not Path(operabrowser_updater_path).exists():
                message = f'operabrowser_updater_path: {operabrowser_updater_path} is not exists. Please report your OS information and path to {operabrowser_updater_path} file in repository.'
                raise FileNotFoundError(message)

            is_browser_up_to_date, current_version, latest_version = self._compare_current_version_and_latest_version_opera_browser()

            if not is_browser_up_to_date:

                self._get_latest_opera_browser_for_current_os()

                is_browser_up_to_date, current_version, latest_version = self._compare_current_version_and_latest_version_opera_browser()

                if not is_browser_up_to_date:
                    message = f'Problem with updating opera browser current_version: {current_version} latest_version: {latest_version}'
                    logger.info(message)

        except (ValueError, FileNotFoundError):
            pass

    def _get_current_version_opera_browser_selenium(self) -> str:
        """Gets current opera browser version


        Returns:
            str

            browser_version (str)   : Current opera browser version.

        Raises:
            SessionNotCreatedException: Occurs when current operadriver could not start.

            WebDriverException: Occurs when current operadriver could not start or critical error occured.

        """

        browser_version : str = ''

        try:

            browser_version = self._get_current_version_opera_browser_selenium_via_terminal()
            if not browser_version:
                message = 'Trying to get current version of opera browser via operadriver'
                logger.info(message)

            if Path(self.operadriver_path).exists() and not browser_version:

                with webdriver.Opera(executable_path = self.operadriver_path) as driver:
                    browser_version = driver.execute_script("return navigator.userAgent")

                find_string = re.findall('OPR/' + self.setting["Program"]["wedriverVersionPattern"], browser_version)
                browser_version = find_string[0] if len(find_string) > 0 else ''

            logger.info(f'Current version of opera browser: {browser_version}')

        except (WebDriverException, SessionNotCreatedException, OSError):
            pass #[Errno 86] Bad CPU type in executable:

        return browser_version

    def _get_latest_version_opera_browser(self) -> str:
        """Gets latest opera browser version


        Returns:
            str

            latest_version (str)    : Latest version of opera browser.

        Raises:
            Except: If unexpected error raised.

        """

        latest_version : str = ''
        version : str = ''

        url = self.setting["OperaBrowser"]["LinkAllLatestRelease"]
        json_data = self.requests_getter.get_result_by_request(url=url)

        soup = BeautifulSoup(json_data, 'html.parser')

        system_name = platform.system()
        system_name = system_name.replace('Darwin', 'mac')
        system_name = system_name.replace('Windows', 'win')
        system_name = system_name.lower() + '/' #mac -> mac/ or Linux -> linux/

        elements = soup.findAll('a')
        for i,_ in enumerate(elements, 1):
            version = elements[-i].attrs.get('href')
            url_release = url + version

            json_data = self.requests_getter.get_result_by_request(url=url_release)

            if not system_name in json_data:
                continue

            else:
                break
        
        latest_version = version.replace('/', '')
        
        logger.info(f'Latest version of opera browser: {latest_version}')

        return latest_version

    def _get_latest_opera_browser_for_current_os(self) -> None:
        """Trying to update opera browser to its latest version

        Raises:
            Except: If unexpected error raised.

        """
        try:
            is_admin : bool = bool(os.getuid() == 0)
        except Exception:
            is_admin : bool = False

        try:

            update_command : str = self.setting["OperaBrowser"]["OperaBrowserUpdater"]

            message = 'Trying to update opera browser to the latest version.'
            logger.info(message)

            if platform.system() == 'Linux':

                if is_admin:
                    os.system(update_command)

                elif not is_admin:
                    message = 'You have not ran library with sudo privileges to update opera browser - so updating is impossible.'
                    raise ValueError(message)

            else:

                os.system(update_command)
                time.sleep(60) #wait for the updating

            message = 'Opera browser was successfully updated to the latest version.'
            logger.info(message)

        except ValueError:
            pass

    def _compare_current_version_and_latest_version_opera_browser(self) -> Tuple[bool, str, str]:
        """Compares current version of opera browser to latest version

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

        current_version = self._get_current_version_opera_browser_selenium()

        if not current_version:
            return True, current_version, latest_version

        latest_version = self._get_latest_version_opera_browser()

        if current_version == latest_version:
            is_browser_up_to_date = True
            message = f"Your existing opera browser is up to date. current_version: {current_version} latest_version: {latest_version}"
            logger.info(message)

        return is_browser_up_to_date, current_version, latest_version

    def _get_current_version_opera_browser_selenium_via_terminal(self) -> str:
        """Gets current opera browser version via command in terminal


        Returns:
            str

            browser_version (str)   : Current opera browser version.

        Raises:

            Except: If unexpected error raised.

        """

        browser_version : str = ''
        browser_version_terminal : str = ''

        operabrowser_path = self.setting["OperaBrowser"]["Path"]
        if operabrowser_path:

            logger.info('Trying to get current version of opera browser via terminal')

            if platform.system() == 'Windows':

                with subprocess.Popen(operabrowser_path, stdout=subprocess.PIPE) as process:
                    browser_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string_terminal = re.findall("Opera.*", browser_version_terminal)

                browser_version_terminal = find_string_terminal[0] if len(find_string_terminal) > 0 else ''

            elif platform.system() == 'Darwin':

                with subprocess.Popen([operabrowser_path, '--version'], stdout=subprocess.PIPE) as process:
                    browser_version_terminal = process.communicate()[0].decode('UTF-8')

            find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], browser_version_terminal)
            browser_version = find_string[0] if len(find_string) > 0 else ''

        return browser_version
