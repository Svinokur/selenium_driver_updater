import shutil
import subprocess
from selenium import webdriver
import wget
import os
import traceback
import logging
import time
import os
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

from typing import Tuple

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from _setting import setting

import platform

from bs4 import BeautifulSoup

import stat

from util.extractor import Extractor
from util.requests_getter import RequestsGetter

import pathlib

import re

class EdgeDriver():

    _tmp_folder_path = 'tmp'
    
    def __init__(self, path : str, **kwargs):
        """Class for working with Selenium edgedriver binary

        Args:
            path (str)                          : Specified path which will used for downloading or updating Selenium edgedriver binary. Must be folder path.
            upgrade (bool)                      : If true, it will overwrite existing driver in the folder. Defaults to False.
            chmod (bool)                        : If true, it will make edgedriver binary executable. Defaults to True.
            check_driver_is_up_to_date (bool)   : If true, it will check driver version before and after upgrade. Defaults to False.
            filename (str)                      : Specific name for edgedriver. If given, it will replace name for edgedriver.
            version (str)                       : Specific version for edgedriver. If given, it will downloads given version.
            check_browser_is_up_to_date (bool)  : If true, it will check edge browser version before edgedriver update/upgrade.
        """
        self.setting = setting

        self.path : str = path
                    
        self.upgrade : bool = bool(kwargs.get('upgrade'))

        self.chmod : bool = bool(kwargs.get('chmod'))

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))
        
        specific_filename = str(kwargs.get('filename'))
        self.filename = f"{specific_filename}.exe" if platform.system() == 'Windows' and specific_filename else\
                        specific_filename

        self.edgedriver_path : str =  self.path + self.setting['EdgeDriver']['LastReleasePlatform'] if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date'))

        self.info_messages = bool(kwargs.get('info_messages'))

        self.extractor = Extractor
        self.requests_getter = RequestsGetter

    def __get_current_version_edgedriver_selenium(self) -> Tuple[bool, str, str]:
        """Gets current edgedriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current driver version.

        Raises:
            SessionNotCreatedException: Occurs when current edgedriver could not start.

            WebDriverException: Occurs when current edgedriver could not start or critical error occured

            OSError: Occurs when chromedriver made for another CPU type

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''

        try:

            if os.path.exists(self.edgedriver_path):

                result, message, driver_version = self.__get_current_version_edgedriver_via_terminal()
                if not result:
                    logging.error(message)
                    message = 'Trying to get current version of edgedriver via webdriver'
                    logging.info(message)
                
                if not result or not driver_version:

                    #driver = Edge(executable_path=self.edgedriver_path, desired_capabilities=desired_cap)
                    desired_cap = {}

                    driver = webdriver.Edge(executable_path = self.edgedriver_path, capabilities=desired_cap)
                    
                    driver_version_selenium = str(driver.capabilities['msedge']['msedgedriverVersion'])

                    find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_selenium)
                    driver_version = find_string[0] if len(find_string) > 0 else driver_version_selenium.split(' ')[0]

                    driver.close()
                    driver.quit()
        
                logging.info(f'Current version of edgedriver: {driver_version}')

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

    def __get_latest_version_edgedriver(self) -> Tuple[bool, str, str]:
        """Gets latest edgedriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            latest_version (str)    : Latest version of edgedriver
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_version : str = ''
        stable_channel_element = None
        latest_version_element = None

        try:
            
            url = self.setting['EdgeDriver']['LinkLastRelease']
            result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
            if not result:
                logging.error(message)
                return result, message, latest_version

            soup = BeautifulSoup(json_data, 'html.parser')

            elements = soup.findAll('ul', attrs={'class' : 'bare driver-downloads'})
            stable_channel_text = 'stable ChannelCurrent'

            for element in elements:
                if stable_channel_text in element.text:
                    stable_channel_element = element
                    break

            if not stable_channel_element:
                message = f'Could not determine latest version of Edge Driver. Maybe the text "{stable_channel_text}" is changed'
                logging.error(message)
                return result_run, message, latest_version
            
            latest_version_element = stable_channel_element.findAll('p', attrs={'class' : 'driver-download__meta'})[0].text
            
            latest_version = re.findall(self.setting["Program"]["wedriverVersionPattern"], latest_version_element)[0]

            logging.info(f'Latest version of edgedriver: {latest_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __delete_current_edgedriver_for_current_os(self) -> Tuple[bool, str]:
        """Deletes edgedriver from folder


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

            if os.path.exists(self.edgedriver_path):
                logging.info(f'Deleted existing edgedriver edgedriver_path: {self.edgedriver_path}')
                file_to_rem = pathlib.Path(self.edgedriver_path)
                file_to_rem.unlink()
            

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __get_latest_edgedriver_for_current_os(self) -> Tuple[bool, str, str]:
        """Download latest edgedriver to folder

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            file_name (str)         : File name of unzipped file
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        file_name : str = ''
        driver_notes_path : str = self.path + 'Driver_Notes'

        try:

            result, message, latest_version = self.__get_latest_version_edgedriver()
            if not result:
                logging.error(message)
                return result, message, file_name
            
            logging.info(f'Started download edgedriver latest_version: {latest_version}')

            url = self.setting["EdgeDriver"]["LinkLastReleaseFile"].format(latest_version)
            out_path = self.path + url.split('/')[4]

            logging.info(f'Started download edgedriver by url: {url}')

            if os.path.exists(out_path):
                os.remove(out_path)

            if self.info_messages:
                file_name = wget.download(url=url, out=out_path)
            else:
                file_name = wget.download(url=url, out=out_path, bar=None)
            time.sleep(2)

            logging.info(f'Edgedriver was downloaded to path: {file_name}')

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
                filename = self.setting['EdgeDriver']['LastReleasePlatform']
                filename_replace = self.filename

                result, message = self.extractor.extract_all_zip_archive_with_specific_name(archive_path=archive_path, 
                out_path=out_path, filename=filename, filename_replace=filename_replace)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            if os.path.exists(file_name):
                os.remove(file_name)

            if os.path.exists(driver_notes_path):
                shutil.rmtree(driver_notes_path)

            file_name = self.edgedriver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, file_name
    
    def __check_if_edgedriver_is_up_to_date(self) -> Tuple[bool, str, str]:
        """Checks for the latest version, downloads or updates edgedriver binary

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where edgedriver was downloaded or updated.
            
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
                    return True, message, self.edgedriver_path

            if self.upgrade:

                result, message = self.__delete_current_edgedriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result, message, driver_path = self.__get_latest_edgedriver_for_current_os()
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
                    message = f'Problem with updating edgedriver current_version : {current_version} latest_version : {latest_version}'
                    logging.error(message)
                    return result_run, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __compare_current_version_and_latest_version(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of edgedriver to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Empty string if function passed correctly, non-empty string if error.
            is_driver_up_to_date (bool) : If true current version of edgedriver is up to date. Defaults to False.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        is_driver_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''
        
        try:

            result, message, current_version = self.__get_current_version_edgedriver_selenium()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

            if not current_version:
                return True, message_run, is_driver_up_to_date, current_version, latest_version

            result, message, latest_version = self.__get_latest_version_edgedriver()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_driver_up_to_date = True
                message = f'Your existing edgedriver is up to date. current_version: {current_version} latest_version: {latest_version}' 
                logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_driver_up_to_date, current_version, latest_version

    def __chmod_driver(self) -> Tuple[bool, str]:
        """Tries to give edgedriver needed permissions

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

            if os.path.exists(self.edgedriver_path):

                logging.info('Trying to give edgedriver needed permissions')

                st = os.stat(self.edgedriver_path)
                os.chmod(self.edgedriver_path, st.st_mode | stat.S_IEXEC)

                logging.info('Needed rights for edgedriver were successfully issued')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def main(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates edgedriver binary

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where edgedriver was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''
        
        try:

            if self.check_browser_is_up_to_date:

                result, message = self.__check_if_edge_browser_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            if not self.version:

                result, message, driver_path = self.__check_if_edgedriver_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            else:

                result, message, driver_path = self.__download_edgedriver_for_specific_version(version=self.version)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __download_edgedriver_for_specific_version(self, version : str) -> Tuple[bool, str, str]:
        """Downloads specific version of edgedriver

        Args:
            version (str)    : Specific version of edgedriver.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where edgedriver was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''
        
        try:

            if self.upgrade:

                result, message = self.__delete_current_edgedriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result, message, driver_path = self.__get_specific_version_edgedriver_for_current_os(version=version)
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

    def __get_specific_version_edgedriver_for_current_os(self, version : str) -> Tuple[bool, str, str]:
        """Download specific version of edgedriver to folder

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            file_name (str)         : File name of unzipped file
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        file_name : str = ''
        driver_notes_path : str = self.path + 'Driver_Notes'

        try:
            
            logging.info(f'Started download edgedriver specific_version: {version}')

            url = self.setting["EdgeDriver"]["LinkLastReleaseFile"].format(version)
            result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url, return_text=False)
            if not result:
                logging.error(message)
                return result, message, file_name

            out_path = self.path + url.split('/')[4]

            logging.info(f'Started download edgedriver by url: {url}')

            if os.path.exists(out_path):
                os.remove(out_path)

            if self.info_messages:
                file_name = wget.download(url=url, out=out_path)
            else:
                file_name = wget.download(url=url, out=out_path, bar=None)
            time.sleep(2)

            logging.info(f'Edgedriver was downloaded to path: {file_name}')

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
                filename = self.setting['EdgeDriver']['LastReleasePlatform']
                filename_replace = self.filename

                result, message = self.extractor.extract_all_zip_archive_with_specific_name(archive_path=archive_path, 
                out_path=out_path, filename=filename, filename_replace=filename_replace)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            if os.path.exists(file_name):
                os.remove(file_name)

            if os.path.exists(driver_notes_path):
                shutil.rmtree(driver_notes_path)

            file_name = self.edgedriver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, file_name

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
                message = f'Parameter "check_browser_is_up_to_date" has not been optimized for your OS yet. Please wait for the new releases.'
                logging.info(message)
                return True, message

            if not os.path.exists(edgebrowser_updater_path):
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

        except:
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
            
            if os.path.exists(self.edgedriver_path) and not result or not browser_version:

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

        except:
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

        except:
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

            message = f'Trying to update edge browser to the latest version.'
            logging.info(message)

            os.system(self.setting["EdgeBrowser"]["EdgeBrowserUpdater"])
            time.sleep(60) #wait for the updating
            
            message = f'Edge browser was successfully updated to the latest version.'
            logging.info(message)

            result_run = True

        except:
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

            result, message, latest_version = self.__get_latest_version_edge_browser()
            if not result:
                logging.error(message)
                return result, message, is_browser_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_browser_up_to_date = True
                message = f"Your existing edge browser is up to date. current_version: {current_version} latest_version: {latest_version}"
                logging.info(message)

            result_run = True

        except:
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

                if platform.system() == 'Windows':

                    process = subprocess.Popen(edgebrowser_path, stdout=subprocess.PIPE)
        
                    browser_version_terminal = process.communicate()[0].decode('UTF-8')
                    browser_version_terminal = browser_version_terminal[-50:].strip()

                elif platform.system() == 'Darwin':
                    process = subprocess.Popen([edgebrowser_path, '--version'], stdout=subprocess.PIPE)
        
                    browser_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], browser_version_terminal)
                browser_version = find_string[0] if len(find_string) > 0 else ''

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)
        
        return result_run, message_run, browser_version

    def __get_current_version_edgedriver_via_terminal(self) -> Tuple[bool, str, str]:
        """Gets current edgedriver version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current edgedriver version.

        Raises:

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''
        driver_version_terminal : str = ''
        
        try:

            logging.info('Trying to get current version of edgedriver via terminal')
        
            process = subprocess.Popen([self.edgedriver_path, '--version'], stdout=subprocess.PIPE)
    
            driver_version_terminal = process.communicate()[0].decode('UTF-8')

            find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_terminal)
            driver_version = find_string[0] if len(find_string) > 0 else ''

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)
        
        return result_run, message_run, driver_version