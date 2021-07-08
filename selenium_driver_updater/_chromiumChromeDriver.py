#Standart library imports
import subprocess
import os
import traceback
import logging
import re
from typing import Tuple, Any

# Third party imports
import platform
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

# Local imports
from _setting import setting

from util.requests_getter import RequestsGetter

from browsers._chromiumChromeBrowser import ChromiumChromeBrowser

class ChromiumChromeDriver():
    """Class for working with Selenium chromedriver binary"""

    def __init__(self, **kwargs):

        self.setting : Any = setting

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))

        self.chromium_chromedriver_name = 'chromedriver'

        self.requests_getter = RequestsGetter

        self.chromium_chromebrowser = ChromiumChromeBrowser(**kwargs)

    def main(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates chromium chromedriver binary or
        downloads specific version of chromium chromedriver.

        Returns:
            Tuple of bool, str and str

            result_run (bool) : True if function passed correctly, False otherwise.
            message_run (str) : Returns an error message if an error occurs in the function.
            driver_path (str) : Path where chromium chromedriver was downloaded or updated.

        Raises:
            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''
        try:
            is_admin : bool = bool(os.getuid() == 0)
        except Exception:
            is_admin : bool = False

        try:

            if platform.system() != 'Linux':
                message = 'chromium_chromedriver webdriver downloading/updating is only supported for Linux only. Please wait for the new releases.'
                logging.error(message)
                return False, message, driver_path

            if not is_admin:
                message = 'You have not ran library with sudo privileges to download or update chromium_chromedriver - so that is impossible.'
                logging.error(message)
                return False, message, driver_path

            result, message = self.chromium_chromebrowser.main()
            if not result:
                logging.error(message)
                return result, message, driver_path

            result, message, driver_path = self.__check_if_chromedriver_is_up_to_date()
            if not result:
                logging.error(message)
                return result, message, driver_path

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __get_latest_version_chromium_chromedriver(self) -> Tuple[bool, str, str]:
        """Gets latest chromium_chromedriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
            latest_version (str)    : Latest version of chromedriver.

        Raises:
            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        latest_version : str = ''

        try:

            url = self.setting["ChromeDriver"]["LinkLastRelease"]
            result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
            if not result:
                logging.error(message)
                return result, message, latest_version

            latest_version = str(json_data)

            logging.info(f'Latest version of chromium_chromedriver: {latest_version}')

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __get_current_version_chromium_chromedriver(self) -> Tuple[bool, str, str]:
        """Gets current chromium_chromedriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
            driver_version (str)    : Current chromium_chromedriver version.

        Raises:
            SessionNotCreatedException: Occurs when current chromium_chromedriver could not start.

            WebDriverException: Occurs when current chromedriver could not start or critical error occured.

            OSError: Occurs when chromium_chromedriver made for another CPU type

            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''

        try:

            result, message, driver_version = self.__get_current_version_chromium_chromedriver_via_terminal()
            if not result:
                logging.error(message)
                message = 'Trying to get current version of chromium_chromedriver via webdriver'
                logging.info(message)

            if not result or not driver_version:

                chrome_options = webdriver.ChromeOptions()

                chrome_options.add_argument('--headless')

                driver = webdriver.Chrome(options = chrome_options)
                driver_version = str(driver.capabilities['chrome']['chromedriverVersion'].split(" ")[0])
                driver.close()
                driver.quit()

            logging.info(f'Current version of chromium_chromedriver: {driver_version}')

            result_run = True

        except SessionNotCreatedException:
            message_run = f'SessionNotCreatedException error: {traceback.format_exc()}'
            logging.error(message_run)
            return True, message_run, driver_version

        except WebDriverException:
            message_run = f'WebDriverException error: {traceback.format_exc()}'
            logging.error(message_run)
            return True, message_run, driver_version

        except OSError:
            message_run = f'OSError error: {traceback.format_exc()}' #probably [Errno 86] Bad CPU type in executable:
            logging.error(message_run)
            return True, message_run, driver_version

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_version

    def __get_current_version_chromium_chromedriver_via_terminal(self) -> Tuple[bool, str, str]:
        """Gets current chromium_chromedriver version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
            driver_version (str)    : Current chromium_chromedriver version.

        Raises:

            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''
        driver_version_terminal : str = ''

        try:

            logging.info('Trying to get current version of chromium_chromedriver via terminal')

            with subprocess.Popen(self.chromium_chromedriver_name + ' --version', stdout=subprocess.PIPE, shell=True) as process:
                driver_version_terminal = process.communicate()[0].decode('UTF-8')

            find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_terminal)
            driver_version = find_string[0] if len(find_string) > 0 else ''

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_version

    def __compare_current_version_and_latest_version(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of chromium_chromedriver to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Returns an error message if an error occurs in the function.
            is_driver_up_to_date (bool) : If true current version of chromium_chromedriver is up to date. Defaults to False.

        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''
        is_driver_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''

        try:

            result, message, current_version = self.__get_current_version_chromium_chromedriver()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

            result, message, latest_version = self.__get_latest_version_chromium_chromedriver()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_driver_up_to_date = True
                message = ('Your existing chromium_chromedriver is up to date.'
                            f'current_version: {current_version} latest_version: {latest_version}')
                logging.info(message)

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_driver_up_to_date, current_version, latest_version

    def __check_if_chromedriver_is_up_to_date(self) -> Tuple[bool, str, str]:
        """Сhecks for the latest version, downloads or updates chromedriver binary

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
            driver_path (str)       : Path where chromedriver was downloaded or updated.

        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''

        try:

            if self.check_driver_is_up_to_date:

                result, message, is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if is_driver_up_to_date:
                    return True, message, ''

            result, message, driver_path = self.__get_latest_chromium_chromedriver_for_current_os()
            if not result:
                logging.error(message)
                return result, message, driver_path

            if self.check_driver_is_up_to_date:

                result, message, is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if not is_driver_up_to_date:
                    message = f'Problem with updating chromedriver current_version: {current_version} latest_version: {latest_version}'
                    logging.error(message)
                    return result_run, message, driver_path

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __get_latest_chromium_chromedriver_for_current_os(self) -> Tuple[bool, str, str]:
        """Downloads latest chromium_chromedriver to specific path

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
            driver_path (str)       : Path where chromedriver was downloaded or updated.

        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''

        try:

            message = 'Trying to update chromium_chromedriver to the latest version.'
            logging.info(message)

            os.system(self.setting["ChromiumChromeDriver"]["ChromiumChromeDriverUpdater"])

            message = 'Chromium_chromedriver was successfully updated to the latest version.'
            logging.info(message)

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path
