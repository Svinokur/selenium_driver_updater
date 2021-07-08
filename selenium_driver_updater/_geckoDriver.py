#Standart library imports
import subprocess
import os
import traceback
import logging
import time
from typing import Tuple, Any
import re
from pathlib import Path
import stat

# Third party imports
import wget

# Local imports

from _setting import setting

from util.extractor import Extractor
from util.github_viewer import GithubViewer
from util.requests_getter import RequestsGetter

from browsers._firefoxBrowser import FirefoxBrowser

class GeckoDriver():
    """Class for working with Selenium geckodriver binary"""

    _repo_name = 'mozilla/geckodriver'

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
        specific_system = specific_system.replace('mac64_m1', 'macos-aarch64').replace('mac64', 'macos')
        if specific_system:
            if 'win' in specific_system:
                self.system_name = "geckodriver-v{}-" + f"{specific_system}.zip"
            else:
                self.system_name = "geckodriver-v{}-" + f"{specific_system}.tar.gz"

        self.setting['GeckoDriver']['LastReleasePlatform'] = 'geckodriver'

        #assign of filename
        specific_filename = str(kwargs.get('filename'))
        if specific_filename:
            self.filename = specific_filename + self.setting['Program']['DriversFileFormat']

        self.setting['GeckoDriver']['LastReleasePlatform'] += self.setting['Program']['DriversFileFormat']

        self.geckodriver_path : str =  self.path + self.setting['GeckoDriver']['LastReleasePlatform'] if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.info_messages = bool(kwargs.get('info_messages'))

        self.extractor = Extractor
        self.github_viewer = GithubViewer
        self.requests_getter = RequestsGetter

        kwargs.update(path=self.geckodriver_path)
        self.firefoxbrowser = FirefoxBrowser(**kwargs)

    def main(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates geckodriver binary or
        downloads specific version of geckodriver.

        Returns:
            Tuple of bool, str and str

            result_run (bool) : True if function passed correctly, False otherwise.
            message_run (str) : Returns an error message if an error occurs in the function.
            driver_path (str) : Path where geckodriver was downloaded or updated.

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

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __get_current_version_geckodriver(self) -> Tuple[bool, str, str]:
        """Gets current geckodriver version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
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

                with subprocess.Popen([self.geckodriver_path, '--version'], stdout=subprocess.PIPE) as process:
                    driver_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_terminal)
                driver_version = find_string[0] if len(find_string) > 0 else ''

                logging.info(f'Current version of geckodriver: {driver_version}')

            result_run = True

        except OSError:
            message_run = f'OSError error: {traceback.format_exc()}' #probably [Errno 86] Bad CPU type in executable:
            logging.error(message_run)
            return True, message_run, driver_version

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_version

    def __get_latest_version_geckodriver(self) -> Tuple[bool, str, str]:
        """Gets latest geckodriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
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

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __delete_current_geckodriver_for_current_os(self) -> Tuple[bool, str]:
        """Deletes geckodriver from folder


        Returns:
            Tuple of bool, str and str

            result_run (bool) : True if function passed correctly, False otherwise.
            message_run (str) : Returns an error message if an error occurs in the function.

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

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __check_if_geckodriver_is_up_to_date(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates geckodriver binary

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
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

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __compare_current_version_and_latest_version(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of geckodriver to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Returns an error message if an error occurs in the function.
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

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_driver_up_to_date, current_version, latest_version

    def __chmod_driver(self) -> Tuple[bool, str]:
        """Tries to give geckodriver needed permissions

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

            if Path(self.geckodriver_path).exists():

                logging.info('Trying to give geckodriver needed permissions')

                st = os.stat(self.geckodriver_path)
                os.chmod(self.geckodriver_path, st.st_mode | stat.S_IEXEC)

                logging.info('Needed rights for geckodriver were successfully issued')

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __get_latest_previous_version_geckodriver_via_requests(self) -> Tuple[bool, str, str]:
        """Gets previous latest geckodriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Returns an error message if an error occurs in the function.
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

        except Exception:
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
            message_run (str)       : Returns an error message if an error occurs in the function.
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

        except Exception:
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

            parameters = dict(archive_path=archive_path, out_path=out_path)

            if not self.filename:

                result, message = self.extractor.extract_and_detect_archive_format(**parameters)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            else:
                filename = self.setting['GeckoDriver']['LastReleasePlatform']
                parameters.update(dict(filename=filename, filename_replace=self.filename))
                result, message = self.extractor.extract_all_zip_archive_with_specific_name(**parameters)
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

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path
        