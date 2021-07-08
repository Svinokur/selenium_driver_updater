#Standart library imports
import shutil
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
from util.requests_getter import RequestsGetter

from browsers._edgeBrowser import EdgeBrowser

class EdgeDriver():
    """Class for working with Selenium edgedriver binary"""

    _tmp_folder_path = 'tmp'

    def __init__(self, **kwargs):

        self.setting : Any = setting

        self.path : str = str(kwargs.get('path'))

        self.upgrade : bool = bool(kwargs.get('upgrade'))

        self.chmod : bool = bool(kwargs.get('chmod'))

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))

        self.system_name = ''
        self.filename = ''

        #assign of specific os
        specific_filename = str(kwargs.get('filename'))
        specific_system = str(kwargs.get('system_name', ''))
        if specific_system:
            self.system_name = f"edgedriver_{specific_system}.zip"

        self.setting['EdgeDriver']['LastReleasePlatform'] = 'msedgedriver'

        #assign of filename
        specific_filename = str(kwargs.get('filename'))
        if specific_filename:
            self.filename = specific_filename + self.setting['Program']['DriversFileFormat']

        self.setting['EdgeDriver']['LastReleasePlatform'] += self.setting['Program']['DriversFileFormat']

        self.edgedriver_path : str =  self.path + self.setting['EdgeDriver']['LastReleasePlatform'] if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.info_messages = bool(kwargs.get('info_messages'))

        self.extractor = Extractor
        self.requests_getter = RequestsGetter

        kwargs.update(path=self.edgedriver_path)
        self.edgebrowser = EdgeBrowser(**kwargs)

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

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __get_current_version_edgedriver(self) -> Tuple[bool, str, str]:
        """Gets current edgedriver version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
            driver_version (str)    : Current edgedriver version.

        Raises:

            OSError: Occurs when chromedriver made for another CPU type

            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''
        driver_version_terminal : str = ''

        try:

            if Path(self.edgedriver_path).exists():

                with subprocess.Popen([self.edgedriver_path, '--version'], stdout=subprocess.PIPE) as process:
                    driver_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string = re.findall(str(self.setting["Program"]["wedriverVersionPattern"]), str(driver_version_terminal))
                driver_version = find_string[0] if len(find_string) > 0 else ''

                logging.info(f'Current version of edgedriver: {driver_version}')

            result_run = True

        except OSError:
            message_run = f'OSError error: {traceback.format_exc()}' #probably [Errno 86] Bad CPU type in executable:
            logging.error(message_run)
            return True, message_run, driver_version

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_version

    def __get_latest_version_edgedriver(self) -> Tuple[bool, str, str]:
        """Gets latest edgedriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
            latest_version (str)    : Latest version of edgedriver

        Raises:
            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        latest_version : str = ''
        url = str(self.setting['EdgeDriver']['LinkLastRelease'])

        try:

            result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
            if not result:
                logging.error(message)
                return result, message, latest_version

            latest_version = re.findall(str(self.setting["Program"]["wedriverVersionPattern"]), json_data)[0]

            logging.info(f'Latest version of edgedriver: {latest_version}')

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __delete_current_edgedriver_for_current_os(self) -> Tuple[bool, str]:
        """Deletes edgedriver from folder


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

            if Path(self.edgedriver_path).exists():

                logging.info(f'Deleted existing edgedriver edgedriver_path: {self.edgedriver_path}')
                Path(self.edgedriver_path).unlink()


            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __check_if_edgedriver_is_up_to_date(self) -> Tuple[bool, str, str]:
        """Checks for the latest version, downloads or updates edgedriver binary

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Returns an error message if an error occurs in the function.
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
                    message = ('Problem with updating edgedriver'
                                f'current_version: {current_version} latest_version: {latest_version}')
                    logging.error(message)

                    message = 'Trying to download previous latest version of edgedriver'
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
        """Compares current version of edgedriver to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Returns an error message if an error occurs in the function.
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

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_driver_up_to_date, current_version, latest_version

    def __chmod_driver(self) -> Tuple[bool, str]:
        """Tries to give edgedriver needed permissions

        Returns:
            Tuple of bool and str

            result_run (bool)   : True if function passed correctly, False otherwise.
            message_run (str)   : Returns an error message if an error occurs in the function.

        Raises:
            Except: If unexpected error raised.

        """
        result_run : bool = False
        message_run : str = ''

        try:

            if Path(self.edgedriver_path).exists():

                logging.info('Trying to give edgedriver needed permissions')

                st = os.stat(self.edgedriver_path)
                os.chmod(self.edgedriver_path, st.st_mode | stat.S_IEXEC)

                logging.info('Needed rights for edgedriver were successfully issued')

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __get_latest_previous_version_edgedriver_via_requests(self) -> Tuple[bool, str, str]:
        """Gets previous latest edgedriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Returns an error message if an error occurs in the function.
            latest_version_previous (str)   : Latest previous version of edgedriver.

        Raises:
            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        latest_previous_version : str = ''

        try:

            result, message, latest_version = self.__get_latest_version_edgedriver()
            if not result:
                logging.error(message)
                return result, message, latest_previous_version

            latest_version_main = int(latest_version.split('.')[0])
            latest_previous_version_main = str(latest_version_main-1)

            url = self.setting["EdgeDriver"]["LinkLatestReleaseSpecificVersion"].format(latest_previous_version_main)

            result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
            if not result:
                logging.error(message)
                return result, message, latest_version

            latest_previous_version = str(json_data.strip())

            logging.info(f'Latest previous version of edgedriver: {latest_previous_version}')

            result_run = True

        except Exception:
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
            message_run (str)       : Returns an error message if an error occurs in the function.
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
                message = ('Wrong version or system_name was specified.'
                f'version_valid: {version_valid} version_url: {version_url} url: {url}')
                logging.error(message)
                return False, message

            result_run = True

        except Exception:
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
            message_run (str)       : Returns an error message if an error occurs in the function.
            file_name (str)         : Path to unzipped driver.

        Raises:
            Except: If unexpected error raised.

        """

        result_run : bool = False
        message_run : str = ''
        url : str = ''
        driver_notes_path : str = self.path + 'Driver_Notes'
        latest_previous_version : str = ''
        latest_version : str = ''

        driver_path : str = ''

        try:

            if self.upgrade:

                result, message = self.__delete_current_edgedriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            if version:

                url = str(self.setting["EdgeDriver"]["LinkLastReleaseFile"]).format(version)
                logging.info(f'Started download edgedriver specific_version: {version}')

            elif previous_version:

                result, message, latest_previous_version = self.__get_latest_previous_version_edgedriver_via_requests()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                logging.info(f'Started download edgedriver latest_previous_version: {latest_previous_version}')
                url = str(self.setting["EdgeDriver"]["LinkLastReleaseFile"]).format(latest_previous_version)

            else:

                result, message, latest_version = self.__get_latest_version_edgedriver()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                logging.info(f'Started download edgedriver latest_version: {latest_version}')
                url = str(self.setting["EdgeDriver"]["LinkLastReleaseFile"]).format(latest_version)

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

            logging.info(f'Started download edgedriver by url: {url}')

            if Path(out_path).exists():
                Path(out_path).unlink()

            if self.info_messages:
                archive_path = wget.download(url=url, out=out_path)
            else:
                archive_path = wget.download(url=url, out=out_path, bar=None)
            time.sleep(2)

            logging.info(f'Edgedriver was downloaded to path: {archive_path}')

            out_path = self.path

            parameters = dict(archive_path=archive_path, out_path=out_path)

            if not self.filename:

                result, message = self.extractor.extract_and_detect_archive_format(**parameters)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            else:


                filename = str(self.setting['EdgeDriver']['LastReleasePlatform'])
                parameters.update(dict(filename=filename, filename_replace=self.filename))

                result, message = self.extractor.extract_all_zip_archive_with_specific_name(**parameters)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            if Path(archive_path).exists():
                Path(archive_path).unlink()

            if Path(driver_notes_path).exists():
                shutil.rmtree(driver_notes_path)

            driver_path = self.edgedriver_path

            logging.info(f'Edgedriver was successfully unpacked by path: {driver_path}')

            if self.chmod:

                result, message = self.__chmod_driver()
                if not result:
                    return result, message, driver_path

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path
        