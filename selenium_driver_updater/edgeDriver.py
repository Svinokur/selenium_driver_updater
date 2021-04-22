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

from typing import Tuple

import requests

from .setting import setting

import platform

from bs4 import BeautifulSoup

import stat

import zipfile

class EdgeDriver():
    
    def __init__(self, path : str, upgrade : bool, chmod : bool, check_driver_is_up_to_date : bool, info_messages : bool):
        """Class for working with Selenium edgedriver binary

        Args:
            path (str)                          : Specified path which will used for downloading or updating Selenium edgedriver binary. Must be folder path.
            upgrade (bool)                      : If true, it will overwrite existing driver in the folder. Defaults to False.
            chmod (bool)                        : If true, it will make edgedriver binary executable. Defaults to True.
            check_driver_is_up_to_date (bool)   : If true, it will check driver version before and after upgrade. Defaults to False.
            info_messages (bool)                : If false, it will disable all info messages. Defaults to True.
        """
        self.setting = setting

        self.path : str = path

        self.edgedriver_path : str =  path + "msedgedriver.exe" if platform.system() == 'Windows' else\
                                        path + "msedgedriver"
                    
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

    def __get_current_version_edgedriver_selenium(self) -> Tuple[bool, str, str]:
        """Gets current edgedriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current driver version

        Raises:
            SessionNotCreatedException: Occurs when current edgedriver could not start

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''
        try:

            if os.path.exists(self.edgedriver_path):
                
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

            with zipfile.ZipFile(file_name, 'r') as zip_ref:
                zip_ref.extractall(self.path)

            time.sleep(3)

            if os.path.exists(file_name):
                os.remove(file_name)

            if os.path.exists(driver_notes_path):
                shutil.rmtree(driver_notes_path)

            file_name = self.edgedriver_path

            if self.chmod:

                st = os.stat(self.edgedriver_path)
                os.chmod(self.edgedriver_path, st.st_mode | stat.S_IEXEC)

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, file_name
    
    def check_if_edgedriver_is_up_to_date(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates edgedriver binary

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            file_name (str)         : Path where edgedriver was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        file_name : str = ''
        
        try:

            if self.check_driver_is_up_to_date:

                result, message, current_version = self.__get_current_version_edgedriver_selenium()
                if not result:
                    logging.error(message)
                    return result, message, file_name

                result, message, latest_version = self.__get_latest_version_edgedriver()
                if not result:
                    logging.error(message)
                    return result, message, file_name

                if current_version == latest_version:
                    message = f'Your existing edgedriver is already up to date. current_version: {current_version} latest_version: {latest_version}' 
                    logging.info(message)
                    return True, message_run, self.edgedriver_path

            else:

                result, message, latest_version = self.__get_latest_version_edgedriver()
                if not result:
                    logging.error(message)
                    return result, message, file_name

            if self.upgrade:

                result, message = self.__delete_current_edgedriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, file_name

            result, message, file_name = self.__get_latest_edgedriver_for_current_os(latest_version)
            if not result:
                logging.error(message)
                return result, message, file_name

            if self.check_driver_is_up_to_date:

                result, message, current_version_updated = self.__get_current_version_edgedriver_selenium()
                if not result:
                    logging.error(message)
                    return result, message, file_name

                result, message, latest_version = self.__get_latest_version_edgedriver()
                if not result:
                    logging.error(message)
                    return result, message, file_name

                if current_version_updated != latest_version:
                    message = f'Problem with updating edgedriver current_version_updated : {current_version_updated} latest_version : {latest_version}'
                    logging.error(message)
                    return result_run, message, file_name

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, file_name