#pylint: disable=logging-fstring-interpolation
#Standart library imports
import subprocess
import time
import os
import re
from typing import Tuple, Any
from pathlib import Path
import platform
import shutil

#Third party imports
import wget

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
        """Main function, checks for the latest version, downloads or updates edge browser"""

        if self.check_browser_is_up_to_date:
            self._check_if_edge_browser_is_up_to_date()

    def _check_if_edge_browser_is_up_to_date(self) -> None:
        """Сhecks for the latest version of edge browser"""

        try:

            if platform.system() not in ['Darwin']:
                message = 'Edge browser checking/updating is currently disabled for your OS. Please wait for the new releases.'
                logger.error(message)
                return

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

        """

        latest_version : str = ''

        url = self.setting['EdgeDriver']["LinkLastRelease"]
        json_data = self.requests_getter.get_result_by_request(url=url)

        latest_version = str(json_data).strip()

        logger.info(f'Latest version of edge browser: {latest_version}')

        return latest_version

    def _get_latest_edge_browser_for_current_os(self) -> None:
        """Trying to update edge browser to its latest version"""

        if platform.system() not in ['Darwin']:
            message = 'Edge browser checking/updating is currently disabled for your OS. Please wait for the new releases.'
            logger.error(message)
            return

        url_release = self.setting["EdgeBrowser"]["LinkAllLatestReleaseFile"]
        latest_version = self._get_latest_version_edge_browser()

        path = self.edgedriver_path.replace(self.edgedriver_path.split(os.path.sep)[-1], '') + 'selenium-driver-updater' + os.path.sep
        archive_name = f'MicrosoftEdge-{latest_version}.pkg'

        if not Path(path).exists():
            Path(path).mkdir()

        if Path(path + archive_name).exists():
            Path(path + archive_name).unlink()

        logger.info(f'Started to download edge browser by url: {url_release}')
        package_path = wget.download(url=url_release, out=path + archive_name)

        logger.info(f'Edge browser was downloaded to path: {package_path}')

        if platform.system() == 'Darwin':

            logger.info('Trying to kill all edgebrowser processes')
            subprocess.Popen(r'killall Microsoft\ Edge', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info('Successfully killed all edgebrowser processes')

            package_expanded_path = f'{path}expanded{os.path.sep}'

            if Path(package_expanded_path).exists():
                shutil.rmtree(package_expanded_path)

            logger.info(f'Trying to expand package: {package_path}')
            os.system(f'pkgutil --expand {package_path} {package_expanded_path}')
            logger.info(f'Successfully unpacked package at path: {package_expanded_path}')

            package_expanded_payload_path = package_expanded_path + 'expanded_payload'

            if not Path(package_expanded_payload_path).exists():
                Path(package_expanded_payload_path).mkdir()

            subprocess.Popen(f'tar -xvf {package_expanded_path + archive_name}/Payload -C {package_expanded_payload_path}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            time.sleep(5)

            edge_browser_path = package_expanded_payload_path + os.path.sep + 'Microsoft Edge.app'

            edge_browser_path_application = '/Applications/Microsoft Edge.app'

            if Path(edge_browser_path_application).exists():
                shutil.rmtree(edge_browser_path_application)
            shutil.move(edge_browser_path, edge_browser_path_application)

            logger.info(f'Successfully moved edge browser from: {edge_browser_path} to: {edge_browser_path_application}')

            if Path(package_path).exists():
                Path(package_path).unlink()

            if Path(package_expanded_path).exists():
                shutil.rmtree(package_expanded_path)

    def _compare_current_version_and_latest_version_edge_browser(self) -> Tuple[bool, str, str]:
        """Compares current version of edge browser to latest version

        Returns:
            Tuple of bool, str and str

            is_browser_up_to_date (bool)    : It true the browser is up to date. Defaults to False.
            current_version (str)           : Current version of the browser.
            latest_version (str)            : Latest version of the browser.

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
