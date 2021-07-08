#Standart library imports
import subprocess
import traceback
import logging
import os
import re
from typing import Tuple, Any

# Third party imports
from bs4 import BeautifulSoup

# Selenium imports
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

# Local imports
from _setting import setting
from util.requests_getter import RequestsGetter

class ChromiumChromeBrowser():
    """Class for working with Chromium browser"""

    def __init__(self, **kwargs):
        self.setting : Any = setting
        self.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date'))

        self.requests_getter = RequestsGetter

    def main(self):
        """Main function, checks for the latest version, downloads or updates chromium browser

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
                result, message = self.__check_if_chromiumbrowser_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message


            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __check_if_chromiumbrowser_is_up_to_date(self) -> Tuple[bool, str]:
        """Сhecks for the latest version of chromiumbrowser

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

            result, message, is_browser_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_chromiumbrowser()
            if not result:
                logging.error(message)
                return result, message

            if not is_browser_up_to_date:

                result, message = self.__get_latest_chromium_browser_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message

                result, message, is_browser_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_chromiumbrowser()
                if not result:
                    logging.error(message)
                    return result, message

                if not is_browser_up_to_date:
                    message = f'Problem with updating chromium_browser current_version: {current_version} latest_version: {latest_version}'
                    logging.info(message)

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __compare_current_version_and_latest_version_chromiumbrowser(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of chromiumbrowser to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Empty string if function passed correctly, non-empty string if error.
            is_browser_up_to_date (bool)    : If true current version of chromiumbrowser is up to date. Defaults to False.

        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''
        is_browser_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''

        try:

            result, message, current_version = self.__get_current_version_chromiumbrowser_selenium()
            if not result:
                logging.error(message)
                return result, message, is_browser_up_to_date, current_version, latest_version

            if not current_version:
                return True, message, True, current_version, latest_version

            result, message, latest_version = self.__get_latest_version_chromiumbrowser()
            if not result:
                logging.error(message)
                return result, message, is_browser_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_browser_up_to_date = True
                message = (f"Your existing chromiumbrowser is up to date."
                            f"current_version: {current_version} latest_version: {latest_version}")
                logging.info(message)

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_browser_up_to_date, current_version, latest_version

    def __get_current_version_chromiumbrowser_selenium(self) -> Tuple[bool, str, str]:
        """Gets current chromiumbrowser version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            browser_version (str)   : Current chromiumbrowser version.

        Raises:
            SessionNotCreatedException: Occurs when current chromedriver could not start.

            WebDriverException: Occurs when current chromedriver could not start or critical error occured.

            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        browser_version : str = ''

        try:

            result, message, browser_version = self.__get_current_version_chromiumbrowser_via_terminal()
            if not result:
                logging.error(message)
                message = 'Trying to get current version of chromiumbrowser via chromium_chromedriver'
                logging.info(message)

            if not result or not browser_version:

                chrome_options = webdriver.ChromeOptions()

                chrome_options.add_argument('--headless')

                driver = webdriver.Chrome(options = chrome_options)
                browser_version = str(driver.capabilities['browserVersion'])
                driver.close()
                driver.quit()

            logging.info(f'Current version of chrome browser: {browser_version}')

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

    def __get_current_version_chromiumbrowser_via_terminal(self) -> Tuple[bool, str, str]:
        """Gets current chromiumbrowser version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            browser_version (str)   : Current chromiumbrowser version.

        Raises:

            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        browser_version : str = ''
        browser_version_terminal : str = ''

        try:


            logging.info('Trying to get current version of chromium browser via terminal')

            with subprocess.Popen(self.setting["ChromiumBrowser"]["Path"] + ' --version', stdout=subprocess.PIPE, shell=True) as process:
                browser_version_terminal = process.communicate()[0].decode('UTF-8')

            find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], browser_version_terminal)
            browser_version = find_string[0] if len(find_string) > 0 else ''

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, browser_version

    def __get_latest_version_chromiumbrowser(self) -> Tuple[bool, str, str]:
        """Gets latest chromiumbrowser version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            latest_version (str)    : Latest version of chromiumbrowser.

        Raises:
            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        latest_version : str = ''
        latest_stable_version_element : Any = ''

        try:

            url = self.setting["ChromeBrowser"]["LinkAllLatestRelease"]
            result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
            if not result:
                logging.error(message)
                return result, message, latest_version

            soup = BeautifulSoup(json_data, 'html.parser')
            elements_news = soup.findAll('div', attrs={'class' : 'post'})
            stable_channel_header_text = 'Stable Channel Update for Desktop'

            for news in elements_news:
                if stable_channel_header_text in news.text:
                    latest_stable_version_element = news.text.replace('\n', '').replace('\xa0', '')
                    break

            if not latest_stable_version_element:
                message = f'Could not determine latest stable channel post of Chrome Browser. Maybe the text "{stable_channel_header_text}" is changed'
                logging.error(message)
                return result_run, message, latest_version

            latest_version = re.findall(self.setting["Program"]["wedriverVersionPattern"], latest_stable_version_element)[0]

            logging.info(f'Latest version of chromiumbrowser: {latest_version}')

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __get_latest_chromium_browser_for_current_os(self) -> Tuple[bool, str]:
        """Trying to update chromium_browser to its latest version

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

            message = 'Trying to update chromium_browser to the latest version.'
            logging.info(message)

            os.system(self.setting["ChromeBrowser"]["ChromeBrowserUpdater"])

            message = 'Chrome browser was successfully updated to the latest version.'
            logging.info(message)

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
        