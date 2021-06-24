import subprocess
import wget
import os
import traceback
import logging
import time
import os

from typing import Tuple

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from _setting import setting

import platform

import stat

from util.extractor import Extractor
from util.github_viewer import GithubViewer
from util.requests_getter import RequestsGetter
from browsers._firefoxBrowser import FirefoxBrowser

import re

from pathlib import Path

from typing import Any

class GeckoDriver():

    _repo_name = 'mozilla/geckodriver'
    
    def __init__(self, path : str,**kwargs):
        """Class for working with Selenium geckodriver binary

        Args:
            path (str)                          : Specified path which will used for downloading or updating Selenium geckodriver binary. Must be folder path.
            upgrade (bool)                      : If true, it will overwrite existing driver in the folder. Defaults to False.
            chmod (bool)                        : If true, it will make geckodriver binary executable. Defaults to True.
            check_driver_is_up_to_date (bool)   : If true, it will check driver version before and after upgrade. Defaults to False.
            filename (str)                      : Specific name for geckodriver. If given, it will replace name for geckodriver.
            version (str)                       : Specific version for geckodriver. If given, it will downloads given version.
            check_browser_is_up_to_date (bool)  : If true, it will check firefox browser version before geckodriver update or upgrade.
            system_name (Union[str, list[str]]) : Specific OS for driver. Defaults to empty string.
        """
        self.setting : Any = setting

        self.path : str = path
                    
        self.upgrade : bool = bool(kwargs.get('upgrade'))

        self.chmod : bool = bool(kwargs.get('chmod'))

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))

        specific_system = str(kwargs.get('system_name'))
        self.system_name =  "geckodriver-v{}-win64.zip" if specific_system == 'windows' or specific_system == 'windows64' else\
                            "geckodriver-v{}-win32.zip" if specific_system == 'windows32' else\
                            "geckodriver-v{}-linux64.tar.gz" if specific_system == 'linux' or specific_system == 'linux64' else\
                            "geckodriver-v{}-linux32.tar.gz" if specific_system == 'linux32' else\
                            "geckodriver-v{}-macos-aarch64.tar.gz" if specific_system == 'macos_m1' else\
                            "geckodriver-v{}-macos.tar.gz" if specific_system == 'macos' else\
                           logging.error(f"You specified system_name: {specific_system} which unsupported by geckodriver - so used default instead.")\
                           if specific_system else ''

        self.specific_driver_name = ''
                           
        if not self.system_name:
        
            specific_filename = str(kwargs.get('filename'))
            self.filename = f"{specific_filename}.exe" if platform.system() == 'Windows' and specific_filename else\
                            specific_filename

            self.geckodriver_path : str =  self.path + self.setting['GeckoDriver']['LastReleasePlatform'] if not specific_filename else self.path + self.filename

        else:

            specific_filename = str(kwargs.get('filename'))
            self.filename = f"{specific_filename}.exe" if 'windows' in specific_system and specific_filename else\
                            specific_filename
                        
            self.specific_driver_name =    "geckodriver.exe" if 'windows' in specific_system else\
                                    "geckodriver"

            self.geckodriver_path : str =  self.path + self.specific_driver_name if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date'))

        self.info_messages = bool(kwargs.get('info_messages'))

        self.extractor = Extractor
        self.github_viewer = GithubViewer
        self.requests_getter = RequestsGetter
        self.firefoxbrowser = FirefoxBrowser(path=self.path, check_browser_is_up_to_date=self.check_browser_is_up_to_date)

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

            result, message = self.firefoxbrowser.main()
            if not result:
                logging.error(message)
                return result, message, driver_path

            if not self.version:

                result, message, driver_path = self.__check_if_geckodriver_is_up_to_date()
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

    def __get_current_version_geckodriver(self) -> Tuple[bool, str, str]:
        """Gets current geckodriver version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current geckodriver version.

        Raises:

            OSError: Occurs when geckodriver maded for another CPU type

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''
        driver_version_terminal : str = ''
        
        try:
            
            if Path(self.geckodriver_path).exists():
            
                process = subprocess.Popen([self.geckodriver_path, '--version'], stdout=subprocess.PIPE)
        
                driver_version_terminal = process.communicate()[0].decode('UTF-8')
                
                find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_terminal)
                driver_version = find_string[0] if len(find_string) > 0 else ''

                logging.info(f'Current version of geckodriver: {driver_version}')

            result_run = True

        except OSError:
            message_run = f'OSError error: {traceback.format_exc()}' #probably [Errno 86] Bad CPU type in executable:
            logging.error(message_run)
            return True, message_run, driver_version

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
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
            message_run = f'Unexcepted error: {traceback.format_exc()}'
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

            if Path(self.geckodriver_path).exists():
                logging.info(f'Deleted existing geckodriver geckodriver_path: {self.geckodriver_path}')
                Path(self.geckodriver_path).unlink()
            

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
    
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

            if self.check_driver_is_up_to_date and not self.system_name:

                result, message, is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if is_driver_up_to_date:
                    return True, message, self.geckodriver_path

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
                    message = f'Problem with updating geckodriver current_version: {current_version} latest_version: {latest_version}'
                    logging.error(message)
                    message = 'Trying to download previous latest version of geckodriver'
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

            result, message, current_version = self.__get_current_version_geckodriver()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

            if not current_version:
                return True, message_run, is_driver_up_to_date, current_version, latest_version

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
            message_run = f'Unexcepted error: {traceback.format_exc()}'
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

            if Path(self.geckodriver_path).exists():

                logging.info('Trying to give geckodriver needed permissions')

                st = os.stat(self.geckodriver_path)
                os.chmod(self.geckodriver_path, st.st_mode | stat.S_IEXEC)

                logging.info('Needed rights for geckodriver were successfully issued')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __get_latest_previous_version_geckodriver_via_requests(self) -> Tuple[bool, str, str]:
        """Gets previous latest geckodriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Empty string if function passed correctly, non-empty string if error.
            latest_version_previous (str)   : Latest previous version of geckodriver.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_previous_version : str = ''

        try:

            repo_name = GeckoDriver._repo_name
            result, message, json_data = self.github_viewer.get_all_releases_data_by_repo_name(repo_name=repo_name)
            if not result:
                return result, message, latest_previous_version

            latest_previous_version = latest_previous_version = json_data[1].get('name')

            logging.info(f'Latest previous version of geckodriver: {latest_previous_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_previous_version

    def __check_if_version_is_valid(self, url : str, version_url : str) -> Tuple[bool, str]:
        """Checks the specified version for existence.

        Args:
            url (str)           : Full download url of geckodriver.
            version_url (str)   : Version that will be downloaded.

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
        """
        result_run : bool = False
        message_run : str = ''
        archive_name : str = url.split("/")[len(url.split("/"))-1]
        is_found : bool = False

        try:

            result, message, json_data = self.github_viewer.get_all_releases_data_by_repo_name(GeckoDriver._repo_name)
            if not result:
                logging.error(message)
                return result, message

            for data in json_data:
                if data.get('name') == version_url:
                    for asset in data.get('assets'):
                        if asset.get('name') == archive_name:
                            is_found = True
                            break
                    break

            if not is_found:
                message = f'Wrong version or system_name was specified. version_url: {version_url} url: {url}'
                logging.error(message)
                return False, message

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)
        
        return result_run, message_run
        
    def __download_driver(self, version : str = '', previous_version : bool = False) -> Tuple[bool, str, str]:
        """Function to download, delete or upgrade current geckodriver

        Args:
            version (str)               : Specific geckodriver version to download. Defaults to empty string.
            previous_version (boll)     : If true, geckodriver latest previous version will be downloaded. Defaults to False.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path to unzipped driver.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        url : str = ''
        latest_version : str = ''
        latest_previous_version : str = ''

        driver_path : str = ''

        try:

            if self.upgrade:

                result, message = self.__delete_current_geckodriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            if version:
                
                url = self.setting["GeckoDriver"]["LinkLastReleasePlatform"].format(version, version)
                logging.info(f'Started download geckodriver specific_version: {version}')

            elif previous_version:

                result, message, latest_previous_version = self.__get_latest_previous_version_geckodriver_via_requests()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                url = self.setting["GeckoDriver"]["LinkLastReleasePlatform"].format(latest_previous_version, latest_previous_version)
                logging.info(f'Started download geckodriver latest_previous_version: {latest_previous_version}')

            else:

                result, message, latest_version = self.__get_latest_version_geckodriver()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                url = self.setting["GeckoDriver"]["LinkLastReleasePlatform"].format(latest_version, latest_version)
                logging.info(f'Started download geckodriver latest_version: {latest_version}')

            if self.system_name:
                url = url.replace(url.split("/")[len(url.split("/"))-1], '')
                url = url + self.system_name.format(latest_version) if latest_version else url + self.system_name.format(latest_previous_version) if latest_previous_version else\
                url + self.system_name.format(version)    

                logging.info(f'Started downloading geckodriver for specific system: {self.system_name}')

            if any([version, self.system_name ,latest_previous_version]):
                version_url = version if version else latest_previous_version if latest_previous_version else latest_version
                result, message = self.__check_if_version_is_valid(url=url, version_url=version_url)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            archive_name = url.split("/")[len(url.split("/"))-1]
            out_path = self.path + archive_name

            if Path(out_path).exists():
                Path(out_path).unlink()

            logging.info(f'Started download geckodriver by url: {url}')

            if self.info_messages:
                archive_path = wget.download(url=url, out=out_path)
            else:
                archive_path = wget.download(url=url, out=out_path, bar=None)
            time.sleep(2)

            logging.info(f'Geckodriver was downloaded to path: {archive_path}')

            out_path = self.path

            if not self.filename:

                result, message = self.extractor.extract_and_detect_archive_format(archive_path=archive_path, out_path=out_path)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            else:

                filename = self.setting['GeckoDriver']['LastReleasePlatform'] if not self.specific_driver_name else self.specific_driver_name
                filename_replace = self.filename
                result, message = self.extractor.extract_all_zip_archive_with_specific_name(archive_path=archive_path, 
                out_path=out_path, filename=filename, filename_replace=filename_replace)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            if Path(archive_path).exists():
                Path(archive_path).unlink()

            driver_path = self.geckodriver_path

            logging.info(f'Geckodriver was successfully unpacked by path: {driver_path}')

            if self.chmod:

                result, message = self.__chmod_driver()
                if not result:
                    return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path