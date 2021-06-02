import subprocess
import os
import traceback
import logging
import time
import os

import platform

from typing import Tuple

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from _setting import setting

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

from util.extractor import Extractor
from util.requests_getter import RequestsGetter

from bs4 import BeautifulSoup

import re

class FirefoxBrowser():

    def __init__(self, path : str, check_browser_is_up_to_date : bool):
        self.setting = setting
        self.check_browser_is_up_to_date = check_browser_is_up_to_date

        self.geckodriver_path = path
        self.extractor = Extractor
        self.requests_getter = RequestsGetter

    def main(self):
        result_run : bool = False
        message_run : str = ''
        
        try:

            if self.check_browser_is_up_to_date:
                result, message = self.__check_if_firefox_browser_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message
        

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __check_if_firefox_browser_is_up_to_date(self) -> Tuple[bool, str]:
        """Сhecks for the latest version of firefox browser

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

            firefoxbrowser_updater_path = str(self.setting["FirefoxBrowser"]["FirefoxBrowserUpdaterPath"])
            if not firefoxbrowser_updater_path:
                message = f'Parameter "check_browser_is_up_to_date" has not been optimized for your OS yet. Please wait for the new releases.'
                logging.info(message)
                return True, message

            if not os.path.exists(firefoxbrowser_updater_path):
                message = f'firefoxbrowser_updater_path: {firefoxbrowser_updater_path} is not exists. Please report your OS information and path to {firefoxbrowser_updater_path} file in repository.'
                logging.info(message)
                return True, message

            result, message, is_browser_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_firefox_browser()
            if not result:
                logging.error(message)
                return result, message

            if not is_browser_up_to_date:

                result, message = self.__get_latest_firefox_browser_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message

                result, message, is_browser_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_firefox_browser()
                if not result:
                    logging.error(message)
                    return result, message

                if not is_browser_up_to_date:
                    message = f'Problem with updating firefox browser current_version: {current_version} latest_version: {latest_version}'
                    logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __get_current_version_firefox_browser_selenium(self) -> Tuple[bool, str, str]:
        """Gets current firefox browser version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            browser_version (str)   : Current firefox browser version.

        Raises:
            SessionNotCreatedException: Occurs when current geckodriver could not start.

            WebDriverException: Occurs when current geckodriver could not start or critical error occured.

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        browser_version : str = ''
        
        try:
            
            result, message, browser_version = self.__get_current_version_firefox_browser_selenium_via_terminal()
            if not result:
                logging.error(message)
                message = 'Trying to get current version of firefox browser via geckodriver'
                logging.info(message)
            
            if os.path.exists(self.geckodriver_path) and not result or not browser_version:

                options = FirefoxOptions()
                options.add_argument("--headless")

                driver = webdriver.Firefox(executable_path = self.geckodriver_path, options=options)
                browser_version = str(driver.capabilities['browserVersion'])
                driver.close()
                driver.quit()

            logging.info(f'Current version of firefox browser: {browser_version}')

            result_run = True

        except SessionNotCreatedException:
            message_run = f'SessionNotCreatedException error: {traceback.format_exc()}'
            logging.error(message_run)
            return True, message_run, browser_version

        except WebDriverException:
            message_run = f'WebDriverException error: {traceback.format_exc()}'
            logging.error(message_run)
            return True, message_run, browser_version

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)
        
        return result_run, message_run, browser_version

    def __get_latest_version_firefox_browser(self) -> Tuple[bool, str, str]:
        """Gets latest firefox browser version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            latest_version (str)    : Latest version of firefox browser.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_version : str = ''

        try:
            
            url = self.setting["FirefoxBrowser"]["LinkAllLatestReleases"]
            result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
            if not result:
                logging.error(message)
                return result, message, latest_version

            soup = BeautifulSoup(json_data, 'html.parser')
            element_releases_list = soup.findAll('ol', attrs={'class' : 'c-release-list'})[0]

            all_releases_elements = element_releases_list.findAll('a', attrs={'href' : re.compile('/releasenotes/')})
            all_releases = []

            [all_releases.append(release.text) for release in all_releases_elements]
            all_releases.sort(key=lambda s: list(map(int, s.split('.'))), reverse=True)

            latest_version = all_releases[0]
            
            logging.info(f'Latest version of firefox browser: {latest_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __get_latest_firefox_browser_for_current_os(self) -> Tuple[bool, str]:
        """Trying to update firefox browser to its latest version

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
            is_admin : bool = True if os.getuid() == 0 else False
        except:
            is_admin : bool = False
            
        update_command : str = self.setting["FirefoxBrowser"]["FirefoxBrowserUpdater"]
        
        try:

            message = f'Trying to update firefox browser to the latest version.'
            logging.info(message)

            if platform.system() == 'Linux':

                if is_admin:
                    os.system(update_command)

                elif not is_admin:
                    message = 'You have not ran library with sudo privileges to update firefox browser - so updating is impossible.'
                    logging.error(message)
                    return True, message_run
            
            else:

                os.system(update_command)
                time.sleep(60) #wait for the updating - too long
            
            message = f'Firefox browser was successfully updated to the latest version.'
            logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __compare_current_version_and_latest_version_firefox_browser(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of firefox browser to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Empty string if function passed correctly, non-empty string if error.
            is_browser_up_to_date (bool)    : If true current version of firefox browser is up to date. Defaults to False.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        is_browser_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''
        
        try:

            result, message, current_version = self.__get_current_version_firefox_browser_selenium()
            if not result:
                logging.error(message)
                return result, message, is_browser_up_to_date, current_version, latest_version

            result, message, latest_version = self.__get_latest_version_firefox_browser()
            if not result:
                logging.error(message)
                return result, message, is_browser_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_browser_up_to_date = True
                message = f"Your existing firefox browser is up to date. current_version: {current_version} latest_version: {latest_version}"
                logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_browser_up_to_date, current_version, latest_version

    def __get_current_version_firefox_browser_selenium_via_terminal(self) -> Tuple[bool, str, str]:
        """Gets current firefox browser version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            browser_version (str)   : Current firefox browser version.

        Raises:

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        browser_version : str = ''
        browser_version_terminal : str = ''
        
        try:
            
            firefox_path = self.setting["FirefoxBrowser"]["Path"]
            if firefox_path:

                logging.info('Trying to get current version of firefox browser via terminal')

                if platform.system() == 'Windows':

                    for command in firefox_path:

                        process = subprocess.Popen(command, stdout=subprocess.PIPE)
            
                        browser_version_terminal = process.communicate()[0].decode('UTF-8')

                        if not 'invalid' in browser_version_terminal.lower():
                            break

                elif platform.system() == 'Darwin':
                    process = subprocess.Popen([firefox_path, '--version'], stdout=subprocess.PIPE)
            
                    browser_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string = re.findall(self.setting["FirefoxBrowser"]["FirefoxBrowserVersionPattern"], browser_version_terminal)
                browser_version = find_string[0] if len(find_string) > 0 else ''

                if not browser_version:
                    find_string = re.findall(self.setting["FirefoxBrowser"]["FirefoxBrowserVersionPattern2"], browser_version_terminal)
                    browser_version = find_string[0] if len(find_string) > 0 else ''

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)
        
        return result_run, message_run, browser_version