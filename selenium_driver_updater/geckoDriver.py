from selenium import webdriver
import wget
import os
import traceback
import logging
import time
import os
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

from selenium.webdriver.firefox.options import Options as FirefoxOptions

from typing import Tuple

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from _setting import setting

import platform

import stat

from util.extractor import Extractor
from util.github_viewer import GithubViewer

import requests
from bs4 import BeautifulSoup
import re

import pathlib

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
        """
        self.setting = setting

        self.path : str = path
                    
        self.upgrade : bool = bool(kwargs.get('upgrade'))

        self.chmod : bool = bool(kwargs.get('chmod'))

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))

        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/35.0.1916.47 Safari/537.36'

        self.headers = {'User-Agent': user_agent}
        
        specific_filename = str(kwargs.get('filename'))
        self.filename = f"{specific_filename}.exe" if platform.system() == 'Windows' and specific_filename else\
                        specific_filename

        self.geckodriver_path : str =  self.path + self.setting['GeckoDriver']['LastReleasePlatform'] if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.extractor = Extractor

        self.github_viewer = GithubViewer

        self.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date'))

    def __get_current_version_geckodriver_selenium(self) -> Tuple[bool, str, str]:
        """Gets current geckodriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current driver version.

        Raises:
            SessionNotCreatedException: Occurs when current geckodriver could not start.
            
            WebDriverException: Occurs when current geckodriver could not start or critical error occured.

            OSError: Occurs when geckodriver made for another CPU type

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''
        try:
            
            if os.path.exists(self.geckodriver_path):

                options = FirefoxOptions()
                options.add_argument("--headless")

                driver = webdriver.Firefox(executable_path = self.geckodriver_path, options=options)
                driver_version = str(driver.capabilities['moz:geckodriverVersion'])
                driver.close()
                driver.quit()

                logging.info(f'Current version of geckodriver: {driver_version}')


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

            if os.path.exists(self.geckodriver_path):
                logging.info(f'Deleted existing geckodriver geckodriver_path: {self.geckodriver_path}')
                file_to_rem = pathlib.Path(self.geckodriver_path)
                file_to_rem.unlink()
            

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __get_latest_geckodriver_for_current_os(self) -> Tuple[bool, str, str]:
        """Download latest geckodriver to folder

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
        asset_name : str = ''
        url : str = ''
        geckodriver_version : str = ''

        try:
            
            repo_name = GeckoDriver._repo_name
            asset_name = self.setting['GeckoDriver']['LinkLastReleasePlatform']
            result, message, data = self.github_viewer.get_specific_asset_by_repo_name(repo_name=repo_name, asset_name=asset_name)
            if not result:
                return result, message, file_name

            geckodriver_version = data[0].get('version')
            url = data[0].get('asset').get('browser_download_url')
            asset_name = data[0].get('asset').get('name')
            
            logging.info(f'Started download geckodriver geckodriver_version: {geckodriver_version}')
            out_path = self.path + asset_name

            if os.path.exists(out_path):
                os.remove(out_path)

            logging.info(f'Started download geckodriver by url: {url}')

            file_name = wget.download(url=url, out=out_path)

            logging.info(f'Geckodriver was downloaded to path: {file_name}')

            time.sleep(2)

            if not self.filename:

                if asset_name.endswith('.tar.gz'):

                    archive_path = file_name
                    out_path = self.path
                    result, message = self.extractor.extract_all_tar_gz_archive(archive_path=archive_path, out_path=out_path)
                    if not result:
                        logging.error(message)
                        return result, message, file_name

                elif asset_name.endswith('.zip'):

                    archive_path = file_name
                    out_path = self.path
                    result, message = self.extractor.extract_all_zip_archive(archive_path=archive_path, out_path=out_path)
                    if not result:
                        logging.error(message)
                        return result, message, file_name

                else:
                    message = f'Unknown archive format was specified asset_name: {asset_name}'
                    logging.error(message)
                    return result_run, message, file_name

            else:

                archive_path = file_name
                out_path = self.path
                filename = self.setting['GeckoDriver']['LastReleasePlatform']
                filename_replace = self.filename
                result, message = self.extractor.extract_all_zip_archive_with_specific_name(archive_path=archive_path, 
                out_path=out_path, filename=filename, filename_replace=filename_replace)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            time.sleep(3)

            if os.path.exists(file_name):
                os.remove(file_name)

            file_name = self.geckodriver_path

            logging.info(f'Geckodriver was successfully unpacked by path: {file_name}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, file_name
    
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

            if self.check_driver_is_up_to_date:

                result, message, is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if is_driver_up_to_date:
                    return True, message, self.geckodriver_path

            if self.upgrade:

                result, message = self.__delete_current_geckodriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result, message, driver_path = self.__get_latest_geckodriver_for_current_os()
            if not result:
                logging.error(message)
                return result, message, driver_path

            if self.chmod:

                result, message = self.__chmod_driver()
                if not result:
                    return result, message, driver_path

            if self.check_driver_is_up_to_date:

                result, message, is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if not is_driver_up_to_date:
                    message = f'Problem with updating geckodriver current_version : {current_version} latest_version : {latest_version}'
                    logging.error(message)
                    return result_run, message, driver_path

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

            result, message, current_version = self.__get_current_version_geckodriver_selenium()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

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

            if os.path.exists(self.geckodriver_path):

                logging.info('Trying to give geckodriver needed permissions')

                st = os.stat(self.geckodriver_path)
                os.chmod(self.geckodriver_path, st.st_mode | stat.S_IEXEC)

                logging.info('Needed rights for geckodriver were successfully issued')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

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

            if self.check_browser_is_up_to_date:

                if os.path.exists(self.geckodriver_path):

                    result, message = self.__check_if_firefox_browser_is_up_to_date()
                    if not result:
                        logging.error(message)
                        return result, message, driver_path

            if not self.version:

                result, message, driver_path = self.__check_if_geckodriver_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            else:

                result, message, driver_path = self.__download_geckodriver_for_specific_version(version=self.version)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __download_geckodriver_for_specific_version(self, version : str) -> Tuple[bool, str, str]:
        """Downloads specific version of geckodriver

        Args:
            version (str)    : Specific version of geckodriver.

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

            if self.upgrade:

                result, message = self.__delete_current_geckodriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result, message, driver_path = self.__get_specific_version_geckodriver_for_current_os(version=version)
            if not result:
                logging.error(message)
                return result, message, driver_path

            if self.chmod:

                result, message = self.__chmod_driver()
                if not result:
                    return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __get_specific_version_geckodriver_for_current_os(self, version) -> Tuple[bool, str, str]:
        """Downloads specific version of geckodriver to specific path

        Args:
            version (str)    : Specific version of geckodriver.

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
        asset_name : str = ''

        try:

            repo_name = GeckoDriver._repo_name
            asset_name = self.setting['GeckoDriver']['LinkLastReleasePlatform']
            version = version
            result, message, data = self.github_viewer.get_specific_asset_by_specific_version_by_repo_name(repo_name=repo_name, 
            asset_name=asset_name, version=version)
            if not result:
                return result, message, file_name

            url = data[0].get('asset').get('browser_download_url')
            asset_name = data[0].get('asset').get('name')
            
            logging.info(f'Started download geckodriver specific_version: {version}')
            out_path = self.path + asset_name

            if os.path.exists(out_path):
                os.remove(out_path)

            logging.info(f'Started download geckodriver by url: {url}')

            file_name = wget.download(url=url, out=out_path)

            logging.info(f'Geckodriver was downloaded to path: {file_name}')

            time.sleep(2)

            if not self.filename:

                if asset_name.endswith('.tar.gz'):

                    archive_path = file_name
                    out_path = self.path
                    result, message = self.extractor.extract_all_tar_gz_archive(archive_path=archive_path, out_path=out_path)
                    if not result:
                        logging.error(message)
                        return result, message, file_name

                elif asset_name.endswith('.zip'):

                    archive_path = file_name
                    out_path = self.path
                    result, message = self.extractor.extract_all_zip_archive(archive_path=archive_path, out_path=out_path)
                    if not result:
                        logging.error(message)
                        return result, message, file_name

                else:
                    message = f'Unknown archive format was specified asset_name: {asset_name}'
                    logging.error(message)
                    return result_run, message, file_name

            else:

                archive_path = file_name
                out_path = self.path
                filename = self.setting['GeckoDriver']['LastReleasePlatform']
                filename_replace = self.filename
                result, message = self.extractor.extract_all_zip_archive_with_specific_name(archive_path=archive_path, 
                out_path=out_path, filename=filename, filename_replace=filename_replace)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            time.sleep(3)

            if os.path.exists(file_name):
                os.remove(file_name)

            file_name = self.geckodriver_path

            logging.info(f'Geckodriver was successfully unpacked by path: {file_name}')

            result_run = True
        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, file_name

    def __check_if_firefox_browser_is_up_to_date(self) -> Tuple[bool, str]:
        """Сhecks for the latest version of firefox browser

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        
        try:

            firefoxbrowser_updater_path = str(self.setting["FirefoxBrowser"]["FirefoxBrowserUpdaterPath"])
            if not firefoxbrowser_updater_path:
                message = f'Parameter "check_browser_is_up_to_date" has not been optimized for your OS yet. Please wait for the new releases.'
                logging.info(message)
                return True, message

            if not os.path.exists(firefoxbrowser_updater_path):
                message = f'firefoxbrowser_updater_path: {firefoxbrowser_updater_path} is not exists. Please report your OS information and path to {firefoxbrowser_updater_path} file in repository.'
                logging.info(message)
                return True, message

            result, message, is_browser_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_firefox_browser()
            if not result:
                logging.error(message)
                return result, message

            if not is_browser_up_to_date:

                result, message = self.__get_latest_firefox_browser_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message

                result, message, is_browser_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version_firefox_browser()
                if not result:
                    logging.error(message)
                    return result, message

                if not is_browser_up_to_date:
                    message = f'Problem with updating firefox browser current_version: {current_version} latest_version: {latest_version}'
                    logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __get_current_version_firefox_browser_selenium(self) -> Tuple[bool, str, str]:
        """Gets current firefox browser version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            browser_version (str)   : Current firefox browser version.

        Raises:
            SessionNotCreatedException: Occurs when current geckodriver could not start.

            WebDriverException: Occurs when current geckodriver could not start or critical error occured.

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        browser_version : str = ''
        
        try:
            
            if os.path.exists(self.geckodriver_path):

                options = FirefoxOptions()
                options.add_argument("--headless")

                driver = webdriver.Firefox(executable_path = self.geckodriver_path, options=options)
                browser_version = str(driver.capabilities['browserVersion'])
                driver.close()
                driver.quit()

                logging.info(f'Current version of firefox browser: {browser_version}')

            result_run = True

        except SessionNotCreatedException:
            message_run = f'SessionNotCreatedException error: {traceback.format_exc()}'
            logging.error(message_run)
            return True, message_run, browser_version

        except WebDriverException:
            message_run = f'WebDriverException error: {traceback.format_exc()}'
            logging.error(message_run)
            return True, message_run, browser_version

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)
        
        return result_run, message_run, browser_version

    def __get_latest_version_firefox_browser(self) -> Tuple[bool, str, str]:
        """Gets latest firefox browser version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            latest_version (str)    : Latest version of firefox browser.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_version : str = ''

        try:
            
            url = self.setting["FirefoxBrowser"]["LinkAllLatestReleases"]
            request = requests.get(url=url, headers=self.headers)
            request_text = request.text
            status_code = request.status_code

            if status_code != 200:
                message = f'status_code not equal 200 status_code: {status_code} request_text: {request.text}'
                return result_run, message, latest_version

            soup = BeautifulSoup(request_text, 'html.parser')
            element_releases_list = soup.findAll('ol', attrs={'class' : 'c-release-list'})[0]

            all_releases_elements = element_releases_list.findAll('a', attrs={'href' : re.compile('/releasenotes/')})
            all_releases = []

            [all_releases.append(release.text) for release in all_releases_elements]
            all_releases.sort(key=lambda s: list(map(int, s.split('.'))), reverse=True)

            latest_version = all_releases[0]
            
            logging.info(f'Latest version of firefox browser: {latest_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __get_latest_firefox_browser_for_current_os(self) -> Tuple[bool, str]:
        """Trying to update firefox browser to its latest version

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        
        try:

            message = f'Trying to update firefox browser to the latest version.'
            logging.info(message)

            os.system(self.setting["FirefoxBrowser"]["FirefoxBrowserUpdater"])
            time.sleep(60) #wait for the updating - too long
            
            message = f'Firefox browser was successfully updated to the latest version.'
            logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __compare_current_version_and_latest_version_firefox_browser(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of firefox browser to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Empty string if function passed correctly, non-empty string if error.
            is_browser_up_to_date (bool)    : If true current version of firefox browser is up to date. Defaults to False.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        is_browser_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''
        
        try:

            result, message, current_version = self.__get_current_version_firefox_browser_selenium()
            if not result:
                logging.error(message)
                return result, message, is_browser_up_to_date, current_version, latest_version

            result, message, latest_version = self.__get_latest_version_firefox_browser()
            if not result:
                logging.error(message)
                return result, message, is_browser_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_browser_up_to_date = True
                message = f"Your existing firefox browser is up to date. current_version: {current_version} latest_version: {latest_version}"
                logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_browser_up_to_date, current_version, latest_version