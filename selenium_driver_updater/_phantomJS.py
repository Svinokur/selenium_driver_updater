#pylint: disable=logging-fstring-interpolation
#Standart library imports
import shutil
import os
import time
from typing import Tuple
from pathlib import Path
import re
from shutil import copyfile
import wget

# Local imports
from selenium_driver_updater.util.logger import logger
from selenium_driver_updater.util.exceptions import DriverVersionInvalidException

from selenium_driver_updater.driver_base import DriverBase

class PhantomJS(DriverBase):
    "Class for working with Selenium phantomjs binary"

    _repo_name = 'ariya/phantomjs'
    _tmp_folder_path = 'tmp'

    def __init__(self, **kwargs):

        kwargs.update(repo_name=PhantomJS._repo_name)

        DriverBase.__init__(self, **kwargs)

        self.system_name = ''

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

        self.phantomjs_path = self.driver_path

    def _get_latest_version_phantomjs(self) -> str:
        """Gets latest phantomjs version


        Returns:
            str

            latest_version (str)    : Latest version of phantomjs.

        """

        latest_version : str = ''

        repo_name = PhantomJS._repo_name
        latest_version = self.github_viewer.get_latest_release_tag_by_repo_name(repo_name=repo_name)

        logger.info(f'Latest version of phantomjs: {latest_version}')

        return latest_version

    def _compare_current_version_and_latest_version_phantomjs(self) -> Tuple[bool, str, str]:
        """Compares current version of phantomjs to latest version

        Returns:
            Tuple of bool, str and str

            is_driver_up_to_date (bool) : It true the driver is up to date. Defaults to False.
            current_version (str)       : Current version of the driver.
            latest_version (str)        : Latest version of the driver.

        """
        is_driver_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''

        current_version = super()._get_current_version_driver()

        if not current_version:
            return is_driver_up_to_date, current_version, latest_version

        latest_version = self._get_latest_version_phantomjs()

        if current_version == latest_version:
            is_driver_up_to_date = True
            message = ('Your existing phantomjs is up to date.'
                    f'current_version: {current_version} latest_version: {latest_version}')
            logger.info(message)

        return is_driver_up_to_date, current_version, latest_version

    def _check_if_phantomjs_is_up_to_date(self) -> str:
        """Сhecks for the latest version, downloads or updates phantomjs binary

        Returns:
            str

            driver_path (str)       : Path where phantomjs was downloaded or updated.

        """
        driver_path : str = ''

        if self.check_driver_is_up_to_date and not self.system_name:

            is_driver_up_to_date, current_version, latest_version = self._compare_current_version_and_latest_version_phantomjs()

            if is_driver_up_to_date:
                return self.phantomjs_path

        driver_path = self._download_driver()

        if self.check_driver_is_up_to_date and not self.system_name:

            is_driver_up_to_date, current_version, latest_version = self._compare_current_version_and_latest_version_phantomjs()

            if not is_driver_up_to_date:
                message = ('Problem with updating phantomjs'
                            f'current_version: {current_version} latest_version: {latest_version}')
                logger.error(message)
                message = 'Trying to download previous latest version of phantomjs'
                logger.info(message)

                driver_path = self._download_driver(previous_version=True)

        return driver_path

    def __rename_driver(self, archive_folder_path : str, archive_driver_path : str) -> None:
        """Renames phantomjs if it was given

        Args:
            archive_folder_path (str)       : Path to the main folder
            archive_driver_path (str)       : Path to the phantomjs archive

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

        """
        driver_path : str = ''

        if not self.version:

            driver_path = self._check_if_phantomjs_is_up_to_date()

        else:

            driver_path = self._download_driver(version=self.version)

        return driver_path

    def _get_latest_previous_version_phantomjs_via_requests(self) -> str:
        """Gets previous latest phantomjs version

        Returns:
            str

            latest_version_previous (str)   : Latest previous version of phantomjs.

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

    def _check_if_version_is_valid(self, url : str) -> None:
        """Checks the specified version for existence.

        Args:
            url (str) : Full download url of chromedriver.

        """

        archive_name : str = url.split("/")[len(url.split("/"))-1]
        url_releases : str = self.setting["PhantomJS"]["LinkAllReleases"]
        is_found : bool = False

        while is_found is False:

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

    def _download_driver(self, version : str = '', previous_version : bool = False) -> str:
        """Function to download, delete or upgrade current phantomjs

        Args:
            version (str)               : Specific phantomjs version to download. Defaults to empty string.
            previous_version (boll)     : If true, phantomjs latest previous version will be downloaded. Defaults to False.

        Returns:
            str

            driver_path (str)       : Path to unzipped driver.

        """

        url : str = ''
        latest_version : str = ''
        latest_previous_version : str = ''

        driver_path : str = ''

        if self.upgrade:

            super()._delete_current_driver_for_current_os()

        if version:

            logger.info(f'Started download phantomjs specific_version: {version}')

            url = self.setting["PhantomJS"]["LinkLastReleaseFile"].format(version)

        elif previous_version:

            latest_previous_version = self._get_latest_previous_version_phantomjs_via_requests()

            logger.info(f'Started download phantomjs latest_previous_version: {latest_previous_version}')

            url = self.setting["PhantomJS"]["LinkLastReleaseFile"].format(latest_previous_version)

        else:
            latest_version = self._get_latest_version_phantomjs()

            logger.info(f'Started download phantomjs latest_version: {latest_version}')

            url = self.setting["PhantomJS"]["LinkLastReleaseFile"].format(latest_version)

        if self.system_name:
            url = url.replace(url.split("/")[-1], '')
            version = [value for key,value in locals().items() if 'version' in key and value][0]
            url = url + self.system_name.format(version)

            logger.info(f'Started downloading geckodriver for specific system: {self.system_name}')

        if any([version, self.system_name ,latest_previous_version]):

            self._check_if_version_is_valid(url=url)

        archive_name = url.split("/")[-1]
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

        archive_path_folder = self.path + url.split("/")[-1].replace('.zip', '').replace(".tar.bz2", '') + os.path.sep
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

            super()._chmod_driver()

        return driver_path
