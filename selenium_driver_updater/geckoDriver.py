import json
from selenium import webdriver
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

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from _setting import setting

import platform

import stat

from util.extractor import Extractor

try:
    from util.github_viewer import GithubViewer
except:
    from selenium_driver_updater.selenium_driver_updater.util.github_viewer import GithubViewer

class GeckoDriver():

    _repo_name = 'mozilla/geckodriver'
    
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

        self.extractor = Extractor

        self.github_viewer = GithubViewer

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
            
            repo_name = GeckoDriver._repo_name
            result, message, json_data = self.github_viewer.get_latest_release_data_by_repo_name(repo_name=repo_name)
            if not result:
                return result, message, latest_version

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
        asset_name : str = ''
        url : str = ''
        geckodriver_version : str = ''

        try:
            
            repo_name = GeckoDriver._repo_name
            asset_name = self.setting['GeckoDriver']['LinkLastReleasePlatform']
            result, message, data = self.github_viewer.get_specific_asset_by_repo_name(repo_name=repo_name, asset_name=asset_name)
            if not result:
                return result, message, file_name

            geckodriver_version = data[0].get('version')
            url = data[0].get('asset').get('browser_download_url')
            asset_name = data[0].get('asset').get('name')
            
            logging.info(f'Started download geckodriver geckodriver_version: {geckodriver_version}')
            out_path = self.path + asset_name

            if os.path.exists(out_path):
                os.remove(out_path)

            logging.info(f'Started download geckodriver by url: {url}')

            file_name = wget.download(url=url, out=out_path)

            logging.info(f'Geckodriver was downloaded to path: {file_name}')

            time.sleep(2)

            if not self.filename:

                if asset_name.endswith('.tar.gz'):

                    archive_path = file_name
                    out_path = self.path
                    result, message = self.extractor.extract_all_tar_gz_archive(archive_path=archive_path, out_path=out_path)
                    if not result:
                        logging.error(message)
                        return result, message, file_name

                elif asset_name.endswith('.zip'):

                    archive_path = file_name
                    out_path = self.path
                    result, message = self.extractor.extract_all_zip_archive(archive_path=archive_path, out_path=out_path)
                    if not result:
                        logging.error(message)
                        return result, message, file_name

                else:
                    message = f'Unknown archive format was specified asset_name: {asset_name}'
                    logging.error(message)
                    return result_run, message, file_name

            else:

                archive_path = file_name
                out_path = self.path
                filename = setting['GeckoDriver']['LastReleasePlatform']
                filename_replace = self.filename
                result, message = self.extractor.extract_all_zip_archive_with_specific_name(archive_path=archive_path, 
                out_path=out_path, filename=filename, filename_replace=filename_replace)
                if not result:
                    logging.error(message)
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
        url : str = ''
        asset_name : str = ''

        try:

            repo_name = GeckoDriver._repo_name
            asset_name = self.setting['GeckoDriver']['LinkLastReleasePlatform']
            version = version
            result, message, data = self.github_viewer.get_specific_asset_by_specific_version_by_repo_name(repo_name=repo_name, 
            asset_name=asset_name, version=version)
            if not result:
                return result, message, file_name

            url = data[0].get('asset').get('browser_download_url')
            asset_name = data[0].get('asset').get('name')
            
            logging.info(f'Started download geckodriver specific_version: {version}')
            out_path = self.path + asset_name

            if os.path.exists(out_path):
                os.remove(out_path)

            logging.info(f'Started download geckodriver by url: {url}')

            file_name = wget.download(url=url, out=out_path)

            logging.info(f'Geckodriver was downloaded to path: {file_name}')

            time.sleep(2)

            if not self.filename:

                if asset_name.endswith('.tar.gz'):

                    archive_path = file_name
                    out_path = self.path
                    result, message = self.extractor.extract_all_tar_gz_archive(archive_path=archive_path, out_path=out_path)
                    if not result:
                        logging.error(message)
                        return result, message, file_name

                elif asset_name.endswith('.zip'):

                    archive_path = file_name
                    out_path = self.path
                    result, message = self.extractor.extract_all_zip_archive(archive_path=archive_path, out_path=out_path)
                    if not result:
                        logging.error(message)
                        return result, message, file_name

                else:
                    message = f'Unknown archive format was specified asset_name: {asset_name}'
                    logging.error(message)
                    return result_run, message, file_name

            else:

                archive_path = file_name
                out_path = self.path
                filename = setting['GeckoDriver']['LastReleasePlatform']
                filename_replace = self.filename
                result, message = self.extractor.extract_all_zip_archive_with_specific_name(archive_path=archive_path, 
                out_path=out_path, filename=filename, filename_replace=filename_replace)
                if not result:
                    logging.error(message)
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