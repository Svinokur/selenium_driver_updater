#Standart library imports
import subprocess
import traceback
import logging
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
from _setting import setting

from util.requests_getter import RequestsGetter

class EdgeBrowser():
    """Class for working with Edge browser"""

    def __init__(self, **kwargs):
        self.setting : Any = setting
        self.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date'))

        self.edgedriver_path = str(kwargs.get('path'))

        self.requests_getter = RequestsGetter

    def main(self):
        """Main function, checks for the latest version, downloads or updates edge browser

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where phantomjs was downloaded or updated.

        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''

        try:

            if self.check_browser_is_up_to_date:
                result, message = self.__check_if_edge_browser_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message


            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __check_if_edge_browser_is_up_to_date(self) -> Tuple[bool, str]:
        """Сhecks for the latest version of edge browser

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.

        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''

        try:

            edgebrowser_updater_path = str(self.setting["EdgeBrowser"]["EdgeBrowserUpdaterPath"])
            if not edgebrowser_updater_path:
                message = 'Parameter "check_browser_is_up_to_date" has not been optimized for your OS yet. Please wait for the new releases.'
                logging.info(message)
                return True, message

            if not Path(edgebrowser_updater_path).exists():
                message = f'edgebrowser_updater_path: {edgebrowser_updater_path} is not exists. Please report your OS information and path to {edgebrowser_updater_path} file in repository.'
                logging.info(message)
                return True, message

            result, message, is_browser_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_edge_browser()
            if not result:
                logging.error(message)
                return result, message

            if not is_browser_up_to_date:

                result, message = self.__get_latest_edge_browser_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message

                result, message, is_browser_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_edge_browser()
                if not result:
                    logging.error(message)
                    return result, message

                if not is_browser_up_to_date:
                    message = f'Problem with updating edge browser current_version: {current_version} latest_version: {latest_version}'
                    logging.info(message)

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __get_current_version_edge_browser_selenium(self) -> Tuple[bool, str, str]:
        """Gets current edge browser version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            browser_version (str)   : Current edge browser version.

        Raises:
            SessionNotCreatedException: Occurs when current edgedriver could not start.

            WebDriverException: Occurs when current edgedriver could not start or critical error occured.

            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        browser_version : str = ''

        try:

            result, message, browser_version = self.__get_current_version_edge_browser_selenium_via_terminal()
            if not result:
                logging.error(message)
                message = 'Trying to get current version of edge browser via edgedriver'
                logging.info(message)

            if Path(self.edgedriver_path).exists() and (not result or not browser_version):

                desired_cap = {}

                driver = webdriver.Edge(executable_path = self.edgedriver_path, capabilities=desired_cap)
                browser_version = str(driver.capabilities['browserVersion'])
                driver.close()
                driver.quit()

            logging.info(f'Current version of edge browser: {browser_version}')

            result_run = True

        except SessionNotCreatedException:
            message_run = f'SessionNotCreatedException error: {traceback.format_exc()}'
            logging.error(message_run)
            return True, message_run, browser_version

        except WebDriverException:
            message_run = f'WebDriverException error: {traceback.format_exc()}'
            logging.error(message_run)
            return True, message_run, browser_version

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, browser_version

    def __get_latest_version_edge_browser(self) -> Tuple[bool, str, str]:
        """Gets latest edge browser version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            latest_version (str)    : Latest version of edge browser.

        Raises:
            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        latest_version : str = ''

        try:

            url = self.setting["EdgeBrowser"]["LinkAllLatestRelease"]
            result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
            if not result:
                logging.error(message)
                return result, message, latest_version

            soup = BeautifulSoup(json_data, 'html.parser')
            latest_version_element = soup.findAll('h2')[0].text

            latest_version = re.findall(self.setting["Program"]["wedriverVersionPattern"], latest_version_element)[0]

            logging.info(f'Latest version of edge browser: {latest_version}')

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __get_latest_edge_browser_for_current_os(self) -> Tuple[bool, str]:
        """Trying to update edge browser to its latest version

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.

        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''

        try:

            message = 'Trying to update edge browser to the latest version.'
            logging.info(message)

            os.system(self.setting["EdgeBrowser"]["EdgeBrowserUpdater"])
            time.sleep(60) #wait for the updating

            message = 'Edge browser was successfully updated to the latest version.'
            logging.info(message)

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __compare_current_version_and_latest_version_edge_browser(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of edge browser to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Empty string if function passed correctly, non-empty string if error.
            is_browser_up_to_date (bool)    : If true current version of edge browser is up to date. Defaults to False.

        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''
        is_browser_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''

        try:

            result, message, current_version = self.__get_current_version_edge_browser_selenium()
            if not result:
                logging.error(message)
                return result, message, is_browser_up_to_date, current_version, latest_version

            if not current_version:
                return True, message, True, current_version, latest_version

            result, message, latest_version = self.__get_latest_version_edge_browser()
            if not result:
                logging.error(message)
                return result, message, is_browser_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_browser_up_to_date = True
                message = f"Your existing edge browser is up to date. current_version: {current_version} latest_version: {latest_version}"
                logging.info(message)

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_browser_up_to_date, current_version, latest_version

    def __get_current_version_edge_browser_selenium_via_terminal(self) -> Tuple[bool, str, str]:
        """Gets current edge browser version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            browser_version (str)   : Current edge browser version.

        Raises:

            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        browser_version : str = ''
        browser_version_terminal : str = ''

        try:

            edgebrowser_path = self.setting["EdgeBrowser"]["Path"]
            if edgebrowser_path:

                logging.info('Trying to get current version of edge browser via terminal')


                if platform.system() == 'Darwin':

                    with subprocess.Popen([edgebrowser_path, '--version'], stdout=subprocess.PIPE) as process:
                        browser_version_terminal = process.communicate()[0].decode('UTF-8')

                elif platform.system() == 'Windows':

                    with subprocess.Popen(edgebrowser_path, stdout=subprocess.PIPE) as process:
                        browser_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], browser_version_terminal)
                browser_version = find_string[0] if len(find_string) > 0 else ''

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, browser_version
