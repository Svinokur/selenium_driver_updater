#Standart library imports
import subprocess
import traceback
import logging
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
from _setting import setting
from util.extractor import Extractor
from util.requests_getter import RequestsGetter

class ChromeBrowser():
    """Class for working with Chrome browser"""

    def __init__(self, **kwargs):
        self.setting : Any = setting
        self.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date'))

        self.chromedriver_path = str(kwargs.get('path'))
        self.extractor = Extractor
        self.requests_getter = RequestsGetter

    def main(self):
        """Main function, checks for the latest version, downloads or updates chrome browser

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
                result, message = self.__check_if_chrome_browser_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __check_if_chrome_browser_is_up_to_date(self) -> Tuple[bool, str]:
        """Сhecks for the latest version of chrome browser

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''

        try:

            if platform.system() != 'Linux':

                chromebrowser_updater_path = str(self.setting["ChromeBrowser"]["ChromeBrowserUpdaterPath"])
                if not chromebrowser_updater_path:
                    message = 'Parameter "check_browser_is_up_to_date" has not been optimized for your OS yet. Please wait for the new releases.'
                    logging.info(message)
                    return True, message

                if not Path(chromebrowser_updater_path).exists():
                    message = f'chromebrowser_updater_path: {chromebrowser_updater_path} is not exists. Please report your OS information and path to {chromebrowser_updater_path} file in repository.'
                    logging.info(message)
                    return True, message

            result, message, is_browser_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_chrome_browser()
            if not result:
                logging.error(message)
                return result, message

            if not is_browser_up_to_date:

                result, message = self.__get_latest_chrome_browser_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message

                result, message, is_browser_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_chrome_browser()
                if not result:
                    logging.error(message)
                    return result, message

                if not is_browser_up_to_date:
                    message = f'Problem with updating chrome browser current_version: {current_version} latest_version: {latest_version}'
                    logging.info(message)

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __compare_current_version_and_latest_version_chrome_browser(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of chrome browser to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Returns an error message if an error occurs in the function.
            is_browser_up_to_date (bool)    : If true current version of chrome browser is up to date. Defaults to False.

        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''
        is_browser_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''

        try:

            result, message, current_version = self.__get_current_version_chrome_browser_selenium()
            if not result:
                logging.error(message)
                return result, message, is_browser_up_to_date, current_version, latest_version

            if not current_version:
                return True, message, True, current_version, latest_version

            result, message, latest_version = self.__get_latest_version_chrome_browser()
            if not result:
                logging.error(message)
                return result, message, is_browser_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_browser_up_to_date = True
                message = f"Your existing chrome browser is up to date. current_version: {current_version} latest_version: {latest_version}"
                logging.info(message)

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_browser_up_to_date, current_version, latest_version

    def __get_current_version_chrome_browser_selenium(self) -> Tuple[bool, str, str]:
        """Gets current chrome browser version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
            browser_version (str)   : Current chrome browser version.

        Raises:
            SessionNotCreatedException: Occurs when current chromedriver could not start.

            WebDriverException: Occurs when current chromedriver could not start or critical error occured.

            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        browser_version : str = ''

        try:

            result, message, browser_version = self.__get_current_version_chrome_browser_selenium_via_terminal()
            if not result:
                logging.error(message)
                message = 'Trying to get current version of chrome browser via chromedriver'
                logging.info(message)

            if Path(self.chromedriver_path).exists() and (not result or not browser_version):

                chrome_options = webdriver.ChromeOptions()

                chrome_options.add_argument('--headless')

                driver = webdriver.Chrome(executable_path = self.chromedriver_path, options = chrome_options)
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

    def __get_current_version_chrome_browser_selenium_via_terminal(self) -> Tuple[bool, str, str]:
        """Gets current chrome browser version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
            browser_version (str)   : Current chrome browser version.

        Raises:

            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        browser_version : str = ''
        browser_version_terminal : str = ''

        try:

            chromebrowser_path = self.setting["ChromeBrowser"]["Path"]
            if chromebrowser_path:

                logging.info('Trying to get current version of chrome browser via terminal')

                if platform.system() == 'Windows':

                    for command in chromebrowser_path:

                        with subprocess.Popen(command, stdout=subprocess.PIPE) as process:
                            browser_version_terminal = process.communicate()[0].decode('UTF-8')

                        if 'invalid' not in browser_version_terminal.lower():
                            break

                elif platform.system() in ['Linux', 'Darwin']:

                    with subprocess.Popen([chromebrowser_path, '--version'], stdout=subprocess.PIPE) as process:
                        browser_version_terminal = process.communicate()[0].decode('UTF-8')


                find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], browser_version_terminal)
                browser_version = find_string[0] if len(find_string) > 0 else ''

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, browser_version

    def __get_latest_version_chrome_browser(self, no_messages : bool = False) -> Tuple[bool, str, str]:
        """Gets latest chrome browser version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            latest_version (str)    : Latest version of chrome browser.

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

                    current_os = platform.system().replace('Darwin', 'Mac')
                    if not current_os.lower() in news.text.lower():
                        continue

                    latest_stable_version_element = news.text
                    break

            if not latest_stable_version_element:
                message = f'Could not determine latest stable channel post of Chrome Browser. Maybe the text "{stable_channel_header_text}" is changed'
                logging.error(message)

                message = 'Trying to determine latest stable channel post of Chrome Browser without OS detection'
                logging.info(message)

                latest_stable_version_element = [news.text for news in elements_news if stable_channel_header_text in news.text][0]
                if not latest_stable_version_element:
                    return result_run, message, latest_version

            latest_version = re.findall(self.setting["Program"]["wedriverVersionPattern"], latest_stable_version_element)[0]

            if not no_messages:

                logging.info(f'Latest version of chrome browser: {latest_version}')

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __get_latest_chrome_browser_for_current_os(self) -> Tuple[bool, str]:
        """Trying to update chrome browser to its latest version

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.

        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''
        try:
            is_admin : bool = bool(os.getuid() == 0)
        except Exception:
            is_admin : bool = False

        update_command : str = self.setting["ChromeBrowser"]["ChromeBrowserUpdater"]

        try:

            message = 'Trying to update chrome browser to the latest version.'
            logging.info(message)

            if platform.system() == 'Linux':

                if is_admin:
                    os.system(update_command)

                elif not is_admin:
                    message = 'You have not ran library with sudo privileges to update chrome browser - so updating is impossible.'
                    logging.error(message)
                    return True, message_run

            else:

                os.system(update_command)
                time.sleep(60) #wait for the updating

            message = 'Chrome browser was successfully updated to the latest version.'
            logging.info(message)

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
