#Standart library imports
import shutil
import subprocess
import os
import traceback
import logging
import time
from typing import Tuple, Any
import stat
from shutil import copyfile
from pathlib import Path
import re

# Third party imports
import wget
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

# Local imports
from _setting import setting

from util.extractor import Extractor
from util.github_viewer import GithubViewer

from util.requests_getter import RequestsGetter
from browsers._operaBrowser import OperaBrowser

class OperaDriver():
    """Class for working with Selenium operadriver binary"""

    _repo_name = 'operasoftware/operachromiumdriver'

    def __init__(self, **kwargs):

        self.setting : Any = setting

        self.path : str = str(kwargs.get('path'))

        self.upgrade : bool = bool(kwargs.get('upgrade'))

        self.chmod : bool = bool(kwargs.get('chmod'))

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))

        self.system_name = ''
        self.filename = ''

        #assign of specific os
        specific_system = str(kwargs.get('system_name', ''))
        specific_system = specific_system.replace('linux32', 'linux64')
        if specific_system:
            self.system_name = f"operadriver_{specific_system}.zip"

        self.setting['OperaDriver']['LastReleasePlatform'] = 'operadriver'

        #assign of filename
        specific_filename = str(kwargs.get('filename'))
        if specific_filename:
            self.filename = specific_filename + self.setting['Program']['DriversFileFormat']

        self.setting['OperaDriver']['LastReleasePlatform'] += self.setting['Program']['DriversFileFormat']

        self.operadriver_path : str =  self.path + self.setting['OperaDriver']['LastReleasePlatform'] if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.info_messages = bool(kwargs.get('info_messages'))

        self.extractor = Extractor
        self.github_viewer = GithubViewer
        self.requests_getter = RequestsGetter

        kwargs.update(path=self.operadriver_path)
        self.operabrowser = OperaBrowser(**kwargs)

    def main(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates operadriver binary or
        downloads specific version of operadriver.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
            driver_path (str)       : Path where operadriver was downloaded or updated.

        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''

        try:

            result, message = self.operabrowser.main()
            if not result:
                logging.error(message)
                return result, message, driver_path

            if not self.version:

                result, message, driver_path = self.__check_if_operadriver_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            else:

                result, message, driver_path = self.__download_driver(version=self.version)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __get_current_version_operadriver(self) -> Tuple[bool, str, str]:
        """Gets current operadriver version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
            driver_version (str)    : Current operadriver version.

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

            if Path(self.operadriver_path).exists():

                with subprocess.Popen([self.operadriver_path, '--version'], stdout=subprocess.PIPE) as process:
                    driver_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_terminal)
                driver_version = find_string[0] if len(find_string) > 0 else ''

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

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_version

    def __get_latest_version_operadriver(self) -> Tuple[bool, str, str]:
        """Gets latest operadriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
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

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __delete_current_operadriver_for_current_os(self) -> Tuple[bool, str]:
        """Deletes operadriver from specific folder


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.

        Raises:
            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''

        try:

            if Path(self.operadriver_path).exists():
                logging.info(f'Deleted existing operadriver operadriver_path: {self.operadriver_path}')
                Path(self.operadriver_path).unlink()


            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __check_if_operadriver_is_up_to_date(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates operadriver binary

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
            driver_path (str)       : Path where operadriver was downloaded or updated.

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
                    return True, message, self.operadriver_path

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
                    message = ('Problem with updating operadriver'
                                f'current_version: {current_version} latest_version: {latest_version}')
                    logging.error(message)
                    message = 'Trying to download previous latest version of operadriver'
                    logging.info(message)

                    result, message, driver_path = self.__download_driver(previous_version=True)
                    if not result:
                        logging.error(message)
                        return result, message, driver_path

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __compare_current_version_and_latest_version(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of operadriver to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Returns an error message if an error occurs in the function.
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

            result, message, current_version = self.__get_current_version_operadriver()
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
                message = ('Your existing operadriver is up to date.' 
                        f'current_version: {current_version} latest_version: {latest_version}')
                logging.info(message)

            result_run = True

        except Exception:
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
            message_run (str)           : Returns an error message if an error occurs in the function.

        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''
        renamed_driver_path : str = ''

        try:

            new_path = archive_folder_path + os.path.sep + self.filename

            if Path(new_path).exists():
                Path(new_path).unlink()

            os.rename(archive_operadriver_path, new_path)

            renamed_driver_path = self.path + self.filename
            if Path(renamed_driver_path).exists():
                Path(renamed_driver_path).unlink()

            copyfile(new_path, renamed_driver_path)

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __chmod_driver(self) -> Tuple[bool, str]:
        """Tries to give operadriver needed permissions

        Returns:
            Tuple of bool and str

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Returns an error message if an error occurs in the function.

        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''

        try:

            if Path(self.operadriver_path).exists():

                logging.info('Trying to give operadriver needed permissions')

                st = os.stat(self.operadriver_path)
                os.chmod(self.operadriver_path, st.st_mode | stat.S_IEXEC)

                logging.info('Needed rights for operadriver were successfully issued')

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __get_latest_previous_version_operadriver_via_requests(self) -> Tuple[bool, str, str]:
        """Gets previous latest operadriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Returns an error message if an error occurs in the function.
            latest_version_previous (str)   : Latest previous version of operadriver.

        Raises:
            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        latest_previous_version : str = ''

        try:

            repo_name = OperaDriver._repo_name
            result, message, json_data = self.github_viewer.get_all_releases_data_by_repo_name(repo_name=repo_name)
            if not result:
                return result, message, latest_previous_version

            latest_previous_version = json_data[1].get('name')

            logging.info(f'Latest previous version of operadriver: {latest_previous_version}')

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_previous_version

    def __check_if_version_is_valid(self, url : str, version_url : str) -> Tuple[bool, str]:
        """Checks the specified version for existence.

        Args:
            url (str)           : Full download url of operadriver.
            version_url (str)   : Version that will be downloaded.

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
        """
        result_run : bool = False
        message_run : str = ''
        archive_name : str = url.split("/")[len(url.split("/"))-1]
        is_found : bool = False

        try:

            result, message, json_data = self.github_viewer.get_all_releases_data_by_repo_name(OperaDriver._repo_name)
            if not result:
                logging.error(message)
                return result, message

            for data in json_data:
                if data.get('tag_name') == version_url or data.get('name') == version_url:
                    for asset in data.get('assets'):
                        if asset.get('name') == archive_name:
                            is_found = True
                            break

            if not is_found:
                message = f'Wrong version or system_name was specified. version_url: {version_url} url: {url}'
                logging.error(message)
                return False, message

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __download_driver(self, version : str = '', previous_version : bool = False) -> Tuple[bool, str, str]:
        """Function to download, delete or upgrade current operadriver

        Args:
            version (str)               : Specific operadriver version to download. Defaults to empty string.
            previous_version (boll)     : If true, operadriver latest previous version will be downloaded. Defaults to False.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
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

                result, message = self.__delete_current_operadriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            if version:

                url = self.setting["OperaDriver"]["LinkLastReleasePlatform"].format(version, version)

                logging.info(f'Started download operadriver specific_version: {version}')

            elif previous_version:

                result, message, latest_previous_version = self.__get_latest_previous_version_operadriver_via_requests()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                url = self.setting["OperaDriver"]["LinkLastReleasePlatform"].format(latest_previous_version, latest_previous_version)

                logging.info(f'Started download operadriver latest_previous_version: {latest_previous_version}')

            else:

                result, message, latest_version = self.__get_latest_version_operadriver()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                url = self.setting["OperaDriver"]["LinkLastReleasePlatform"].format(latest_version, latest_version)

                logging.info(f'Started download operadriver latest_version: {latest_version}')

            if self.system_name:
                url = url.replace(url.split("/")[len(url.split("/"))-1], '')
                url = url + self.system_name

                logging.info(f'Started downloading chromedriver for specific system: {self.system_name}')

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

            logging.info(f'Started download operadriver by url: {url}')

            if self.info_messages:
                archive_path = wget.download(url=url, out=out_path)
            else:
                archive_path = wget.download(url=url, out=out_path, bar=None)

            logging.info(f'Operadriver was downloaded to path: {archive_path}')

            time.sleep(2)

            out_path = self.path
            result, message = self.extractor.extract_and_detect_archive_format(archive_path=archive_path, out_path=out_path)
            if not result:
                logging.error(message)
                return result, message, driver_path

            platform : str = self.setting['OperaDriver']['LastReleasePlatform'] if not self.specific_driver_name else self.specific_driver_name

            archive_folder_path = self.path + Path(archive_path).stem + os.path.sep
            archive_operadriver_path = archive_folder_path + platform

            if not self.filename:
                
                copyfile(archive_operadriver_path, self.path + platform)

            else:

                result, message = self.__rename_driver(archive_folder_path=archive_folder_path,
                                                        archive_operadriver_path=archive_operadriver_path)
                if not result:
                    return result, message, driver_path

            if Path(archive_path).exists():
                Path(archive_path).unlink()

            if Path(archive_folder_path).exists():
                shutil.rmtree(archive_folder_path)

            driver_path = self.operadriver_path

            logging.info(f'Operadriver was successfully unpacked by path: {driver_path}')

            if self.chmod:

                result, message = self.__chmod_driver()
                if not result:
                    return result, message, driver_path

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path
        