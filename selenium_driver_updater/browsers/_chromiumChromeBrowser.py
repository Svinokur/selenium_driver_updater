#pylint: disable=logging-fstring-interpolation
#Standart library imports
import subprocess
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
from selenium_driver_updater._setting import setting

from selenium_driver_updater.util.requests_getter import RequestsGetter
from selenium_driver_updater.util.logger import logger

class ChromiumChromeBrowser():
    """Class for working with Chromium browser"""

    def __init__(self, **kwargs):
        self.setting : Any = setting
        self.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date'))

        self.requests_getter = RequestsGetter

    def main(self) -> None:
        """Main function, checks for the latest version, downloads or updates chromium browser"""

        if self.check_browser_is_up_to_date:
            self._check_if_chromiumbrowser_is_up_to_date()

    def _check_if_chromiumbrowser_is_up_to_date(self) -> None:
        """Сhecks for the latest version of chromiumbrowser

        Raises:
            Except: If unexpected error raised.

        """

        is_browser_up_to_date, current_version, latest_version = self._compare_current_version_and_latest_version_chromiumbrowser()

        if not is_browser_up_to_date:

            self._get_latest_chromium_browser_for_current_os()

            is_browser_up_to_date, current_version, latest_version = self._compare_current_version_and_latest_version_chromiumbrowser()

            if not is_browser_up_to_date:
                message = f'Problem with updating chromium_browser current_version: {current_version} latest_version: {latest_version}'
                logger.info(message)

    def _compare_current_version_and_latest_version_chromiumbrowser(self) -> Tuple[bool, str, str]:
        """Compares current version of chromiumbrowser to latest version

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

        current_version = self._get_current_version_chromiumbrowser_selenium()

        if not current_version:
            return True, current_version, latest_version

        latest_version = self._get_latest_version_chromiumbrowser()

        if current_version == latest_version:
            is_browser_up_to_date = True
            message = (f"Your existing chromiumbrowser is up to date."
                        f"current_version: {current_version} latest_version: {latest_version}")
            logger.info(message)

        return is_browser_up_to_date, current_version, latest_version

    def _get_current_version_chromiumbrowser_selenium(self) -> str:
        """Gets current chromiumbrowser version


        Returns:
            str

            browser_version (str)   : Current chromiumbrowser version.

        Raises:
            SessionNotCreatedException: Occurs when current chromedriver could not start.

            WebDriverException: Occurs when current chromedriver could not start or critical error occured.

            Except: If unexpected error raised.

        """

        browser_version : str = ''

        try:

            browser_version = self._get_current_version_chromiumbrowser_via_terminal()
            if not browser_version:
                message = 'Trying to get current version of chromiumbrowser via chromium_chromedriver'
                logger.info(message)

            if not browser_version:

                chrome_options = webdriver.ChromeOptions()

                chrome_options.add_argument('--headless')

                with webdriver.Chrome(options = chrome_options) as driver:
                    browser_version = str(driver.capabilities['browserVersion'])

            logger.info(f'Current version of chrome browser: {browser_version}')

        except (WebDriverException, SessionNotCreatedException, OSError):
            pass #[Errno 86] Bad CPU type in executable:

        return browser_version

    def _get_current_version_chromiumbrowser_via_terminal(self) -> str:
        """Gets current chromiumbrowser version via command in terminal


        Returns:
            str

            browser_version (str)   : Current chromiumbrowser version.

        Raises:

            Except: If unexpected error raised.

        """

        browser_version : str = ''
        browser_version_terminal : str = ''


        logger.info('Trying to get current version of chromium browser via terminal')

        with subprocess.Popen(self.setting["ChromiumBrowser"]["Path"] + ' --version', stdout=subprocess.PIPE, shell=True) as process:
            browser_version_terminal = process.communicate()[0].decode('UTF-8')

        find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], browser_version_terminal)
        browser_version = find_string[0] if len(find_string) > 0 else ''

        return browser_version

    def _get_latest_version_chromiumbrowser(self) -> str:
        """Gets latest chromiumbrowser version


        Returns:
            str

            latest_version (str)    : Latest version of chromiumbrowser.

        Raises:
            Except: If unexpected error raised.

        """

        latest_version : str = ''
        latest_stable_version_element : Any = ''

        url = self.setting["ChromeBrowser"]["LinkAllLatestRelease"]
        json_data = self.requests_getter.get_result_by_request(url=url)

        soup = BeautifulSoup(json_data, 'html.parser')
        elements_news = soup.findAll('div', attrs={'class' : 'post'})
        stable_channel_header_text = 'Stable Channel Update for Desktop'

        for news in elements_news:
            if stable_channel_header_text in news.text:
                latest_stable_version_element = news.text.replace('\n', '').replace('\xa0', '')
                break

        if not latest_stable_version_element:
            message = f'Could not determine latest stable channel post of Chrome Browser. Maybe the text "{stable_channel_header_text}" is changed'
            logger.error(message)

        latest_version = re.findall(self.setting["Program"]["wedriverVersionPattern"], latest_stable_version_element)[0]

        logger.info(f'Latest version of chromiumbrowser: {latest_version}')

        return latest_version

    def _get_latest_chromium_browser_for_current_os(self) -> None:
        """Trying to update chromium_browser to its latest version"""

        message = 'Trying to update chromium_browser to the latest version.'
        logger.info(message)

        os.system(self.setting["ChromeBrowser"]["ChromeBrowserUpdater"])

        message = 'Chrome browser was successfully updated to the latest version.'
        logger.info(message)
        