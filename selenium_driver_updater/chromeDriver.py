import requests
import wget
import os
import traceback
import logging
import zipfile
import time
import stat
import os

import platform

from typing import Tuple

from .setting import setting

class ChromeDriver():
    
    def __init__(self, path : str, upgrade : bool, chmod : bool):
        """Class for working with Selenium chromedriver binary

        Args:
            path (str)      : Specified path which will used for downloading or updating Selenium chromedriver binary. Must be folder path.
            upgrade (bool)  : If true, it will overwrite existing driver in the folder. Defaults to False.
            chmod (bool)    : If true, it will make chromedriver binary executable. Defaults to True.
        """
        self.setting = setting

        self.path : str = path

        self.chromedriver_path : str =  path + "chromedriver.exe" if platform.system() == 'Windows' else\
                                        path + "chromedriver"
                    
        self.upgrade : bool = upgrade

        self.chmod : bool = chmod

    def __get_latest_version_chrome_driver(self) -> Tuple[bool, str, str]:
        """Gets latest chromedriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            latest_version (str)    : Latest version of chromedriver.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_version : str = ''

        try:
            
            request = requests.get(self.setting["ChromeDriver"]["LinkLastRelease"])
            latest_version = str(request.text)

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __delete_current_chromedriver_for_current_os(self) -> Tuple[bool, str]:
        """Deletes chromedriver from folder if parameter "upgrade" is True


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

            if os.path.exists(self.chromedriver_path):
                os.remove(self.chromedriver_path)
            

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run

    def __get_latest_chromedriver_for_current_os(self, latest_version : str) -> Tuple[bool, str, str]:
        """Downloads latest chromedriver to specific path

        Args:
            latest_version (str)    : Latest version of chromedriver.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            file_name (str)         : Path where chromedriver was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        file_name : str = ''
        try:

            url = self.setting["ChromeDriver"]["LinkLastReleaseFile"].format(latest_version)
            out_path = self.path + url.split('/')[4]

            if os.path.exists(out_path):
                os.remove(out_path)

            file_name = wget.download(url=url, out=out_path)

            time.sleep(2)

            with zipfile.ZipFile(file_name, 'r') as zip_ref:
                zip_ref.extractall(self.path)

            time.sleep(3)

            if os.path.exists(file_name):
                os.remove(file_name)

            
            file_name = self.chromedriver_path

            if self.chmod:

                st = os.stat(self.chromedriver_path)
                os.chmod(self.chromedriver_path, st.st_mode | stat.S_IEXEC)

            result_run = True

        except:

            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, file_name

    def check_if_chromedriver_is_up_to_date(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates chromedriver binary

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            file_name (str)         : Path where chromedriver was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        file_name : str = ''
        
        try:

            result, message, latest_version = self.__get_latest_version_chrome_driver()
            if not result:
                logging.error(message)
                return result, message, file_name

            if self.upgrade:

                result, message = self.__delete_current_chromedriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, file_name

            result, message, file_name = self.__get_latest_chromedriver_for_current_os(latest_version)
            if not result:
                logging.error(message)
                return result, message, file_name

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, file_name
    