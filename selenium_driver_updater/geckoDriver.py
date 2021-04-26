import json
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

from selenium.webdriver.firefox.options import Options as FirefoxOptions

from typing import Tuple

import requests

import tarfile

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from _setting import setting

import platform

import shutil
from shutil import copyfile

import stat

import zipfile

class GeckoDriver():

    _tmp_folder_path = 'tmp'
    
    def __init__(self, path : str, upgrade : bool, chmod : bool, check_driver_is_up_to_date : bool, 
                info_messages : bool, filename : str, version : str):
        """Class for working with Selenium geckodriver binary

        Args:
            path (str)                          : Specified path which will used for downloading or updating Selenium geckodriver binary. Must be folder path.
            upgrade (bool)                      : If true, it will overwrite existing driver in the folder. Defaults to False.
            chmod (bool)                        : If true, it will make geckodriver binary executable. Defaults to True.
            check_driver_is_up_to_date (bool)   : If true, it will check driver version before and after upgrade. Defaults to False.
            info_messages (bool)                : If false, it will disable all info messages. Defaults to True.
            filename (str)                      : Specific name for geckodriver. If given, it will replace name for geckodriver.
            version (str)                       : Specific version for geckodriver. If given, it will downloads given version.
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

        self.geckodriver_path : str =  path + setting['GeckoDriver']['LastReleasePlatform'] if not filename else self.path + self.filename

        self.version = version

    def __get_current_version_geckodriver_selenium(self) -> Tuple[bool, str, str]:
        """Gets current geckodriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current driver version.

        Raises:
            SessionNotCreatedException: Occurs when current geckodriver could not start.
            
            WebDriverException: Occurs when current geckodriver could not start or critical error occured.

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''
        try:
            
            if os.path.exists(self.geckodriver_path):

                options = FirefoxOptions()
                options.add_argument("--headless")

                driver = webdriver.Firefox(executable_path = self.geckodriver_path, options=options)
                driver_version = str(driver.capabilities['moz:geckodriverVersion'])
                driver.close()
                driver.quit()

                logging.info(f'Current version of geckodriver: {driver_version}')


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

    def __get_latest_version_geckodriver(self) -> Tuple[bool, str, str]:
        """Gets latest geckodriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            latest_version (str)    : Latest version of geckodriver
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_version : str = ''

        try:
            
            url = self.setting['GeckoDriver']['LinkLastRelease']
            request = requests.get(url=url, headers=self.headers)
            request_text = request.text
            json_data = json.loads(str(request_text))

            latest_version = json_data.get('name')

            logging.info(f'Latest version of geckodriver: {latest_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __delete_current_geckodriver_for_current_os(self) -> Tuple[bool, str]:
        """Deletes geckodriver from folder


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

            if os.path.exists(self.geckodriver_path):
                logging.info(f'Deleted existing geckodriver geckodriver_path: {self.geckodriver_path}')
                os.remove(self.geckodriver_path)
            

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run

    def __get_latest_geckodriver_for_current_os(self) -> Tuple[bool, str, str]:
        """Download latest geckodriver to folder

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
        geckodriver_version : str = ''

        try:
            
            url = self.setting['GeckoDriver']['LinkLastRelease']
            request = requests.get(url=url, headers=self.headers)
            request_text = request.text
            json_data = json.loads(str(request_text))

            geckodriver_version = json_data.get('name')

            for asset in json_data.get('assets'):
                if self.setting['GeckoDriver']['LinkLastReleasePlatform'] in asset.get('name'):
                    filename_git = asset.get('name')
                    url = asset.get('browser_download_url')
                    break

            if not filename_git:
                message = (f"Geckodriver binary was not found, maybe unknown OS "
                          f"LinkLastReleasePlatform: {self.setting['GeckoDriver']['LinkLastReleasePlatform']}" )
                logging.error(message)
                return False, message, file_name
            
            logging.info(f'Started download geckodriver geckodriver_version: {geckodriver_version}')
            out_path = self.path + filename_git

            if os.path.exists(out_path):
                os.remove(out_path)

            logging.info(f'Started download geckodriver by url: {url}')

            file_name = wget.download(url=url, out=out_path)

            logging.info(f'Geckodriver was downloaded to path: {file_name}')

            time.sleep(2)

            if not self.filename:

                if filename_git.endswith('.tar.gz'):

                    with tarfile.open(file_name, "r:gz") as tar:
                        tar.extractall(self.path)

                elif filename_git.endswith('.zip'):

                    with zipfile.ZipFile(file_name, 'r') as zip_ref:
                        zip_ref.extractall(self.path)

                else:
                    message = f'Unknown archive format was specified filename: {filename_git}'
                    logging.error(message)
                    return result_run, message, file_name

            else:

                result, message = self.__rename_driver(file_name=file_name,filename_git=filename_git)
                if not result:
                    return result, message, file_name

            time.sleep(3)

            if os.path.exists(file_name):
                os.remove(file_name)

            file_name = self.geckodriver_path

            logging.info(f'Geckodriver was successfully unpacked by path: {file_name}')

            result_run = True

            logging.info(f'Geckodriver was successfully updated to the last version: {geckodriver_version}')

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, file_name
    
    def __check_if_geckodriver_is_up_to_date(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates geckodriver binary

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where geckodriver was downloaded or updated.
            
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
                    return True, message, self.geckodriver_path

            if self.upgrade:

                result, message = self.__delete_current_geckodriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result, message, driver_path = self.__get_latest_geckodriver_for_current_os()
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
                    message = f'Problem with updating geckodriver current_version : {current_version} latest_version : {latest_version}'
                    logging.error(message)
                    return result_run, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __compare_current_version_and_latest_version(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of geckodriver to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Empty string if function passed correctly, non-empty string if error.
            is_driver_up_to_date (bool) : If true current version of geckodriver is up to date. Defaults to False.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        is_driver_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''
        
        try:

            result, message, current_version = self.__get_current_version_geckodriver_selenium()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

            result, message, latest_version = self.__get_latest_version_geckodriver()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_driver_up_to_date = True
                message = f'Your existing geckodriver is up to date. current_version: {current_version} latest_version: {latest_version}' 
                logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, is_driver_up_to_date, current_version, latest_version

    def __rename_driver(self, file_name : str, filename_git : str) -> Tuple[bool, str]:
        """Renames geckodriver if it was given

        Args:
            file_name (str)     : Path to the geckodriver
            filename_git (str)  : Name of geckodriver archive

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

            driver_folder_path = self.path + GeckoDriver._tmp_folder_path
            logging.info(f'Created new directory for replacing name for geckodriver path: {driver_folder_path}')

            if os.path.exists(driver_folder_path):
                shutil.rmtree(driver_folder_path)

            if filename_git.endswith('.tar.gz'):

                with tarfile.open(file_name, "r:gz") as tar:
                    tar.extractall(driver_folder_path)

            elif filename_git.endswith('.zip'):

                with zipfile.ZipFile(file_name, 'r') as zip_ref:
                    zip_ref.extractall(driver_folder_path)

            else:
                message = f'Unknown archive format was specified filename: {filename_git}'
                logging.error(message)
                return result_run, message

            old_geckodriver_path = driver_folder_path + os.path.sep + setting['GeckoDriver']['LastReleasePlatform']
            new_geckodriver_path = driver_folder_path + os.path.sep + self.filename

            os.rename(old_geckodriver_path, new_geckodriver_path)

            renamed_driver_path = self.path + self.filename
            if os.path.exists(renamed_driver_path):
                os.remove(renamed_driver_path)

            copyfile(new_geckodriver_path, renamed_driver_path)

            if os.path.exists(driver_folder_path):
                shutil.rmtree(driver_folder_path)

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run

    def __chmod_driver(self) -> Tuple[bool, str]:
        """Tries to give geckodriver needed permissions

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

            if os.path.exists(self.geckodriver_path):

                logging.info('Trying to give geckodriver needed permissions')

                st = os.stat(self.geckodriver_path)
                os.chmod(self.geckodriver_path, st.st_mode | stat.S_IEXEC)

                logging.info('Needed rights for geckodriver were successfully issued')

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run

    def main(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates geckodriver binary or
        downloads specific version of geckodriver.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where geckodriver was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''
        
        try:

            if not self.version:

                result, message, driver_path = self.__check_if_geckodriver_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            else:

                result, message, driver_path = self.__download_geckodriver_for_specific_version(version=self.version)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __download_geckodriver_for_specific_version(self, version : str) -> Tuple[bool, str, str]:
        """Downloads specific version of geckodriver

        Args:
            version (str)    : Specific version of geckodriver.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where geckodriver was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''
        
        try:

            if self.upgrade:

                result, message = self.__delete_current_geckodriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result, message, driver_path = self.__get_specific_version_geckodriver_for_current_os(version=version)
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

    def __get_specific_version_geckodriver_for_current_os(self, version) -> Tuple[bool, str, str]:
        """Downloads specific version of geckodriver to specific path

        Args:
            version (str)    : Specific version of geckodriver.

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

        try:

            url = self.setting["GeckoDriver"]["LinkAllReleases"]
            request = requests.get(url=url, headers=self.headers)
            request_text = request.text
            json_data = json.loads(str(request_text))

            for release in json_data:
                if version == release.get('name') or version in release.get('tag_name'):
                    for asset in release.get('assets'):
                        if self.setting['GeckoDriver']['LinkLastReleasePlatform'] in asset.get('name'):
                            filename_git = asset.get('name')
                            url = asset.get('browser_download_url')
                            break

            if not filename_git:
                message = (f"Geckodriver binary was not found, maybe unknown OS or incorrect version "
                           f"LinkLastReleasePlatform: {self.setting['GeckoDriver']['LinkLastReleasePlatform']} "
                           f"specific_version: {version}" )
                logging.error(message)
                return False, message, file_name
            
            logging.info(f'Started download geckodriver specific_version: {version}')
            out_path = self.path + filename_git

            if os.path.exists(out_path):
                os.remove(out_path)

            logging.info(f'Started download geckodriver by url: {url}')

            file_name = wget.download(url=url, out=out_path)

            logging.info(f'Geckodriver was downloaded to path: {file_name}')

            time.sleep(2)

            if not self.filename:

                if filename_git.endswith('.tar.gz'):

                    with tarfile.open(file_name, "r:gz") as tar:
                        tar.extractall(self.path)

                elif filename_git.endswith('.zip'):

                    with zipfile.ZipFile(file_name, 'r') as zip_ref:
                        zip_ref.extractall(self.path)

                else:
                    message = f'Unknown archive format was specified filename: {filename_git}'
                    logging.error(message)
                    return result_run, message, file_name

            else:

                result, message = self.__rename_driver(file_name=file_name,filename_git=filename_git)
                if not result:
                    return result, message, file_name

            time.sleep(3)

            if os.path.exists(file_name):
                os.remove(file_name)

            file_name = self.geckodriver_path

            logging.info(f'Geckodriver was successfully unpacked by path: {file_name}')

            result_run = True
        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, file_name