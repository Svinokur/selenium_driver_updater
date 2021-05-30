import shutil
import subprocess
import wget
import os
import traceback
import logging
import time
import stat
import os

import platform

from typing import Tuple

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from _setting import setting

from selenium import webdriver

from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

from util.extractor import Extractor
from util.github_viewer import GithubViewer
from util.requests_getter import RequestsGetter

import pathlib

import re

from shutil import copyfile

class PhantomJS():


    _repo_name = 'ariya/phantomjs'
    _tmp_folder_path = 'tmp'
    
    def __init__(self, path : str, **kwargs):
        """Class for working with Selenium phantomjs binary

        Args:
            path (str)                          : Specified path which will used for downloading or updating Selenium phantomjs binary. Must be folder path.
            upgrade (bool)                      : If true, it will overwrite existing driver in the folder. Defaults to False.
            chmod (bool)                        : If true, it will make phantomjs binary executable. Defaults to True.
            check_driver_is_up_to_date (bool)   : If true, it will check driver version before and after upgrade. Defaults to False.
            filename (str)                      : Specific name for phantomjs. If given, it will replace name for phantomjs.
            version (str)                       : Specific version for phantomjs. If given, it will downloads given version.
        """
        self.setting = setting

        self.path : str = path
                    
        self.upgrade : bool = bool(kwargs.get('upgrade'))

        self.chmod : bool = bool(kwargs.get('chmod'))

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))
        
        specific_filename = str(kwargs.get('filename'))
        self.filename = f"{specific_filename}.exe" if platform.system() == 'Windows' and specific_filename else\
                        specific_filename

        self.phantomjs_path : str =  self.path + self.setting["PhantomJS"]["LastReleasePlatform"] if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.info_messages = bool(kwargs.get('info_messages'))

        self.extractor = Extractor
        self.github_viewer = GithubViewer
        self.requests_getter = RequestsGetter

    def __get_current_version_phantomjs(self) -> Tuple[bool, str, str]:
        """Gets current phantomjs version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current driver version.

        Raises:
            SessionNotCreatedException: Occurs when current phantomjs could not start.

            WebDriverException: Occurs when current phantomjs could not start or critical error occured

            OSError: Occurs when phantomjs made for another CPU type

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''

        try:

            if os.path.exists(self.phantomjs_path):

                result, message, driver_version = self.__get_current_version_phantomjs_via_terminal()
                if not result:
                    logging.error(message)
                    message = 'Trying to get current version of phantomjs via webdriver'
                    logging.info(message)
                
                if not True or not driver_version:

                    driver = webdriver.PhantomJS(executable_path = self.phantomjs_path)
                    driver_version = str(driver.capabilities['version'])
                    driver.close()
                    driver.quit()
        
                logging.info(f'Current version of phantomjs: {driver_version}')

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

    def __get_current_version_phantomjs_via_terminal(self) -> Tuple[bool, str, str]:
        """Gets current phantomjs version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current phantomjs version.

        Raises:

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''
        driver_version_terminal : str = ''
        
        try:
            
            logging.info('Trying to get current version of phantomjs via terminal')
        
            process = subprocess.Popen([self.phantomjs_path, '--version'], stdout=subprocess.PIPE)
    
            driver_version_terminal = process.communicate()[0].decode('UTF-8')

            find_string = re.findall(self.setting["GeckoDriver"]["geckodriverVersionPattern"], driver_version_terminal)
            driver_version = find_string[0] if len(find_string) > 0 else ''

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)
        
        return result_run, message_run, driver_version

    def __get_latest_version_phantomjs(self) -> Tuple[bool, str, str]:
        """Gets latest phantomjs version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            latest_version (str)    : Latest version of phantomjs.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_version : str = ''

        try:
            
            repo_name = PhantomJS._repo_name
            result, message, json_data = self.github_viewer.get_latest_release_tag_by_repo_name(repo_name=repo_name)
            if not result:
                return result, message, latest_version

            find_string = re.findall(self.setting["GeckoDriver"]["geckodriverVersionPattern"], json_data.get('ref'))
            latest_version = find_string[0] if len(find_string) > 0 else ''

            if not latest_version:
                message = 'Unable to determine latest version of PhantomJS, maybe the tags were deleted.'
                logging.error(message)
                return False, message, latest_version

            logging.info(f'Latest version of phantomjs: {latest_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __compare_current_version_and_latest_version_phantomjs(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of phantomjs to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Empty string if function passed correctly, non-empty string if error.
            is_driver_up_to_date (bool) : If true current version of phantomjs is up to date. Defaults to False.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        is_driver_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''
        
        try:

            result, message, current_version = self.__get_current_version_phantomjs()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version
            
            if not current_version:
                return True, message_run, is_driver_up_to_date, current_version, latest_version

            result, message, latest_version = self.__get_latest_version_phantomjs()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_driver_up_to_date = True
                message = f'Your existing phantomjs is up to date. current_version: {current_version} latest_version: {latest_version}' 
                logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_driver_up_to_date, current_version, latest_version

    def __check_if_phantomjs_is_up_to_date(self) -> Tuple[bool, str, str]:
        """Сhecks for the latest version, downloads or updates phantomjs binary

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where phantomjs was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''
        
        try:

            if self.check_driver_is_up_to_date:

                result, message, is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_phantomjs()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if is_driver_up_to_date:
                    return True, message, self.phantomjs_path

            result, message, driver_path = self.__download_driver()
            if not result:
                logging.error(message)
                return result, message, driver_path
            
            if self.check_driver_is_up_to_date:

                result, message, is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_phantomjs()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if not is_driver_up_to_date:
                    message = f'Problem with updating phantomjs current_version: {current_version} latest_version: {latest_version}'
                    logging.error(message)
                    return result_run, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __delete_current_phantomjs_for_current_os(self) -> Tuple[bool, str]:
        """Deletes phantomjs from folder if parameter "upgrade" is True


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

            if os.path.exists(self.phantomjs_path):
                
                logging.info(f'Deleted existing phantomjs phantomjs_path: {self.phantomjs_path}')
                file_to_rem = pathlib.Path(self.phantomjs_path)
                file_to_rem.unlink()

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __chmod_driver(self) -> Tuple[bool, str]:
        """Tries to give phantomjs binary needed permissions

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

            if os.path.exists(self.phantomjs_path):

                logging.info('Trying to give phantomjs needed permissions')

                st = os.stat(self.phantomjs_path)
                os.chmod(self.phantomjs_path, st.st_mode | stat.S_IEXEC)

                logging.info('Needed rights for phantomjs were successfully issued')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __rename_driver(self, archive_folder_path : str, archive_driver_path : str) -> Tuple[bool, str]:
        """Renames phantomjs if it was given

        Args:
            archive_folder_path (str)       : Path to the main folder
            archive_driver_path (str)       : Path to the phantomjs archive

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

            new_path = archive_folder_path + os.path.sep + self.filename if not archive_folder_path.endswith(os.path.sep) else archive_folder_path + self.filename

            if os.path.exists(new_path):
                os.remove(new_path)

            os.rename(archive_driver_path, new_path)
            
            renamed_driver_path = self.path + self.filename
            if os.path.exists(renamed_driver_path):
                os.remove(renamed_driver_path)

            copyfile(new_path, renamed_driver_path)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
    
    def main(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates phantomjs binary or
        downloads specific version of phantomjs.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where phantomjs was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''
        
        try:

            if not self.version:

                result, message, driver_path = self.__check_if_phantomjs_is_up_to_date()
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

    def __download_driver(self, version : str = ''):
        """Download specific version of phantomjs to folder

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

            if self.upgrade:

                result, message = self.__delete_current_phantomjs_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, file_name
            
            if version:

                logging.info(f'Started download phantomjs: {version}')

                url = self.setting["PhantomJS"]["LinkLastReleaseFile"].format(version)
                result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url, return_text = False, no_error_status_code=True)
                if not result:
                    logging.error(message)
                    return result, message, file_name

                if status_code != 200:
                    message = f'Specific binary was not found, wrong version was specified. version: {version}'
                    logging.error(message)
                    return result_run, message, file_name

            else:
                result, message, latest_version = self.__get_latest_version_phantomjs()
                if not result:
                    logging.error(message)
                    return result, message, file_name

                logging.info(f'Started download phantomjs latest_version: {latest_version}')

                url = self.setting["PhantomJS"]["LinkLastReleaseFile"].format(latest_version)

            out_path = self.path + url.split('/')[6]

            if os.path.exists(out_path):
                os.remove(out_path)

            logging.info(f'Started download phantomjs by url: {url}')

            if self.info_messages:
                file_name = wget.download(url=url, out=out_path)
            else:
                file_name = wget.download(url=url, out=out_path, bar=None)
            time.sleep(2)

            logging.info(f'PhantomJS was downloaded to path: {file_name}')

            if file_name.endswith('.zip'):

                archive_path = file_name
                out_path = self.path
                result, message = self.extractor.extract_all_zip_archive(archive_path=archive_path, out_path=out_path)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            elif file_name.endswith('.tar.bz2'):

                archive_path = file_name
                out_path = self.path
                result, message = self.extractor.extract_all_tar_bz2_archive(archive_path=archive_path, out_path=out_path)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            elif file_name.endswith('.tar.gz'):

                archive_path = file_name
                out_path = self.path
                result, message = self.extractor.extract_all_tar_gz_archive(archive_path=archive_path, out_path=out_path)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            else:
                message = f'Unknown archive format was specified file_name: {file_name}'
                logging.error(message)
                return result_run, message, file_name

            archive_path_folder = self.path + url.split('/')[6].replace('.zip', '').replace(".tar.bz2", '') + os.path.sep
            archive_path_folder_bin = archive_path_folder + 'bin' +  os.path.sep
            driver_archive_path = archive_path_folder_bin + self.setting["PhantomJS"]["LastReleasePlatform"]

            if not self.filename:

                copyfile(driver_archive_path, self.path + self.setting["PhantomJS"]["LastReleasePlatform"])

            else:

                result, message = self.__rename_driver(archive_folder_path=archive_path_folder_bin, archive_driver_path=driver_archive_path)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            if os.path.exists(archive_path_folder):
                shutil.rmtree(archive_path_folder)
            
            file_name = self.phantomjs_path

            logging.info(f'PhantomJS was successfully unpacked by path: {file_name}')

            if self.chmod:

                result, message = self.__chmod_driver()
                if not result:
                    return result, message, file_name

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, file_name