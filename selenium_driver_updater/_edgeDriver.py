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

from typing import Any, Tuple

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from _setting import setting

import platform

from bs4 import BeautifulSoup

import stat

from util.extractor import Extractor
from util.requests_getter import RequestsGetter
from browsers._edgeBrowser import EdgeBrowser

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
            system_name (Union[str, list[str]]) : Specific OS for driver. Defaults to empty string.
        """
        self.setting : Any = setting

        self.path : str = path
                    
        self.upgrade : bool = bool(kwargs.get('upgrade'))

        self.chmod : bool = bool(kwargs.get('chmod'))

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))

        specific_system = str(kwargs.get('system_name'))
        self.system_name = "edgedriver_win64.zip" if specific_system == 'windows' or specific_system == 'windows64' else\
                           "edgedriver_win32.zip" if specific_system == 'windows32' else\
                           "edgedriver_linux64.zip" if specific_system == 'linux' or specific_system == 'linux64' else\
                           "edgedriver_mac64.zip" if specific_system == 'macos' else\
                           logging.error(f"You specified system_name: {specific_system} which unsupported by edgedriver - so used default instead.")\
                           if specific_system else ''

        self.specific_driver_name = ''
                           
        if not self.system_name:
        
            specific_filename = str(kwargs.get('filename'))
            self.filename = f"{specific_filename}.exe" if platform.system() == 'Windows' and specific_filename else\
                            specific_filename

            self.edgedriver_path : str =  self.path + str(self.setting['EdgeDriver']['LastReleasePlatform']) if not specific_filename else self.path + self.filename

        else:

            specific_filename = str(kwargs.get('filename'))
            self.filename = f"{specific_filename}.exe" if 'windows' in specific_system and specific_filename else\
                            specific_filename
                        
            self.specific_driver_name = "msedgedriver.exe" if 'windows' in specific_system else\
                                     "msedgedriver"

            self.edgedriver_path : str =  self.path + self.specific_driver_name if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date'))

        self.info_messages = bool(kwargs.get('info_messages'))

        self.extractor = Extractor
        self.requests_getter = RequestsGetter
        self.edgebrowser = EdgeBrowser(path=self.path, check_browser_is_up_to_date=self.check_browser_is_up_to_date)

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

            result, message = self.edgebrowser.main()
            if not result:
                logging.error(message)
                return result, message, driver_path

            if not self.version:

                result, message, driver_path = self.__check_if_edgedriver_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            else:

                result, message, driver_path = self.__download_driver(version=self.version)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __get_current_version_edgedriver(self) -> Tuple[bool, str, str]:
        """Gets current edgedriver version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current edgedriver version.

        Raises:
            SessionNotCreatedException: Occurs when current edgedriver could not start.

            WebDriverException: Occurs when current edgedriver could not start or critical error occured

            OSError: Occurs when chromedriver made for another CPU type

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''
        driver_version_terminal : str = ''
        
        try:

            if os.path.exists(self.edgedriver_path):
        
                process = subprocess.Popen([self.edgedriver_path, '--version'], stdout=subprocess.PIPE)
        
                driver_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string = re.findall(str(self.setting["Program"]["wedriverVersionPattern"]), str(driver_version_terminal))
                driver_version = find_string[0] if len(find_string) > 0 else ''

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
        url = str(self.setting['EdgeDriver']['LinkLastRelease'])

        try:
            
            result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
            if not result:
                logging.error(message)
                return result, message, latest_version

            soup = BeautifulSoup(json_data, 'html.parser')

            elements = soup.findAll('ul', attrs={'class' : 'bare driver-downloads'})
            if len(elements) == 0:
                elements = soup.findAll('div', attrs={'class' : 'bare driver-downloads'})
                
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
            
            latest_version = re.findall(str(self.setting["Program"]["wedriverVersionPattern"]), str(latest_version_element))[0]

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

            if self.check_driver_is_up_to_date and not self.system_name:

                result, message, is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if is_driver_up_to_date:
                    return True, message, self.edgedriver_path

            result, message, driver_path = self.__download_driver()
            if not result:
                logging.error(message)
                return result, message, driver_path

            if self.check_driver_is_up_to_date and not self.system_name:

                result, message, is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if not is_driver_up_to_date:
                    message = f'Problem with updating edgedriver current_version: {current_version} latest_version: {latest_version}'
                    logging.error(message)
                    message = 'Trying to download previous latest version of edgedriver'
                    logging.info(message)

                    result, message, driver_path = self.__download_driver(previous_version=True)
                    if not result:
                        logging.error(message)
                        return result, message, driver_path

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

            result, message, current_version = self.__get_current_version_edgedriver()
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

    def __get_latest_previous_version_edgedriver_via_requests(self) -> Tuple[bool, str, str]:
        """Gets previous latest edgedriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Empty string if function passed correctly, non-empty string if error.
            latest_version_previous (str)   : Latest previous version of edgedriver.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_previous_version : str = ''
        releases_latest_previous_version = []
        url = str(self.setting["EdgeDriver"]["LinkAllReleases"])

        try:

            result, message, latest_version = self.__get_latest_version_edgedriver()
            if not result:
                logging.error(message)
                return result, message, latest_previous_version

            latest_version_main = int(latest_version.split('.')[0])
            latest_previous_version_main = str(latest_version_main-1)

            result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
            if not result:
                logging.error(message)
                return result, message, latest_version

            all_releases = re.findall(self.setting["Program"]["wedriverVersionPattern"], json_data)
            for release in all_releases:
                if release.startswith(latest_previous_version_main):
                    releases_latest_previous_version.append(release)

            releases_latest_previous_version.sort(key=lambda s: list(map(int, s.split('.'))), reverse=True)
            latest_previous_version = releases_latest_previous_version[0]

            logging.info(f'Latest previous version of edgedriver: {latest_previous_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, latest_previous_version

    def __check_if_version_is_valid(self, url : str, version_url : str) -> Tuple[bool, str]:
        """Checks the specified version for existence.

        Args:
            url (str)           : Full download url of edgedriver.
            version_url (str)   : Version that will be downloaded.

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
        """
        result_run : bool = False
        message_run : str = ''
        archive_name : str = url.split("/")[len(url.split("/"))-1]
        url_test_valid = str(self.setting["EdgeDriver"]["LinkCheckVersionIsValid"]).format(version_url)
        version_valid : str = f"{version_url}/{archive_name}"

        try:

            result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url_test_valid)
            if not result:
                logging.error(message)
                return result, message

            if not version_valid in json_data:
                message = f'Wrong version or system_name was specified. version_valid: {version_valid} version_url: {version_url} url: {url}'
                logging.error(message)
                return False, message

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)
        
        return result_run, message_run

    def __download_driver(self, version : str = '', previous_version : bool = False) -> Tuple[bool, str, str]:
        """Function to download, delete or upgrade current chromedriver

        Args:
            version (str)               : Specific chromedriver version to download. Defaults to empty string.
            previous_version (boll)     : If true, chromedriver latest previous version will be downloaded. Defaults to False.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            file_name (str)         : Path to unzipped driver.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        file_name : str = ''
        url : str = ''
        file_name : str = ''
        driver_notes_path : str = self.path + 'Driver_Notes'
        latest_previous_version : str = ''
        latest_version : str = ''

        try:

            if self.upgrade:

                result, message = self.__delete_current_edgedriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, file_name

            if version:

                url = str(self.setting["EdgeDriver"]["LinkLastReleaseFile"]).format(version)
                logging.info(f'Started download edgedriver specific_version: {version}')

            elif previous_version:

                result, message, latest_previous_version = self.__get_latest_previous_version_edgedriver_via_requests()
                if not result:
                    logging.error(message)
                    return result, message, file_name

                logging.info(f'Started download edgedriver latest_previous_version: {latest_previous_version}')
                url = str(self.setting["EdgeDriver"]["LinkLastReleaseFile"]).format(latest_previous_version)

            else:

                result, message, latest_version = self.__get_latest_version_edgedriver()
                if not result:
                    logging.error(message)
                    return result, message, file_name
                
                logging.info(f'Started download edgedriver latest_version: {latest_version}')
                url = str(self.setting["EdgeDriver"]["LinkLastReleaseFile"]).format(latest_version)

            if self.system_name:
                url = url.replace(url.split("/")[len(url.split("/"))-1], '')
                url = url + self.system_name

                logging.info(f'Started downloading chromedriver for specific system: {self.system_name}')

            if version or self.system_name:
                version_url = version if version else latest_previous_version if latest_previous_version else latest_version
                result, message = self.__check_if_version_is_valid(url=url, version_url=version_url)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            archive_name = url.split("/")[len(url.split("/"))-1]
            out_path = self.path + archive_name

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
                filename = str(self.setting['EdgeDriver']['LastReleasePlatform']) if not self.specific_driver_name else self.specific_driver_name
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

            logging.info(f'Edgedriver was successfully unpacked by path: {file_name}')

            if self.chmod:

                result, message = self.__chmod_driver()
                if not result:
                    return result, message, file_name

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, file_name