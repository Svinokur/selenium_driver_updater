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

from typing import Any, Tuple

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from _setting import setting

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
            system_name (Union[str, list[str]]) : Specific OS for driver. Defaults to empty string.
        """
        self.setting : Any = setting

        self.path : str = path
                    
        self.upgrade : bool = bool(kwargs.get('upgrade'))

        self.chmod : bool = bool(kwargs.get('chmod'))

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))

        specific_system = str(kwargs.get('system_name'))
        self.system_name =  "phantomjs-{}-windows.zip" if specific_system == 'windows' or specific_system == 'windows64' else\
                            "phantomjs-{}-windows.zip" if specific_system == 'windows32' else\
                            "phantomjs-{}-linux-x86_64.tar.bz2" if specific_system == 'linux' or specific_system == 'linux64' else\
                            "phantomjs-{}-linux-i686.tar.bz2" if specific_system == 'linux32' else\
                            "phantomjs-{}-macosx.zip" if specific_system == 'macos' else\
                           logging.error(f"You specified system_name: {specific_system} which unsupported by phantomjs - so used default instead.")\
                           if specific_system else ''

        self.specific_driver_name = ''
                           
        if not self.system_name:
        
            specific_filename = str(kwargs.get('filename'))
            self.filename = f"{specific_filename}.exe" if platform.system() == 'Windows' and specific_filename else\
                            specific_filename

            self.phantomjs_path : str =  self.path + self.setting["PhantomJS"]["LastReleasePlatform"] if not specific_filename else self.path + self.filename

        else:

            specific_filename = str(kwargs.get('filename'))
            self.filename = f"{specific_filename}.exe" if 'windows' in specific_system and specific_filename else\
                            specific_filename
                        
            self.specific_driver_name =    "phantomjs.exe" if 'windows' in specific_system else\
                                        "phantomjs"

            self.phantomjs_path : str =  self.path + self.specific_driver_name if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.info_messages = bool(kwargs.get('info_messages'))

        self.extractor = Extractor
        self.github_viewer = GithubViewer
        self.requests_getter = RequestsGetter

    def __get_current_version_phantomjs(self) -> Tuple[bool, str, str]:
        """Gets current phantomjs version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current phantomjs version.

        Raises:

            OSError: Occurs when chromedriver made for another CPU type

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''
        driver_version_terminal : str = ''
        
        try:
            
            if os.path.exists(self.phantomjs_path):
        
                process = subprocess.Popen([self.phantomjs_path, '--version'], stdout=subprocess.PIPE)
        
                driver_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_terminal)
                driver_version = find_string[0] if len(find_string) > 0 else ''

                logging.info(f'Current version of phantomjs: {driver_version}')

            result_run = True

        except OSError:
            message_run = f'OSError error: {traceback.format_exc()}' #probably [Errno 86] Bad CPU type in executable:
            logging.error(message_run)
            return True, message_run, driver_version

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

            find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], json_data.get('ref'))
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

            if self.check_driver_is_up_to_date and not self.system_name:

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
            
            if self.check_driver_is_up_to_date and not self.system_name:

                result, message, is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_phantomjs()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if not is_driver_up_to_date:
                    message = f'Problem with updating phantomjs current_version: {current_version} latest_version: {latest_version}'
                    logging.error(message)
                    message = 'Trying to download previous latest version of phantomjs'
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

    def __get_latest_previous_version_phantomjs_via_requests(self) -> Tuple[bool, str, str]:
        """Gets previous latest phantomjs version


        Returns:
            Tuple of bool, str and str

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Empty string if function passed correctly, non-empty string if error.
            latest_version_previous (str)   : Latest previous version of phantomjs.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_previous_version : str = ''
        all_versions = []

        try:

            url = self.setting["PhantomJS"]["LinkAllReleases"]
            result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url, is_json=True)
            if not result:
                logging.error(message)
                return result, message, latest_previous_version

            values = json_data.get('values')
            for value in values:
                value_name = value.get('name')
                if not 'beta' in value_name:

                    find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], value_name)
                    version = find_string[0] if len(find_string) > 0 else ''

                    all_versions.append(version)

            all_versions = list(set(all_versions))
            all_versions.sort(key=lambda s: list(map(int, s.split('.'))))

            latest_previous_version = all_versions[len(all_versions)-2]

            logging.info(f'Latest previous version of phantomjs: {latest_previous_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, latest_previous_version

    def __check_if_version_is_valid(self, url : str) -> Tuple[bool, str]:
        """Checks the specified version for existence.

        Args:
            url (str)           : Full download url of chromedriver.

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
        """
        result_run : bool = False
        message_run : str = ''
        archive_name : str = url.split("/")[len(url.split("/"))-1]
        url_releases : str = self.setting["PhantomJS"]["LinkAllReleases"]
        is_found : bool = False

        try:

            while is_found == False:

                result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url_releases, is_json=True)
                if not result:
                    logging.error(message)
                    return result, message

                for data in json_data.get('values'):
                    if data.get('name') == archive_name:
                        is_found = True
                        break

                url_releases = json_data.get('next')
                if not url_releases:
                    break

            if not is_found:
                message = f'Wrong version or system_name was specified. archive_name: {archive_name} url: {url}'
                logging.error(message)
                return False, message

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)
        
        return result_run, message_run

    def __download_driver(self, version : str = '', previous_version : bool = False) -> Tuple[bool, str, str]:
        """Function to download, delete or upgrade current phantomjs

        Args:
            version (str)               : Specific phantomjs version to download. Defaults to empty string.
            previous_version (boll)     : If true, phantomjs latest previous version will be downloaded. Defaults to False.

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
        latest_version : str = ''
        latest_previous_version : str = ''

        try:

            if self.upgrade:

                result, message = self.__delete_current_phantomjs_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, file_name
            
            if version:

                logging.info(f'Started download phantomjs specific_version: {version}')

                url = self.setting["PhantomJS"]["LinkLastReleaseFile"].format(version)

            elif previous_version:

                result, message, latest_previous_version = self.__get_latest_previous_version_phantomjs_via_requests()
                if not result:
                    logging.error(message)
                    return result, message, file_name

                logging.info(f'Started download phantomjs latest_previous_version: {latest_previous_version}')

                url = self.setting["PhantomJS"]["LinkLastReleaseFile"].format(latest_previous_version)

            else:
                result, message, latest_version = self.__get_latest_version_phantomjs()
                if not result:
                    logging.error(message)
                    return result, message, file_name

                logging.info(f'Started download phantomjs latest_version: {latest_version}')

                url = self.setting["PhantomJS"]["LinkLastReleaseFile"].format(latest_version)

            if self.system_name:
                url = url.replace(url.split("/")[len(url.split("/"))-1], '')
                url = url + self.system_name.format(latest_version) if latest_version else url + self.system_name.format(latest_previous_version) if latest_previous_version else\
                url + self.system_name.format(version)

                logging.info(f'Started downloading geckodriver for specific system: {self.system_name}')

            if any([version, self.system_name ,latest_previous_version]):

                result, message = self.__check_if_version_is_valid(url=url)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            archive_name = url.split("/")[len(url.split("/"))-1]
            out_path = self.path + archive_name

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

            platform : str = self.setting["PhantomJS"]["LastReleasePlatform"] if not self.specific_driver_name else self.specific_driver_name 

            archive_path_folder = self.path + url.split('/')[len(url.split('/'))-1].replace('.zip', '').replace(".tar.bz2", '') + os.path.sep
            archive_path_folder_bin = archive_path_folder + 'bin' +  os.path.sep
            driver_archive_path = archive_path_folder_bin + platform

            if not self.filename:

                copyfile(driver_archive_path, self.path + platform)

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