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

import stat

from shutil import copyfile

from util.extractor import Extractor
from util.github_viewer import GithubViewer
from util.requests_getter import RequestsGetter

from bs4 import BeautifulSoup

import pathlib

import re

class OperaDriver():

    _repo_name = 'operasoftware/operachromiumdriver'
    
    def __init__(self, path : str, **kwargs):
        """Class for working with Selenium operadriver binary

        Args:
            path (str)                          : Specified path which will used for downloading or updating Selenium operadriver binary. Must be folder path.
            upgrade (bool)                      : If true, it will overwrite existing driver in the folder. Defaults to False.
            chmod (bool)                        : If true, it will make operadriver binary executable. Defaults to True.
            check_driver_is_up_to_date (bool)   : If true, it will check driver version before and after upgrade. Defaults to False.
            filename (str)                      : Specific name for operadriver. If given, it will replace name for operadriver. Defaults to empty string.
            version (str)                       : Specific version for operadriver. If given, it will downloads given version. Defaults to empty string.
            check_browser_is_up_to_date (bool)  : If true, it will check opera browser version before operadriver update/upgrade.
        """
        self.setting = setting

        self.path : str = path
                    
        self.upgrade : bool = bool(kwargs.get('upgrade'))

        self.chmod : bool = bool(kwargs.get('chmod'))

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))
        
        specific_filename = str(kwargs.get('filename'))
        self.filename = f"{specific_filename}.exe" if platform.system() == 'Windows' and specific_filename else\
                        specific_filename

        self.operadriver_path : str =  self.path + self.setting['OperaDriver']['LastReleasePlatform'] if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date'))

        self.info_messages = bool(kwargs.get('info_messages'))

        self.extractor = Extractor
        self.github_viewer = GithubViewer
        self.requests_getter = RequestsGetter

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

            OSError: Occurs when operadriver made for another CPU type

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''

        try:

            if os.path.exists(self.operadriver_path):

                result, message, driver_version = self.__get_current_version_operadriver_via_terminal()
                if not result:
                    logging.error(message)
                    message = 'Trying to get current version of operadriver via webdriver'
                    logging.info(message)
                
                if not result or not driver_version:

                    driver = webdriver.Opera(executable_path = self.operadriver_path)

                    driver_version_selenium = str(driver.capabilities['opera']['operadriverVersion'])

                    find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_selenium)
                    driver_version = find_string[0] if len(find_string) > 0 else driver_version_selenium.split(' ')[0]

                    driver.close()
                    driver.quit()

                logging.info(f'Current version of operadriver: {driver_version}')

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
            
            repo_name = OperaDriver._repo_name
            result, message, json_data = self.github_viewer.get_latest_release_data_by_repo_name(repo_name=repo_name)
            if not result:
                return result, message, latest_version

            latest_version = json_data.get('name')

            logging.info(f'Latest version of operadriver: {latest_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __delete_current_operadriver_for_current_os(self) -> Tuple[bool, str]:
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
                file_to_rem = pathlib.Path(self.operadriver_path)
                file_to_rem.unlink()
            

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
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
        url : str = ''
        operadriver_version : str = ''

        try:

            repo_name = OperaDriver._repo_name
            asset_name = self.setting["OperaDriver"]["NamePlatformRelease"]
            result, message, data = self.github_viewer.get_specific_asset_by_repo_name(repo_name=repo_name, asset_name=asset_name)
            if not result:
                return result, message, file_name

            operadriver_version = data[0].get('version')
            url = data[0].get('asset').get('browser_download_url')
            
            logging.info(f'Started download operadriver operadriver_version: {operadriver_version}')
            out_path = self.path + data[0].get('asset').get('name')

            if os.path.exists(out_path):
                os.remove(out_path)

            logging.info(f'Started download operadriver by url: {url}')

            if self.info_messages:
                file_name = wget.download(url=url, out=out_path)
            else:
                file_name = wget.download(url=url, out=out_path, bar=None)

            logging.info(f'Operadriver was downloaded to path: {file_name}')

            time.sleep(2)

            archive_path = file_name
            out_path = self.path
            result, message = self.extractor.extract_all_zip_archive(archive_path=archive_path, out_path=out_path)
            if not result:
                logging.error(message)
                return result, message, file_name

            archive_folder_path = self.path + self.setting["OperaDriver"]["NamePlatformRelease"]
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

            logging.info(f'Operadriver was successfully unpacked by path: {file_name}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, file_name
    
    def __check_if_operadriver_is_up_to_date(self) -> Tuple[bool, str, str]:
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

                result, message = self.__delete_current_operadriver_for_current_os()
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
            message_run = f'Unexcepted error: {traceback.format_exc()}'
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

            if not current_version:
                return True, message_run, is_driver_up_to_date, current_version, latest_version

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
            message_run = f'Unexcepted error: {traceback.format_exc()}'
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

            copyfile(new_path, renamed_driver_path)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
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

                logging.info('Needed rights for operadriver were successfully issued')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def main(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates operadriver binary or
        downloads specific version of operadriver.

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

            if self.check_browser_is_up_to_date:

                result, message = self.__check_if_opera_browser_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            if not self.version:

                result, message, driver_path = self.__check_if_operadriver_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            else:

                result, message, driver_path = self.__download_operadriver_for_specific_version(version=self.version)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __download_operadriver_for_specific_version(self, version : str) -> Tuple[bool, str, str]:
        """Downloads specific version of operadriver

        Args:
            version (str)    : Specific version of operadriver.

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

            if self.upgrade:

                result, message = self.__delete_current_operadriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result, message, driver_path = self.__get_specific_version_operadriver_for_current_os(version=version)
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

    def __get_specific_version_operadriver_for_current_os(self, version : str) -> Tuple[bool, str, str]:
        """Download specific version of operadriver to folder

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

        try:

            repo_name = OperaDriver._repo_name
            asset_name = self.setting["OperaDriver"]["NamePlatformRelease"]
            version = version
            result, message, data = self.github_viewer.get_specific_asset_by_specific_version_by_repo_name(repo_name=repo_name, 
            asset_name=asset_name, version=version)
            if not result:
                return result, message, file_name

            url = data[0].get('asset').get('browser_download_url')
            
            logging.info(f'Started download operadriver specific_version: {version}')
            out_path = self.path + data[0].get('asset').get('name')

            if os.path.exists(out_path):
                os.remove(out_path)

            logging.info(f'Started download operadriver by url: {url}')

            if self.info_messages:
                file_name = wget.download(url=url, out=out_path)
            else:
                file_name = wget.download(url=url, out=out_path, bar=None)
            time.sleep(2)

            logging.info(f'Operadriver was downloaded to path: {file_name}')

            archive_path = file_name
            out_path = self.path
            result, message = self.extractor.extract_all_zip_archive(archive_path=archive_path, out_path=out_path)
            if not result:
                logging.error(message)
                return result, message, file_name

            archive_folder_path = self.path + self.setting["OperaDriver"]["NamePlatformRelease"]
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
        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, file_name

    def __check_if_opera_browser_is_up_to_date(self) -> Tuple[bool, str]:
        """Сhecks for the latest version of opera browser

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

            operabrowser_updater_path = str(self.setting["OperaBrowser"]["OperaBrowserUpdaterPath"])
            if not operabrowser_updater_path:
                message = f'Parameter "check_browser_is_up_to_date" has not been optimized for your OS yet. Please wait for the new releases.'
                logging.info(message)
                return True, message

            if not os.path.exists(operabrowser_updater_path):
                message = f'operabrowser_updater_path: {operabrowser_updater_path} is not exists. Please report your OS information and path to {operabrowser_updater_path} file in repository.'
                logging.info(message)
                return True, message

            result, message, is_browser_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_opera_browser()
            if not result:
                logging.error(message)
                return result, message

            if not is_browser_up_to_date:

                result, message = self.__get_latest_opera_browser_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message

                result, message, is_browser_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_opera_browser()
                if not result:
                    logging.error(message)
                    return result, message

                if not is_browser_up_to_date:
                    message = f'Problem with updating opera browser current_version: {current_version} latest_version: {latest_version}'
                    logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __get_current_version_opera_browser_selenium(self) -> Tuple[bool, str, str]:
        """Gets current opera browser version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            browser_version (str)   : Current opera browser version.

        Raises:
            SessionNotCreatedException: Occurs when current operadriver could not start.

            WebDriverException: Occurs when current operadriver could not start or critical error occured.

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        browser_version : str = ''
        
        try:
            
            result, message, browser_version = self.__get_current_version_opera_browser_selenium_via_terminal()
            if not result:
                logging.error(message)
                message = 'Trying to get current version of opera browser via operadriver'
                logging.info(message)
            
            if os.path.exists(self.operadriver_path) and not result or not browser_version:

                driver = webdriver.Opera(executable_path = self.operadriver_path)
                browser_version = driver.execute_script("return navigator.userAgent").split('/')[5]
                driver.close()
                driver.quit()

            logging.info(f'Current version of opera browser: {browser_version}')

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

    def __get_latest_version_opera_browser(self) -> Tuple[bool, str, str]:
        """Gets latest opera browser version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            latest_version (str)    : Latest version of opera browser.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_version : str = ''
        latest_version_element : str = ''

        try:
            
            url = self.setting["OperaBrowser"]["LinkAllReleases"]
            result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
            if not result:
                logging.error(message)
                return result, message, latest_version

            soup = BeautifulSoup(json_data, 'html.parser')
            changelogs = soup.findAll('h1', attrs={'class' : 'entry-title'})

            for changelog in changelogs:
                latest_version_element = changelog.text.replace('\n', '')

                if 'macos' in changelog.text.lower() and platform.system() != 'Darwin':
                    continue

                else:
                    break

            if not latest_version_element:
                message = f'Latest main version of opera browser could not be determinated. Maybe the element is changed.'
                logging.error(message)
                return result_run, message, latest_version

            latest_version = re.findall(self.setting["Program"]["wedriverVersionPattern"], latest_version_element)[0]
            
            logging.info(f'Latest version of opera browser: {latest_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __get_latest_opera_browser_for_current_os(self) -> Tuple[bool, str]:
        """Trying to update opera browser to its latest version

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
            
        update_command : str = self.setting["OperaBrowser"]["OperaBrowserUpdater"]
        
        try:

            message = f'Trying to update opera browser to the latest version.'
            logging.info(message)

            if platform.system() == 'Linux':

                if is_admin:
                    os.system(update_command)

                elif not is_admin:
                    message = 'You have not ran library with sudo privileges to update opera browser - so updating is impossible.'
                    logging.error(message)
                    return True, message_run
            
            else:

                os.system(update_command)
                time.sleep(60) #wait for the updating
            
            message = f'Opera browser was successfully updated to the latest version.'
            logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __compare_current_version_and_latest_version_opera_browser(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of opera browser to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Empty string if function passed correctly, non-empty string if error.
            is_browser_up_to_date (bool)    : If true current version of opera browser is up to date. Defaults to False.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        is_browser_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''
        
        try:

            result, message, current_version = self.__get_current_version_opera_browser_selenium()
            if not result:
                logging.error(message)
                return result, message, is_browser_up_to_date, current_version, latest_version

            result, message, latest_version = self.__get_latest_version_opera_browser()
            if not result:
                logging.error(message)
                return result, message, is_browser_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_browser_up_to_date = True
                message = f"Your existing opera browser is up to date. current_version: {current_version} latest_version: {latest_version}"
                logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_browser_up_to_date, current_version, latest_version

    def __get_current_version_opera_browser_selenium_via_terminal(self) -> Tuple[bool, str, str]:
        """Gets current opera browser version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            browser_version (str)   : Current opera browser version.

        Raises:

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        browser_version : str = ''
        browser_version_terminal : str = ''
        
        try:
            
            operabrowser_path = self.setting["OperaBrowser"]["Path"]
            if operabrowser_path:

                logging.info('Trying to get current version of opera browser via terminal')

                if platform.system() == 'Windows':

                    process = subprocess.Popen(operabrowser_path, stdout=subprocess.PIPE)
        
                    browser_version_terminal = process.communicate()[0].decode('UTF-8')
                    find_string_terminal = re.findall("Opera.*", browser_version_terminal)
                    
                    browser_version_terminal = find_string_terminal[0] if len(find_string_terminal) > 0 else ''

                elif platform.system() == 'Darwin':
                    process = subprocess.Popen([operabrowser_path, '--version'], stdout=subprocess.PIPE)
        
                    browser_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], browser_version_terminal)
                browser_version = find_string[0] if len(find_string) > 0 else ''

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)
        
        return result_run, message_run, browser_version

    def __get_current_version_operadriver_via_terminal(self) -> Tuple[bool, str, str]:
        """Gets current operadriver version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current operadriver version.

        Raises:

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''
        driver_version_terminal : str = ''
        
        try:
            
            if os.path.exists(self.operadriver_path):

                logging.info('Trying to get current version of operadriver via terminal')
            
                process = subprocess.Popen([self.operadriver_path, '--version'], stdout=subprocess.PIPE)
        
                driver_version_terminal = process.communicate()[0].decode('UTF-8')
                
                find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_terminal)
                driver_version = find_string[0] if len(find_string) > 0 else ''

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)
        
        return result_run, message_run, driver_version