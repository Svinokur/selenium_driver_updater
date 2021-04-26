import shutil
from selenium import webdriver
import requests
import wget
import os
import traceback
import logging
import time
import os
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

from typing import Tuple

import requests

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from _setting import setting

import platform

from bs4 import BeautifulSoup

import stat

import zipfile

from shutil import copyfile

class EdgeDriver():

    _tmp_folder_path = 'tmp'
    
    def __init__(self, path : str, upgrade : bool, chmod : bool, check_driver_is_up_to_date : bool, 
                info_messages : bool, filename : str, version : str):
        """Class for working with Selenium edgedriver binary

        Args:
            path (str)                          : Specified path which will used for downloading or updating Selenium edgedriver binary. Must be folder path.
            upgrade (bool)                      : If true, it will overwrite existing driver in the folder. Defaults to False.
            chmod (bool)                        : If true, it will make edgedriver binary executable. Defaults to True.
            check_driver_is_up_to_date (bool)   : If true, it will check driver version before and after upgrade. Defaults to False.
            info_messages (bool)                : If false, it will disable all info messages. Defaults to True.
            filename (str)                      : Specific name for edgedriver. If given, it will replace name for edgedriver.
            version (str)                       : Specific version for edgedriver. If given, it will downloads given version.
        """
        self.setting = setting

        self.path : str = path
                    
        self.upgrade : bool = upgrade

        self.chmod : bool = chmod

        self.check_driver_is_up_to_date = check_driver_is_up_to_date

        self.info_messages = info_messages

        if self.info_messages:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.ERROR)

        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/35.0.1916.47 Safari/537.36'

        self.headers = {'User-Agent': user_agent}

        self.filename = f"{filename}.exe" if platform.system() == 'Windows' and filename else\
                        filename

        self.edgedriver_path : str =  path + setting['EdgeDriver']['LastReleasePlatform'] if not filename else self.path + self.filename

        self.version = version

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

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''

        try:

            if os.path.exists(self.edgedriver_path):

                #driver = Edge(executable_path=self.edgedriver_path, desired_capabilities=desired_cap)
                desired_cap = {}

                driver = webdriver.Edge(executable_path = self.edgedriver_path, capabilities=desired_cap)
                driver_version = str(driver.capabilities['msedge']['msedgedriverVersion'].split(' ')[0])
                driver.close()
                driver.quit()
        
                logging.info(f'Current version of edgedriver: {driver_version}')

            result_run = True

        except SessionNotCreatedException:
            message_run = f'SessionNotCreatedException error: {str(traceback.format_exc())}'
            logging.error(message_run)
            return True, message_run, driver_version

        except WebDriverException:
            message_run = f'WebDriverException error: {str(traceback.format_exc())}'
            logging.error(message_run)
            return True, message_run, driver_version

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
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
            
            request = requests.get(self.setting['EdgeDriver']['LinkLastRelease'], headers=self.headers)
            request_text = request.text
            soup = BeautifulSoup(request_text, 'lxml')

            elements = soup.findAll('ul', attrs={'class' : 'bare driver-downloads'})

            for element in elements:
                if 'stable ChannelCurrent' in element.text:
                    stable_channel_element = element
                    break

            if not stable_channel_element:
                message = 'Could not determine latest version of Edge Driver.'
                logging.error(message)
                return result_run, message, latest_version
            
            latest_version_element = stable_channel_element.findAll('p', attrs={'class' : 'driver-download__meta'})[0].text
            latest_version = latest_version_element.split(':')[1][1:]

            logging.info(f'Latest version of edgedriver: {latest_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
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
                os.remove(self.edgedriver_path)
            

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run

    def __get_latest_edgedriver_for_current_os(self, latest_version : str) -> Tuple[bool, str, str]:
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
            
            logging.info(f'Started download edgedriver latest_version: {latest_version}')

            url = self.setting["EdgeDriver"]["LinkLastReleaseFile"].format(latest_version)
            out_path = self.path + url.split('/')[4]

            logging.info(f'Started download edgedriver by url: {url}')

            if os.path.exists(out_path):
                os.remove(out_path)

            file_name = wget.download(url=url, out=out_path)

            logging.info(f'Edgedriver was downloaded to path: {file_name}')

            time.sleep(2)

            if not self.filename:
                
                with zipfile.ZipFile(file_name, 'r') as zip_ref:
                    zip_ref.extractall(self.path)

            else:

                result, message = self.__rename_driver(file_name=file_name)
                if not result:
                    return result, message, file_name

            time.sleep(3)

            if os.path.exists(file_name):
                os.remove(file_name)

            if os.path.exists(driver_notes_path):
                shutil.rmtree(driver_notes_path)

            file_name = self.edgedriver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, file_name
    
    def __check_if_edgedriver_is_up_to_date(self) -> Tuple[bool, str, str]:
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

            if self.check_driver_is_up_to_date:

                result, message, is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if is_driver_up_to_date:
                    return True, message, self.edgedriver_path

            else:

                result, message, latest_version = self.__get_latest_version_edgedriver()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            if self.upgrade:

                result, message = self.__delete_current_edgedriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result, message, driver_path = self.__get_latest_edgedriver_for_current_os(latest_version)
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
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
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
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, is_driver_up_to_date, current_version, latest_version

    def __rename_driver(self, file_name : str) -> Tuple[bool, str]:
        """Renames edgedriver if it was given

        Args:
            file_name (str)     : Path to the edgedriver

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Empty string if function passed correctly, non-empty string if error.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        renamed_driver_path : str = ''
        
        try:

            driver_folder_path = self.path + EdgeDriver._tmp_folder_path
            logging.info(f'Created new directory for replacing name for edgedriver path: {driver_folder_path}')

            if os.path.exists(driver_folder_path):
                shutil.rmtree(driver_folder_path)

            with zipfile.ZipFile(file_name, 'r') as zip_ref:
                zip_ref.extractall(driver_folder_path)

            old_edgedriver_path = driver_folder_path + os.path.sep + setting['EdgeDriver']['LastReleasePlatform']
            new_edgedriver_path = driver_folder_path + os.path.sep + self.filename

            os.rename(old_edgedriver_path, new_edgedriver_path)

            renamed_driver_path = self.path + self.filename
            if os.path.exists(renamed_driver_path):
                os.remove(renamed_driver_path)

            copyfile(new_edgedriver_path, renamed_driver_path)

            if os.path.exists(driver_folder_path):
                shutil.rmtree(driver_folder_path)

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run

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
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
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

            if not self.version:

                result, message, driver_path = self.__check_if_edgedriver_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            else:

                result, message, driver_path = self.__download_edgedriver_for_specific_version(version=self.version)

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
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
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
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
            request = requests.get(url=url, headers=self.headers)
            status_code = request.status_code

            if status_code != 200:
                message = f'The wrong version was specified. url: {url} status_code: {status_code} version: {version}'
                logging.error(message)
                return result_run, message, file_name

            out_path = self.path + url.split('/')[4]

            logging.info(f'Started download edgedriver by url: {url}')

            if os.path.exists(out_path):
                os.remove(out_path)

            file_name = wget.download(url=url, out=out_path)

            logging.info(f'Edgedriver was downloaded to path: {file_name}')

            time.sleep(2)

            if not self.filename:
                
                with zipfile.ZipFile(file_name, 'r') as zip_ref:
                    zip_ref.extractall(self.path)

            else:

                result, message = self.__rename_driver(file_name=file_name)
                if not result:
                    return result, message, file_name

            time.sleep(3)

            if os.path.exists(file_name):
                os.remove(file_name)

            if os.path.exists(driver_notes_path):
                shutil.rmtree(driver_notes_path)

            file_name = self.edgedriver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, file_name