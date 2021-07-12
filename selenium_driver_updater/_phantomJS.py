#Standart library imports
import shutil
import subprocess
import os
import traceback
import logging
import time
import stat
from typing import Tuple, Any
from pathlib import Path
import re
from shutil import copyfile
import wget

# Local imports
from _setting import setting

from util.extractor import Extractor
from util.github_viewer import GithubViewer
from util.requests_getter import RequestsGetter

class PhantomJS():
    "Class for working with Selenium phantomjs binary"

    _repo_name = 'ariya/phantomjs'
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
        specific_system = str(kwargs.get('system_name', ''))
        specific_system = specific_system.replace('linux64', 'linux-x86_64')
        specific_system = specific_system.replace('linux32', 'linux-i686').replace('macos', 'macosx')

        if specific_system:
            self.system_name = "phantomjs-{}-" + f"{specific_system}"
            if 'win' in specific_system:
                self.system_name = "phantomjs-{}-windows"

            if 'linux' in specific_system:
                self.system_name = self.system_name + '.tar.bz2'
            else:
                self.system_name = self.system_name + '.zip'

        self.setting['PhantomJS']['LastReleasePlatform'] = 'phantomjs'

        #assign of filename
        specific_filename = str(kwargs.get('filename'))
        if specific_filename:
            self.filename = specific_filename + self.setting['Program']['DriversFileFormat']

        self.setting['PhantomJS']['LastReleasePlatform'] += self.setting['Program']['DriversFileFormat']

        self.phantomjs_path : str = self.path + self.setting['PhantomJS']['LastReleasePlatform'] if not specific_filename else self.path + self.filename

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

            if Path(self.phantomjs_path).exists():

                with subprocess.Popen([self.phantomjs_path, '--version'], stdout=subprocess.PIPE) as process:
                    driver_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_terminal)
                driver_version = find_string[0] if len(find_string) > 0 else ''

                logging.info(f'Current version of phantomjs: {driver_version}')

            result_run = True

        except OSError:
            message_run = f'OSError error: {traceback.format_exc()}' #probably [Errno 86] Bad CPU type in executable:
            logging.error(message_run)
            return True, message_run, driver_version

        except Exception:
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

        except Exception:
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

        except Exception:
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

        except Exception:
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

            if Path(self.phantomjs_path).exists():

                logging.info(f'Deleted existing phantomjs phantomjs_path: {self.phantomjs_path}')
                Path(self.phantomjs_path).unlink()

            result_run = True

        except Exception:
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

            if Path(self.phantomjs_path).exists():

                logging.info('Trying to give phantomjs needed permissions')

                st = os.stat(self.phantomjs_path)
                os.chmod(self.phantomjs_path, st.st_mode | stat.S_IEXEC)

                logging.info('Needed rights for phantomjs were successfully issued')

            result_run = True

        except Exception:
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

            if Path(new_path).exists():
                Path(new_path).unlink()

            os.rename(archive_driver_path, new_path)

            renamed_driver_path = self.path + self.filename
            if Path(renamed_driver_path).exists():
                Path(renamed_driver_path).unlink()

            copyfile(new_path, renamed_driver_path)

            result_run = True

        except Exception:
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

        except Exception:
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

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, latest_previous_version

    def __check_if_version_is_valid(self, url : str) -> Tuple[bool, str]:
        """Checks the specified version for existence.

        Args:
            url (str) : Full download url of chromedriver.

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

        except Exception:
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

                result, message = self.__delete_current_phantomjs_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            if version:

                logging.info(f'Started download phantomjs specific_version: {version}')

                url = self.setting["PhantomJS"]["LinkLastReleaseFile"].format(version)

            elif previous_version:

                result, message, latest_previous_version = self.__get_latest_previous_version_phantomjs_via_requests()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                logging.info(f'Started download phantomjs latest_previous_version: {latest_previous_version}')

                url = self.setting["PhantomJS"]["LinkLastReleaseFile"].format(latest_previous_version)

            else:
                result, message, latest_version = self.__get_latest_version_phantomjs()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

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
                    return result, message, driver_path

            archive_name = url.split("/")[len(url.split("/"))-1]
            out_path = self.path + archive_name

            if Path(out_path).exists():
                Path(out_path).unlink()

            logging.info(f'Started download phantomjs by url: {url}')

            if self.info_messages:
                archive_path = wget.download(url=url, out=out_path)
            else:
                archive_path = wget.download(url=url, out=out_path, bar=None)
            time.sleep(2)

            logging.info(f'PhantomJS was downloaded to path: {archive_path}')

            out_path = self.path

            parameters = dict(archive_path=archive_path, out_path=out_path)

            result, message = self.extractor.extract_and_detect_archive_format(**parameters)
            if not result:
                logging.error(message)
                return result, message, driver_path

            platform : str = self.setting["PhantomJS"]["LastReleasePlatform"]

            archive_path_folder = self.path + url.split('/')[len(url.split('/'))-1].replace('.zip', '').replace(".tar.bz2", '') + os.path.sep
            archive_path_folder_bin = archive_path_folder + 'bin' +  os.path.sep
            driver_archive_path = archive_path_folder_bin + platform

            if not self.filename:

                copyfile(driver_archive_path, self.path + platform)

            else:

                parameters = dict(archive_folder_path=archive_path_folder_bin, archive_driver_path=driver_archive_path)
                result, message = self.__rename_driver(**parameters)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            if Path(archive_path_folder).exists():
                shutil.rmtree(archive_path_folder)
            
            driver_path = self.phantomjs_path

            logging.info(f'PhantomJS was successfully unpacked by path: {driver_path}')

            if self.chmod:

                result, message = self.__chmod_driver()
                if not result:
                    return result, message, driver_path

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path
