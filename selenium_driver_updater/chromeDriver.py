import requests
import wget
import os
import traceback
import logging
import time
import stat
import os

import platform

from typing import Any, Tuple

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from _setting import setting

from selenium import webdriver

from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

from util.extractor import Extractor

from bs4 import BeautifulSoup

import pathlib

class ChromeDriver():

    _tmp_folder_path = 'tmp'
    
    def __init__(self, path : str, **kwargs):
        """Class for working with Selenium chromedriver binary

        Args:
            path (str)                          : Specified path which will used for downloading or updating Selenium chromedriver binary. Must be folder path.
            upgrade (bool)                      : If true, it will overwrite existing driver in the folder. Defaults to False.
            chmod (bool)                        : If true, it will make chromedriver binary executable. Defaults to True.
            check_driver_is_up_to_date (bool)   : If true, it will check driver version before and after upgrade. Defaults to False.
            filename (str)                      : Specific name for chromedriver. If given, it will replace name for chromedriver.
            version (str)                       : Specific version for chromedriver. If given, it will downloads given version.
            check_driver_is_up_to_date (bool)   : If true, it will check chrome browser version before chromedriver update/upgrade.
        """
        self.setting = setting

        self.path : str = path
                    
        self.upgrade : bool = bool(kwargs.get('upgrade'))

        self.chmod : bool = bool(kwargs.get('chmod'))

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))

        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/35.0.1916.47 Safari/537.36'

        self.headers = {'User-Agent': user_agent}
        
        specific_filename = str(kwargs.get('filename'))
        self.filename = f"{specific_filename}.exe" if platform.system() == 'Windows' and specific_filename else\
                        specific_filename

        self.chromedriver_path : str =  self.path + self.setting['ChromeDriver']['LastReleasePlatform'] if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.extractor = Extractor
        
        self.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date'))

    def __get_latest_version_chrome_driver(self, no_messages : bool = False) -> Tuple[bool, str, str]:
        """Gets latest chromedriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            latest_version (str)    : Latest version of chromedriver.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_version : str = ''

        try:
            
            url = self.setting["ChromeDriver"]["LinkLastRelease"]
            request = requests.get(url=url, headers=self.headers)
            status_code = request.status_code

            if status_code != 200:
                message = f'status_code not equal 200 status_code : {status_code} request_text: {request.text}'
                return result_run, message, latest_version

            latest_version = str(request.text)

            if not no_messages:

                logging.info(f'Latest version of chromedriver: {latest_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __delete_current_chromedriver_for_current_os(self) -> Tuple[bool, str]:
        """Deletes chromedriver from folder if parameter "upgrade" is True


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''

        try:

            if os.path.exists(self.chromedriver_path):
                
                logging.info(f'Deleted existing chromedriver chromedriver_path: {self.chromedriver_path}')
                file_to_rem = pathlib.Path(self.chromedriver_path)
                file_to_rem.unlink()

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __get_latest_chromedriver_for_current_os(self, latest_version : str) -> Tuple[bool, str, str]:
        """Downloads latest chromedriver to specific path

        Args:
            latest_version (str)    : Latest version of chromedriver.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            file_name (str)         : Path where chromedriver was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        file_name : str = ''
        
        try:

            logging.info(f'Started download chromedriver latest_version: {latest_version}')

            url = self.setting["ChromeDriver"]["LinkLastReleaseFile"].format(latest_version)
            out_path = self.path + url.split('/')[4]

            if os.path.exists(out_path):
                os.remove(out_path)

            logging.info(f'Started download chromedriver by url: {url}')

            file_name = wget.download(url=url, out=out_path)

            logging.info(f'Chromedriver was downloaded to path: {file_name}')

            time.sleep(2)

            if not self.filename:
                
                archive_path = file_name
                out_path = self.path
                result, message = self.extractor.extract_all_zip_archive(archive_path=archive_path, out_path=out_path)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            else:

                archive_path = file_name
                out_path = self.path
                filename = self.setting['ChromeDriver']['LastReleasePlatform']
                filename_replace = self.filename
                result, message = self.extractor.extract_all_zip_archive_with_specific_name(archive_path=archive_path, 
                out_path=out_path, filename=filename, filename_replace=filename_replace)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            time.sleep(6)

            if os.path.exists(file_name):
                os.remove(file_name)

            
            file_name = self.chromedriver_path

            logging.info(f'Chromedriver was successfully unpacked by path: {file_name}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, file_name

    def __check_if_chromedriver_is_up_to_date(self) -> Tuple[bool, str, str]:
        """Сhecks for the latest version, downloads or updates chromedriver binary

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
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
                    return True, message, self.chromedriver_path

            else:

                result, message, latest_version = self.__get_latest_version_chrome_driver()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            if self.upgrade:

                result, message = self.__delete_current_chromedriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result, message, driver_path = self.__get_latest_chromedriver_for_current_os(latest_version)
            if not result:
                logging.error(message)
                return result, message, driver_path

            if self.chmod:

                result, message = self.__chmod_driver()
                if not result:
                    return result, message, driver_path

            if self.check_driver_is_up_to_date:

                result, message, is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if not is_driver_up_to_date:
                    message = f'Problem with updating chromedriver current_version : {current_version} latest_version : {latest_version}'
                    logging.error(message)
                    return result_run, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __get_current_version_chrome_selenium(self) -> Tuple[bool, str, str]:
        """Gets current chromedriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current chromedriver version.

        Raises:
            SessionNotCreatedException: Occurs when current chromedriver could not start.

            WebDriverException: Occurs when current chromedriver could not start or critical error occured.

            OSError: Occurs when chromedriver made for another CPU type

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''
        
        try:
            
            if os.path.exists(self.chromedriver_path):

                chrome_options = webdriver.ChromeOptions()
        
                chrome_options.add_argument('--headless')

                driver = webdriver.Chrome(executable_path = self.chromedriver_path, options = chrome_options)
                driver_version = str(driver.capabilities['chrome']['chromedriverVersion'].split(" ")[0])
                driver.close()
                driver.quit()

                logging.info(f'Current version of chromedriver: {driver_version}')

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

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)
        
        return result_run, message_run, driver_version

    def __compare_current_version_and_latest_version(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of chromedriver to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Empty string if function passed correctly, non-empty string if error.
            is_driver_up_to_date (bool) : If true current version of chromedriver is up to date. Defaults to False.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        is_driver_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''
        
        try:

            result, message, current_version = self.__get_current_version_chrome_selenium()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

            result, message, latest_version = self.__get_latest_version_chrome_driver()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_driver_up_to_date = True
                message = f'Your existing chromedriver is up to date. current_version: {current_version} latest_version: {latest_version}' 
                logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_driver_up_to_date, current_version, latest_version

    def __chmod_driver(self) -> Tuple[bool, str]:
        """Tries to give chromedriver needed permissions

        Returns:
            Tuple of bool and str

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Empty string if function passed correctly, non-empty string if error.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        
        try:

            if os.path.exists(self.chromedriver_path):

                logging.info('Trying to give chromedriver needed permissions')

                st = os.stat(self.chromedriver_path)
                os.chmod(self.chromedriver_path, st.st_mode | stat.S_IEXEC)

                logging.info('Needed rights for chromedriver was successfully issued')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
    
    def main(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates chromedriver binary or
        downloads specific version of chromedriver.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where chromedriver was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''
        
        try:

            if self.check_browser_is_up_to_date:

                if os.path.exists(self.chromedriver_path):

                    result, message = self.__check_if_chrome_browser_is_up_to_date()
                    if not result:
                        logging.error(message)
                        return result, message, driver_path

            if not self.version:

                #additional checking for equal versions
                result, message, is_equal, latest_version_driver, latest_version_browser = self.__compare_latest_version_main_chromedriver_and_latest_version_main_chrome_browser()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if is_equal:

                    result, message, driver_path = self.__check_if_chromedriver_is_up_to_date()
                    if not result:
                        logging.error(message)
                        return result, message, driver_path

                if not is_equal:

                    result, message, is_driver_up_to_date, latest_previous_version = self.__get_previous_latest_version_chromedriver()
                    if not result:
                        logging.error(message)
                        return result, message, driver_path

            else:

                result, message, driver_path = self.__download_chromedriver_for_specific_version(version=self.version)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __download_chromedriver_for_specific_version(self, version : str) -> Tuple[bool, str, str]:
        """Downloads specific version of chromedriver

        Args:
            version (str)    : Specific version of chromedriver.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where chromedriver was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''
        
        try:

            if self.upgrade:

                result, message = self.__delete_current_chromedriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result, message, driver_path = self.__get_specific_version_chromedriver_for_current_os(version)
            if not result:
                logging.error(message)
                return result, message, driver_path

            if self.chmod:

                result, message = self.__chmod_driver()
                if not result:
                    return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __get_specific_version_chromedriver_for_current_os(self, version : str) -> Tuple[bool, str, str]:
        """Downloads specific version of chromedriver to specific path

        Args:
            version (str)    : Specific version of chromedriver.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            file_name (str)         : Path where chromedriver was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        file_name : str = ''
        
        try:

            logging.info(f'Started download chromedriver specific_version: {version}')

            url = self.setting["ChromeDriver"]["LinkLastReleaseFile"].format(version)
            request = requests.get(url, headers=self.headers)
            status_code = request.status_code

            if status_code != 200:
                message = f'The wrong version was specified. url: {url} status_code: {status_code} version: {version}'
                logging.error(message)
                return result_run, message, file_name

            out_path = self.path + url.split('/')[4]

            if os.path.exists(out_path):
                os.remove(out_path)

            logging.info(f'Started download chromedriver by url: {url}')

            file_name = wget.download(url=url, out=out_path)

            logging.info(f'Chromedriver was downloaded to path: {file_name}')

            time.sleep(2)

            if not self.filename:

                archive_path = file_name
                out_path = self.path
                result, message = self.extractor.extract_all_zip_archive(archive_path=archive_path, out_path=out_path)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            else:

                archive_path = file_name
                out_path = self.path
                filename = self.setting['ChromeDriver']['LastReleasePlatform']
                filename_replace = self.filename
                result, message = self.extractor.extract_all_zip_archive_with_specific_name(archive_path=archive_path, 
                out_path=out_path, filename=filename, filename_replace=filename_replace)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            time.sleep(3)

            if os.path.exists(file_name):
                os.remove(file_name)

            
            file_name = self.chromedriver_path

            logging.info(f'Chromedriver was successfully unpacked by path: {file_name}')

            result_run = True

        except:

            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, file_name

    def __check_if_chrome_browser_is_up_to_date(self) -> Tuple[bool, str]:
        """Сhecks for the latest version of chrome browser

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
            
            chromebrowser_updater_path = str(self.setting["ChromeBrowser"]["ChromeBrowserUpdaterPath"])
            if not chromebrowser_updater_path:
                message = f'Parameter "check_browser_is_up_to_date" has not been optimized for your OS yet. Please wait for the new releases.'
                logging.info(message)
                return True, message

            if not os.path.exists(chromebrowser_updater_path):
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

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __get_current_version_chrome_browser_selenium(self) -> Tuple[bool, str, str]:
        """Gets current chrome browser version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
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
            
            if os.path.exists(self.chromedriver_path):

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

        except:
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
            request = requests.get(url=url, headers=self.headers)
            request_text = request.text
            status_code = request.status_code

            if status_code != 200:
                message = f'status_code not equal 200 status_code: {status_code} request_text: {request.text}'
                return result_run, message, latest_version

            soup = BeautifulSoup(request_text, 'html.parser')
            elements_news = soup.findAll('div', attrs={'class' : 'post-body'})
            stable_channel_text = 'The Stable channel has been updated to '

            for news in elements_news:
                if stable_channel_text in news.text:
                    latest_stable_version_element = news.text.replace('\n', '').replace('\xa0', '')
                    break

            if not latest_stable_version_element:
                message = f'Could not determine latest version of Chrome Browser. Maybe the text {stable_channel_text} is changed'
                logging.error(message)
                return result_run, message, latest_version

            latest_version = latest_stable_version_element.split(stable_channel_text)[1].split(' for Windows')[0] #maybe add more safely execution of version?

            if not no_messages:

                logging.info(f'Latest version of chrome browser: {latest_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __get_latest_chrome_browser_for_current_os(self) -> Tuple[bool, str]:
        """Trying to update chrome browser to its latest version

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

            message = f'Trying to update chrome browser to the latest version.'
            logging.info(message)

            os.system(self.setting["ChromeBrowser"]["ChromeBrowserUpdater"])
            time.sleep(15) #wait for the updating
            
            message = f'Chrome browser was successfully updated to the latest version.'
            logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __compare_current_version_and_latest_version_chrome_browser(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of chrome browser to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Empty string if function passed correctly, non-empty string if error.
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

            result, message, latest_version = self.__get_latest_version_chrome_browser()
            if not result:
                logging.error(message)
                return result, message, is_browser_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_browser_up_to_date = True
                message = f"Your existing chrome browser is up to date. current_version: {current_version} latest_version: {latest_version}"
                logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_browser_up_to_date, current_version, latest_version

    def __get_previous_latest_version_chromedriver(self):
        """Gets previous latest version of chromedriver

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Empty string if function passed correctly, non-empty string if error.
            is_driver_up_to_date (bool) : If true current version of chromedriver is successfully updated. Defaults to False.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        is_driver_up_to_date : bool = False
        latest_previous_version : str = ''
        
        try:

            result, message, is_equal, latest_version_driver, latest_version_browser = self.__compare_latest_version_main_chromedriver_and_latest_version_main_chrome_browser()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, latest_previous_version
            
            message = (f' Problem with chromedriver latest_version_driver : {latest_version_driver} latest_version_browser : {latest_version_browser}\n'
                        f' It often happen when new version of chromedriver released, but new version of chrome browser is not\n'
                        f' Trying to download the latest previous version of chromedriver')
            logging.error(message)

            if self.upgrade:

                result, message = self.__delete_current_chromedriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, is_driver_up_to_date, latest_previous_version

            result, message, latest_previous_version = self.__get_latest_previous_version_chromedriver_via_requests()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, latest_previous_version

            result, message, driver_path = self.__get_specific_version_chromedriver_for_current_os(latest_previous_version)
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, latest_previous_version

            if self.chmod:

                result, message = self.__chmod_driver()
                if not result:
                    return result, message, is_driver_up_to_date, latest_previous_version

            result, message, current_version = self.__get_current_version_chrome_selenium()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, latest_previous_version

            if current_version == latest_previous_version:
                is_driver_up_to_date = True
                message = f'Successfully downgraded to the latest previous version of chromedriver: {latest_previous_version}'
                logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_driver_up_to_date, latest_previous_version

    def __get_latest_previous_version_chromedriver_via_requests(self) -> Tuple[bool, str, str]:
        """Gets latest chromedriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Empty string if function passed correctly, non-empty string if error.
            latest_version_previous (str)   : Latest previous version of chromedriver.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_version_previous : str = ''

        try:
            
            url = self.setting["ChromeDriver"]["LinkLastRelease"]
            request = requests.get(url=url, headers=self.headers)
            status_code = request.status_code

            if status_code != 200:
                message = f'status_code not equal 200 status_code : {status_code} request_text: {request.text}'
                return result_run, message, latest_version_previous

            latest_version = str(request.text)

            logging.info(f'Latest version of chromedriver: {latest_version}')

            latest_version_main = latest_version.split(".")[0]

            logging.info(f'Latest main version of chromedriver: {latest_version_main}')

            latest_version_main_previous = int(latest_version_main) - 1

            url = self.setting["ChromeDriver"]["LinkLatestReleaseSpecificVersion"].format(latest_version_main_previous)
            request = requests.get(url=url, headers=self.headers)
            status_code = request.status_code

            if status_code != 200:
                message = f'status_code not equal 200 status_code : {status_code} request_text: {request.text}'
                return result_run, message, latest_version

            latest_version_previous = str(request.text)

            logging.info(f'Latest previous version of chromedriver: {latest_version_previous}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version_previous

    def __compare_latest_version_main_chromedriver_and_latest_version_main_chrome_browser(self) -> Tuple[bool, str, bool, str, str]:
        """Compares latest main version of chromedriver and latest main version of chrome browser

        Returns:
            Tuple of bool, str and bool

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Empty string if function passed correctly, non-empty string if error.
            is_equal (bool)                 : If true latest versions are both equal. Defaults to False.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        is_equal : bool = False
        latest_version_chromedriver_main : str = ''
        latest_version_browser_main : str = ''
        
        try:

            result, message, latest_version_chromedriver = self.__get_latest_version_chrome_driver(no_messages=True)
            if not result:
                logging.error(message)
                return result, message, is_equal, latest_version_chromedriver_main, latest_version_browser_main

            result, message, latest_version_browser = self.__get_latest_version_chrome_browser(no_messages=True)
            if not result:
                logging.error(message)
                return result, message, is_equal, latest_version_chromedriver_main, latest_version_browser_main

            latest_version_chromedriver_main = latest_version_chromedriver.split('.')[0]
            latest_version_browser_main = latest_version_browser.split('.')[0]

            if latest_version_chromedriver_main == latest_version_browser_main:
                is_equal = True

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_equal, latest_version_chromedriver_main, latest_version_browser_main