import requests
import wget
import os
import traceback
import logging
import zipfile
import time
import stat
import os

import platform

from typing import Tuple

from .setting import setting

from selenium import webdriver

from selenium.common.exceptions import SessionNotCreatedException

from shutil import copyfile

import shutil

class ChromeDriver():

    _tmp_folder_path = 'tmp'
    
    def __init__(self, path : str, upgrade : bool, chmod : bool, check_driver_is_up_to_date : bool, 
                info_messages : bool, filename : str):
        """Class for working with Selenium chromedriver binary

        Args:
            path (str)                          : Specified path which will used for downloading or updating Selenium chromedriver binary. Must be folder path.
            upgrade (bool)                      : If true, it will overwrite existing driver in the folder. Defaults to False.
            chmod (bool)                        : If true, it will make chromedriver binary executable. Defaults to True.
            check_driver_is_up_to_date (bool)   : If true, it will check driver version before and after upgrade. Defaults to False.
            info_messages (bool)                : If false, it will disable all info messages. Defaults to True.
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

        self.filename = f"{filename}.exe" if platform.system() == 'Windows' else\
                        filename

        self.chromedriver_path : str =  path + setting['ChromeDriver']['LastReleasePlatform'] if not self.filename else self.path + self.filename


    def __get_latest_version_chrome_driver(self) -> Tuple[bool, str, str]:
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
            
            request = requests.get(self.setting["ChromeDriver"]["LinkLastRelease"], headers=self.headers)
            latest_version = str(request.text)

            logging.info(f'Latest version of chromedriver: {latest_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
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
                os.remove(self.chromedriver_path)
            

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
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
        renamed_driver_path : str = ''
        
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

                with zipfile.ZipFile(file_name, 'r') as zip_ref:
                    zip_ref.extractall(self.path)

            else:

                driver_folder_path = self.path + ChromeDriver._tmp_folder_path
                logging.info(f'Created new directory for replacing name for chromedriver path: {driver_folder_path}')

                if os.path.exists(driver_folder_path):
                    shutil.rmtree(driver_folder_path)

                with zipfile.ZipFile(file_name, 'r') as zip_ref:
                    zip_ref.extractall(driver_folder_path)

                old_chromedriver_path = driver_folder_path + os.path.sep + setting['ChromeDriver']['LastReleasePlatform']
                new_chromedriver_path = driver_folder_path + os.path.sep + self.filename

                os.rename(old_chromedriver_path, new_chromedriver_path)

                renamed_driver_path = self.path + self.filename
                if os.path.exists(renamed_driver_path):
                    os.remove(renamed_driver_path)

                copyfile(new_chromedriver_path, renamed_driver_path)

                if os.path.exists(driver_folder_path):
                    shutil.rmtree(driver_folder_path)

            time.sleep(3)

            if os.path.exists(file_name):
                os.remove(file_name)

            
            file_name = self.chromedriver_path

            logging.info(f'Chromedriver was successfully unpacked by path: {file_name}')

            if self.chmod:

                st = os.stat(file_name)
                os.chmod(file_name, st.st_mode | stat.S_IEXEC)

            result_run = True

        except:

            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, file_name

    def check_if_chromedriver_is_up_to_date(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates chromedriver binary

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

                result, message, current_version = self.__get_current_version_chrome_selenium()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                result, message, latest_version = self.__get_latest_version_chrome_driver()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if current_version == latest_version:
                    message = f'Your existing chromedriver is already up to date. current_version: {current_version} latest_version: {latest_version}' 
                    logging.info(message)
                    return True, message_run, self.chromedriver_path

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

            if self.check_driver_is_up_to_date:

                result, message, current_version_updated = self.__get_current_version_chrome_selenium()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                result, message, latest_version = self.__get_latest_version_chrome_driver()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if current_version_updated != latest_version:
                    message = f'Problem with updating chromedriver current_version_updated : {current_version_updated} latest_version : {latest_version}'
                    logging.error(message)
                    return result_run, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __get_current_version_chrome_selenium(self) -> Tuple[bool, str, str]:
        """Gets current chromedriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current chromedriver version

        Raises:
            SessionNotCreatedException: Occurs when current chromedriver could not start

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
            message_run = f'SessionNotCreatedException error: {str(traceback.format_exc())}'
            logging.error(message_run)
            return True, message_run, driver_version

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)
        
        return result_run, message_run, driver_version
    