#Standart library imports
import shutil
import subprocess
import os
import traceback
import time
import stat
from typing import Tuple, Any
from pathlib import Path
import re
from shutil import copyfile
import wget

# Local imports
from selenium_driver_updater._setting import setting

from selenium_driver_updater.util.extractor import Extractor
from selenium_driver_updater.util.github_viewer import GithubViewer
from selenium_driver_updater.util.requests_getter import RequestsGetter
from selenium_driver_updater.util.logger import logger

from selenium_driver_updater.util.exceptions import DriverVersionInvalidException

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

    def __get_current_version_phantomjs(self) -> str:
        """Gets current phantomjs version via command in terminal

        Returns:
            str

            driver_version (str)    : Current phantomjs version.

        Raises:

            OSError: Occurs when chromedriver made for another CPU type

            Except: If unexpected error raised.

        """

        driver_version : str = ''
        driver_version_terminal : str = ''

        try:

            if Path(self.phantomjs_path).exists():

                with subprocess.Popen([self.phantomjs_path, '--version'], stdout=subprocess.PIPE) as process:
                    driver_version_terminal = process.communicate()[0].decode('UTF-8')

                find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_terminal)
                driver_version = find_string[0] if len(find_string) > 0 else ''

                logger.info(f'Current version of phantomjs: {driver_version}')

        except OSError:
            message_run = f'OSError error: {traceback.format_exc()}' #probably [Errno 86] Bad CPU type in executable:
            logger.error(message_run)
            return driver_version

        return driver_version

    def __get_latest_version_phantomjs(self) -> str:
        """Gets latest phantomjs version


        Returns:
            str

            latest_version (str)    : Latest version of phantomjs.

        Raises:
            Except: If unexpected error raised.

        """

        latest_version : str = ''

        repo_name = PhantomJS._repo_name
        json_data = self.github_viewer.get_latest_release_tag_by_repo_name(repo_name=repo_name)

        find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], json_data.get('ref'))
        latest_version = find_string[0] if len(find_string) > 0 else ''

        if not latest_version:
            message = 'Unable to determine latest version of PhantomJS, maybe the tags were deleted.'
            logger.error(message)

        logger.info(f'Latest version of phantomjs: {latest_version}')

        return latest_version

    def __compare_current_version_and_latest_version_phantomjs(self) -> Tuple[bool, str, str]:
        """Compares current version of phantomjs to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Empty string if function passed correctly, non-empty string if error.
            is_driver_up_to_date (bool) : If true current version of phantomjs is up to date. Defaults to False.

        Raises:
            Except: If unexpected error raised.

        """
        is_driver_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''

        current_version = self.__get_current_version_phantomjs()

        if not current_version:
            return is_driver_up_to_date, current_version, latest_version

        latest_version = self.__get_latest_version_phantomjs()

        if current_version == latest_version:
            is_driver_up_to_date = True
            message = f'Your existing phantomjs is up to date. current_version: {current_version} latest_version: {latest_version}' 
            logger.info(message)

        return is_driver_up_to_date, current_version, latest_version

    def __check_if_phantomjs_is_up_to_date(self) -> str:
        """Сhecks for the latest version, downloads or updates phantomjs binary

        Returns:
            str

            driver_path (str)       : Path where phantomjs was downloaded or updated.

        Raises:
            Except: If unexpected error raised.

        """
        driver_path : str = ''

        if self.check_driver_is_up_to_date and not self.system_name:

            is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_phantomjs()

            if is_driver_up_to_date:
                return self.phantomjs_path

        driver_path = self.__download_driver()

        if self.check_driver_is_up_to_date and not self.system_name:

            is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_phantomjs()

            if not is_driver_up_to_date:
                message = f'Problem with updating phantomjs current_version: {current_version} latest_version: {latest_version}'
                logger.error(message)
                message = 'Trying to download previous latest version of phantomjs'
                logger.info(message)

                driver_path = self.__download_driver(previous_version=True)

        return driver_path

    def __delete_current_phantomjs_for_current_os(self) -> None:
        """Deletes phantomjs from folder if parameter "upgrade" is True

        Raises:
            Except: If unexpected error raised.

        """

        if Path(self.phantomjs_path).exists():

            logger.info(f'Deleted existing phantomjs phantomjs_path: {self.phantomjs_path}')
            Path(self.phantomjs_path).unlink()

    def __chmod_driver(self) -> None:
        """Tries to give phantomjs binary needed permissions

        Raises:
            Except: If unexpected error raised.

        """

        if Path(self.phantomjs_path).exists():

            logger.info('Trying to give phantomjs needed permissions')

            st = os.stat(self.phantomjs_path)
            os.chmod(self.phantomjs_path, st.st_mode | stat.S_IEXEC)

            logger.info('Needed rights for phantomjs were successfully issued')

    def __rename_driver(self, archive_folder_path : str, archive_driver_path : str) -> None:
        """Renames phantomjs if it was given

        Args:
            archive_folder_path (str)       : Path to the main folder
            archive_driver_path (str)       : Path to the phantomjs archive

        Raises:
            Except: If unexpected error raised.

        """
        renamed_driver_path : str = ''

        new_path = archive_folder_path + os.path.sep + self.filename if not archive_folder_path.endswith(os.path.sep) else archive_folder_path + self.filename

        if Path(new_path).exists():
            Path(new_path).unlink()

        os.rename(archive_driver_path, new_path)

        renamed_driver_path = self.path + self.filename
        if Path(renamed_driver_path).exists():
            Path(renamed_driver_path).unlink()

        copyfile(new_path, renamed_driver_path)

    def main(self) -> str:
        """Main function, checks for the latest version, downloads or updates phantomjs binary or
        downloads specific version of phantomjs.

        Returns:
            str

            driver_path (str)       : Path where phantomjs was downloaded or updated.

        Raises:
            Except: If unexpected error raised.

        """
        driver_path : str = ''

        if not self.version:

            driver_path = self.__check_if_phantomjs_is_up_to_date()

        else:

            driver_path = self.__download_driver(version=self.version)

        return driver_path

    def __get_latest_previous_version_phantomjs_via_requests(self) -> str:
        """Gets previous latest phantomjs version

        Returns:
            str

            latest_version_previous (str)   : Latest previous version of phantomjs.

        Raises:
            Except: If unexpected error raised.

        """
        latest_previous_version : str = ''
        all_versions = []

        url = self.setting["PhantomJS"]["LinkAllReleases"]
        json_data = self.requests_getter.get_result_by_request(url=url, is_json=True)

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

        logger.info(f'Latest previous version of phantomjs: {latest_previous_version}')

        return latest_previous_version

    def __check_if_version_is_valid(self, url : str) -> None:
        """Checks the specified version for existence.

        Args:
            url (str) : Full download url of chromedriver.

        """

        archive_name : str = url.split("/")[len(url.split("/"))-1]
        url_releases : str = self.setting["PhantomJS"]["LinkAllReleases"]
        is_found : bool = False

        while is_found == False:

            json_data = self.requests_getter.get_result_by_request(url=url_releases, is_json=True)

            for data in json_data.get('values'):
                if data.get('name') == archive_name:
                    is_found = True
                    break

            url_releases = json_data.get('next')
            if not url_releases:
                break

        if not is_found:
            message = f'Wrong version or system_name was specified. archive_name: {archive_name} url: {url}'
            raise DriverVersionInvalidException(message)

    def __download_driver(self, version : str = '', previous_version : bool = False) -> str:
        """Function to download, delete or upgrade current phantomjs

        Args:
            version (str)               : Specific phantomjs version to download. Defaults to empty string.
            previous_version (boll)     : If true, phantomjs latest previous version will be downloaded. Defaults to False.

        Returns:
            str

            driver_path (str)       : Path to unzipped driver.

        Raises:
            Except: If unexpected error raised.

        """

        url : str = ''
        latest_version : str = ''
        latest_previous_version : str = ''

        driver_path : str = ''

        if self.upgrade:

            self.__delete_current_phantomjs_for_current_os()

        if version:

            logger.info(f'Started download phantomjs specific_version: {version}')

            url = self.setting["PhantomJS"]["LinkLastReleaseFile"].format(version)

        elif previous_version:

            latest_previous_version = self.__get_latest_previous_version_phantomjs_via_requests()

            logger.info(f'Started download phantomjs latest_previous_version: {latest_previous_version}')

            url = self.setting["PhantomJS"]["LinkLastReleaseFile"].format(latest_previous_version)

        else:
            latest_version = self.__get_latest_version_phantomjs()

            logger.info(f'Started download phantomjs latest_version: {latest_version}')

            url = self.setting["PhantomJS"]["LinkLastReleaseFile"].format(latest_version)

        if self.system_name:
            url = url.replace(url.split("/")[len(url.split("/"))-1], '')
            url = url + self.system_name.format(latest_version) if latest_version else url + self.system_name.format(latest_previous_version) if latest_previous_version else\
            url + self.system_name.format(version)

            logger.info(f'Started downloading geckodriver for specific system: {self.system_name}')

        if any([version, self.system_name ,latest_previous_version]):

            self.__check_if_version_is_valid(url=url)

        archive_name = url.split("/")[len(url.split("/"))-1]
        out_path = self.path + archive_name

        if Path(out_path).exists():
            Path(out_path).unlink()

        logger.info(f'Started download phantomjs by url: {url}')

        if self.info_messages:
            archive_path = wget.download(url=url, out=out_path)
        else:
            archive_path = wget.download(url=url, out=out_path, bar=None)
        time.sleep(2)

        logger.info(f'PhantomJS was downloaded to path: {archive_path}')

        out_path = self.path

        parameters = dict(archive_path=archive_path, out_path=out_path)

        self.extractor.extract_and_detect_archive_format(**parameters)

        platform : str = self.setting["PhantomJS"]["LastReleasePlatform"]

        archive_path_folder = self.path + url.split('/')[len(url.split('/'))-1].replace('.zip', '').replace(".tar.bz2", '') + os.path.sep
        archive_path_folder_bin = archive_path_folder + 'bin' +  os.path.sep
        driver_archive_path = archive_path_folder_bin + platform

        if not self.filename:

            copyfile(driver_archive_path, self.path + platform)

        else:

            parameters = dict(archive_folder_path=archive_path_folder_bin, archive_driver_path=driver_archive_path)
            self.__rename_driver(**parameters)

        if Path(archive_path_folder).exists():
            shutil.rmtree(archive_path_folder)
        
        driver_path = self.phantomjs_path

        logger.info(f'PhantomJS was successfully unpacked by path: {driver_path}')

        if self.chmod:

            self.__chmod_driver()

        return driver_path
