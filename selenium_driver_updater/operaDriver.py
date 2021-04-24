import json
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

import zipfile

from .setting import setting

import platform

import stat

from shutil import copyfile

class OperaDriver():
    
    def __init__(self, path : str, upgrade : bool, chmod : bool, check_driver_is_up_to_date : bool, 
                info_messages : bool, filename : str):
        """Class for working with Selenium operadriver binary

        Args:
            path (str)                          : Specified path which will used for downloading or updating Selenium operadriver binary. Must be folder path.
            upgrade (bool)                      : If true, it will overwrite existing driver in the folder. Defaults to False.
            chmod (bool)                        : If true, it will make operadriver binary executable. Defaults to True.
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

        self.filename = f"{filename}.exe" if platform.system() == 'Windows' and filename else\
                        filename

        self.operadriver_path : str =  path + setting['OperaDriver']['LastReleasePlatform'] if not filename else self.path + self.filename

    def __get_current_version_operadriver_selenium(self) -> Tuple[bool, str, str]:
        """Gets current operadriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current driver version

        Raises:
            SessionNotCreatedException: Occurs when current operadriver could not start.

            WebDriverException: Occurs when current operadriver could not start or critical error occured

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''

        try:

            if os.path.exists(self.operadriver_path):

                driver = webdriver.Opera(executable_path = self.operadriver_path)
                driver_version = str(driver.capabilities['opera']['operadriverVersion'].split(' ')[0])
                driver.close()
                driver.quit()

                logging.info(f'Current version of operadriver: {driver_version}')


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

    def __get_latest_version_operadriver(self) -> Tuple[bool, str, str]:
        """Gets latest operadriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            latest_version (str)    : Latest version of operadriver
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_version : str = ''

        try:
            
            request = requests.get(self.setting['OperaDriver']['LinkLastRelease'], headers=self.headers)
            request_text = request.text
            json_data = json.loads(str(request_text))

            
            latest_version = json_data.get('name')

            logging.info(f'Latest version of operadriver: {latest_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __delete_current_geckodriver_for_current_os(self) -> Tuple[bool, str]:
        """Deletes operadriver from specific folder


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

            if os.path.exists(self.operadriver_path):
                logging.info(f'Deleted existing operadriver operadriver_path: {self.operadriver_path}')
                os.remove(self.operadriver_path)
            

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run

    def __get_latest_operadriver_for_current_os(self) -> Tuple[bool, str, str]:
        """Download latest operadriver to folder

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
        filename_git : str = ''
        url : str = ''
        operadriver_version : str = ''

        try:
            request = requests.get(self.setting['OperaDriver']['LinkLastRelease'], headers=self.headers)
            request_text = request.text
            json_data = json.loads(str(request_text))

            operadriver_version = json_data.get('name')

            for asset in json_data.get('assets'):
                if self.setting['OperaDriver']['LinkLastReleasePlatform'] == asset.get('name'):
                    filename_git = asset.get('name')
                    url = asset.get('browser_download_url')
                    break

            if not filename_git:
                message = (f"Operadriver binary was not found, maybe unknown OS"
                          f"LinkLastReleasePlatform: {self.setting['OperaDriver']['LinkLastReleasePlatform']}")
                logging.error(message)
                return False, message, file_name
            
            logging.info(f'Started download operadriver operadriver_version: {operadriver_version}')
            out_path = self.path + filename_git

            if os.path.exists(out_path):
                os.remove(out_path)

            logging.info(f'Started download operadriver by url: {url}')

            file_name = wget.download(url=url, out=out_path)

            logging.info(f'Operadriver was downloaded to path: {file_name}')

            time.sleep(2)

            with zipfile.ZipFile(file_name, 'r') as zip_ref:
                zip_ref.extractall(self.path)

            time.sleep(3)

            archive_folder_path = self.path + self.setting['OperaDriver']['LinkLastReleasePlatform'][:-4]
            archive_operadriver_path = archive_folder_path + os.path.sep + self.setting['OperaDriver']['LastReleasePlatform']

            if not self.filename:

                copyfile(archive_operadriver_path, self.path + self.setting['OperaDriver']['LastReleasePlatform'])

            else:

                result, message = self.__rename_driver(archive_folder_path=archive_folder_path,
                                                        archive_operadriver_path=archive_operadriver_path)
                if not result:
                    return result, message, file_name

            if os.path.exists(file_name):
                os.remove(file_name)

            if os.path.exists(archive_folder_path):
                shutil.rmtree(archive_folder_path)
            
            file_name = self.operadriver_path

            result_run = True

            logging.info(f'Operadriver was successfully updated to the last version: {operadriver_version}')

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, file_name
    
    def check_if_operadriver_is_up_to_date(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates operadriver binary

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where operadriver was downloaded or updated.
            
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
                    return True, message, self.operadriver_path

            if self.upgrade:

                result, message = self.__delete_current_geckodriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result, message, driver_path = self.__get_latest_operadriver_for_current_os()
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
                    message = f'Problem with updating operadriver current_version: {current_version} latest_version: {latest_version}'
                    logging.error(message)
                    return result_run, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __compare_current_version_and_latest_version(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of operadriver to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Empty string if function passed correctly, non-empty string if error.
            is_driver_up_to_date (bool) : If true current version of operadriver is up to date. Defaults to False.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        is_driver_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''
        
        try:

            result, message, current_version = self.__get_current_version_operadriver_selenium()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

            result, message, latest_version = self.__get_latest_version_operadriver()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_driver_up_to_date = True
                message = f'Your existing operadriver is up to date. current_version: {current_version} latest_version: {latest_version}' 
                logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, is_driver_up_to_date, current_version, latest_version

    def __rename_driver(self, archive_folder_path : str, archive_operadriver_path : str) -> Tuple[bool, str]:
        """Renames operadriver if it was given

        Args:
            archive_folder_path (str)       : Path to the main folder
            archive_operadriver_path (str)  : Path to the operadriver archive

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

            new_path = archive_folder_path + os.path.sep + self.filename

            if os.path.exists(new_path):
                os.remove(new_path)

            os.rename(archive_operadriver_path, new_path)
            
            renamed_driver_path = self.path + self.filename
            if os.path.exists(renamed_driver_path):
                os.remove(renamed_driver_path)

            copyfile(new_path, self.path + self.filename)

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run

    def __chmod_driver(self) -> Tuple[bool, str]:
        """Tries to give operadriver needed permissions

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

            if os.path.exists(self.operadriver_path):

                logging.info('Trying to give operadriver needed permissions')

                st = os.stat(self.operadriver_path)
                os.chmod(self.operadriver_path, st.st_mode | stat.S_IEXEC)

                logging.info('Needed rights for edgedriver was successfully issued')

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run