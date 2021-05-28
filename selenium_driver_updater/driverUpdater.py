import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from _chromeDriver import ChromeDriver
from _geckoDriver import GeckoDriver
from _operaDriver import OperaDriver
from _edgeDriver import EdgeDriver
from _chromiumChromeDriver import ChromiumChromeDriver
from _phantomJS import PhantomJS
from _setting import setting

import logging
import os
import traceback
from typing import Tuple

import time

from util.requests_getter import RequestsGetter

class DriverUpdater():

    chromedriver = 'chromedriver'
    geckodriver = 'geckodriver'
    operadriver = 'operadriver'
    edgedriver = 'edgedriver'
    chromium_chromedriver = 'chromium-chromedriver'
    phantomjs = 'phantomjs'
        
    @staticmethod
    def install(driver_name, **kwargs):
        """Function for install or update Selenium driver binary

        Args:
            driver_name (Union[str, list[str]]) : Specified driver name/names which will be downloaded or updated. Like "DriverUpdater.chromedriver" or etc.
            path (str)                          : Specified path which will used for downloading or updating Selenium driver binary. Must be folder path.
            upgrade (bool)                      : If true, it will overwrite existing driver in the folder. Defaults to False.
            chmod (bool)                        : If true, it will make chromedriver binary executable. Defaults to True.
            check_driver_is_up_to_date (bool)   : If true, it will check driver version before and after upgrade. Defaults to False.
            info_messages (bool)                : If false, it will disable all info messages. Defaults to True.
            filename (str)                      : Specific name for chromedriver. If given, it will replace name for chromedriver. Defaults to empty string.
            version (str)                       : Specific version for chromedriver. If given, it will downloads given version. Defaults to empty string.
            check_browser_is_up_to_date (bool)  : If true, it will check browser version before specific driver update or upgrade. Defaults to False.
            enable_library_update_check (bool)  : If true, it will enable checking for library update while starting. Defaults to True.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where Selenium driver binary was downloaded or updated.

        Raises:
            Except: If unexpected error raised. 

        """

        #Initialize all variables
        result_run : bool = False
        message_run : str = ''
        driver_path = ''

        info_messages = bool(kwargs.get('info_messages', True))
        if info_messages:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.ERROR)

        path = kwargs.get('path', sys.path[0])
        logging.info('You have not specified the path - so used default folder path instead') if not kwargs.get('path') else ''
        path = str(os.path.abspath(path) + os.path.sep)

        filename : str = str(kwargs.get('filename', '')).replace('.', '') if type(kwargs.get('filename', '')) == str else\
                         kwargs.get('filename', '') if type(kwargs.get('filename', '')) == list else ''

        enable_library_update_check = bool(kwargs.get('enable_library_update_check', True))
        upgrade = bool(kwargs.get('upgrade', False))
        chmod = bool(kwargs.get('chmod', True))
        check_driver_is_up_to_date = bool(kwargs.get('check_driver_is_up_to_date', False))
        version = str(kwargs.get('version', ''))
        check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date', False))

        try:

            result, message = DriverUpdater.__check_enviroment_and_variables(path=path, driver_name=driver_name, enable_library_update_check=enable_library_update_check, filename=filename)
            if not result:
                logging.error(message)
                return result, message, driver_path

            if type(driver_name) == str:

                result, message, driver_path = DriverUpdater.__run_specific_driver(driver_name=driver_name, path=path, upgrade=upgrade, chmod=chmod, 
                                                check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                                filename=filename, version=version,
                                                check_browser_is_up_to_date=check_browser_is_up_to_date, info_messages=info_messages)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif type(driver_name) == list:

                list_of_paths : list[str] = []
                
                for driver in driver_name:

                    time.sleep(1) #small sleep

                    filename_driver = str(filename[driver_name.index(driver)]) if len(filename) > driver_name.index(driver) and filename else ''
                    filename_driver.replace('.', '')

                    result, message, driver_path = DriverUpdater.__run_specific_driver(driver_name=driver, path=path, upgrade=upgrade, chmod=chmod, 
                                                check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                                filename=filename_driver, version=version,
                                                check_browser_is_up_to_date=check_browser_is_up_to_date, info_messages=info_messages)
                    if not result:
                        logging.error(message)
                        return result, message, driver_path

                    list_of_paths.append(driver_path)

                driver_path = list_of_paths

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    @staticmethod
    def __check_all_input_parameteres(path, driver_name, filename) -> Tuple[bool, str]:
        """Private function for checking all input parameters

        Args:
            path (str)                          : Specified path which will used for downloading or updating Selenium driver binary. Must be folder path.
            driver_name (Union[str, list[str]]) : Specified driver name/names which will be downloaded or updated. Like "DriverUpdater.chromedriver" or etc.

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

            if not path:
                message = f"Please specify path to folder current path is: {path}"
                logging.error(message)
                return result_run, message

            if not os.path.exists(path):
                message = f"The specified path does not exist current path is: {path}"
                logging.error(message)
                return result_run, message

            if not os.path.isdir(path):
                message = f"The specified path is not a folder current path is: {path}"
                logging.error(message)
                return result_run, message

            if type(driver_name) == str:

                driver_name_check =     DriverUpdater.chromedriver if DriverUpdater.chromedriver == driver_name else \
                                        DriverUpdater.geckodriver  if DriverUpdater.geckodriver == driver_name else \
                                        DriverUpdater.operadriver if DriverUpdater.operadriver == driver_name else \
                                        DriverUpdater.edgedriver if DriverUpdater.edgedriver == driver_name else \
                                        DriverUpdater.chromium_chromedriver if DriverUpdater.chromium_chromedriver == driver_name else \
                                        DriverUpdater.phantomjs if DriverUpdater.phantomjs == driver_name else ''

                if not driver_name_check:
                    message = f'Unknown driver name was specified current driver_name is: {driver_name}'
                    logging.error(message)
                    return result_run, message

                if filename:

                    if type(filename) != str:
                        message = f'Unknown type of filename was specificed type(filename): {type(filename)}, but must be str, if one driver is given'
                        logging.error(message)
                        return result_run, message

            elif type(driver_name) == list:

                for driver in driver_name:

                    driver_name_list =      DriverUpdater.chromedriver if DriverUpdater.chromedriver == driver else \
                                            DriverUpdater.geckodriver  if DriverUpdater.geckodriver == driver else \
                                            DriverUpdater.operadriver if DriverUpdater.operadriver == driver else \
                                            DriverUpdater.edgedriver if DriverUpdater.edgedriver == driver else \
                                            DriverUpdater.chromium_chromedriver if DriverUpdater.chromium_chromedriver == driver else \
                                            DriverUpdater.phantomjs if DriverUpdater.phantomjs == driver else ''

                    if not driver_name_list:
                        message = f'Unknown driver name was specified at index: {driver_name.index(driver)} current name of driver is: {driver}'
                        logging.error(message)
                        return result_run, message

                if filename:

                    if type(filename) != list:
                        message = f'Unknown type of filename was specificed type(filename): {type(filename)}, but must be list[str], if multiply drivers were given'
                        logging.error(message)
                        return result_run, message

            else:

                message = f'Unknown type of driver name was specified, this library only supports str or list[str], current type is: {type(driver_name)}'
                logging.error(message)
                return result_run, message

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
    
    @staticmethod
    def __check_library_is_up_to_date() -> Tuple[bool, str]:
        """Private function for comparing latest version and current version of program

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
            
            url = setting["PyPi"]["urlProjectJson"]
            result, message, status_code, json_data = RequestsGetter.get_result_by_request(url=url, is_json=True)
            if not result:
                logging.error(message)
                return result, message

            current_version = setting["Program"]["version"].replace('b', '')
            latest_version = json_data.get('info').get('version')

            current_version_tuple = tuple(map(int, (current_version.split("."))))
            latest_version_tuple = tuple(map(int, (latest_version.split("."))))

            if latest_version_tuple > current_version_tuple:
                message = ('Your selenium-driver-updater library is out of date, please update it. '
                           f'current_version: {current_version} latest_version: {latest_version} ')
                logging.warning(message)

            elif latest_version_tuple == current_version_tuple:
                message = 'Your selenium-driver-updater library is up to date.'
                logging.info(message)
            
            else:
                message = 'Unable to compare the latest version and current version of the library, maybe you are using a beta version.'
                logging.error(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    @staticmethod
    def __check_is_python_version_compatible_for_library() -> Tuple[bool, str]:
        """Private function for checking if python version if compatible with python version 3+

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.

        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        major = str(sys.version_info[0])
        minor = str(sys.version_info[1])
        patch = str(sys.version_info[2])

        python_version = f"{major}.{minor}.{patch}"

        try:

            if major != "3":
                message = (f"selenium-driver-updater works only on Python 3, you are using {python_version} which is unsupported by this library, "
                           f"you may have some troubles or errors if you will proceed.")
                logging.warning(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    @staticmethod
    def __check_enviroment_and_variables(path : str, driver_name, enable_library_update_check : bool, filename) -> Tuple[bool, str]:
        """Private function for checking all input parameters and enviroment

        Args:
            path (str)                          : Specified path which will used for downloading or updating Selenium driver binary. Must be folder path.
            driver_name (Union[str, list[str]]) : Specified driver name/names which will be downloaded or updated. Like "DriverUpdater.chromedriver" or etc.
            enable_library_update_check (bool)  : If true, it will enable checking for library update while starting.

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

            result, message = DriverUpdater.__check_is_python_version_compatible_for_library()
            if not result:
                logging.error(message)
                return result, message

            if enable_library_update_check:

                result, message = DriverUpdater.__check_library_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message

            result, message = DriverUpdater.__check_all_input_parameteres(path=path, driver_name=driver_name, filename=filename)
            if not result:
                logging.error(message)
                return result, message

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
    
    @staticmethod
    def __run_specific_driver(driver_name, **kwargs) -> Tuple[bool, str, str]:
        """Private function for run download or update for specific driver

        Args:
            driver_name (Union[str, list[str]]) : Specified driver name/names which will be downloaded or updated. Like "DriverUpdater.chromedriver" or etc.
            path (str)                          : Specified path which will used for downloading or updating Selenium driver binary. Must be folder path.
            upgrade (bool)                      : If true, it will overwrite existing driver in the folder.
            chmod (bool)                        : If true, it will make chromedriver binary executable.
            check_driver_is_up_to_date (bool)   : If true, it will check driver version before and after upgrade.
            info_messages (bool)                : If false, it will disable all info messages.
            filename (str)                      : Specific name for chromedriver. If given, it will replace name for chromedriver.
            version (str)                       : Specific version for chromedriver. If given, it will downloads given version.
            check_browser_is_up_to_date (bool)  : If true, it will check browser version before specific driver update or upgrade.
            enable_library_update_check (bool)  : If true, it will enable checking for library update while starting.

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.

        Raises:
            Except: If unexpected error raised. 

        """
        

        result_run : bool = False
        message_run : str = ''

        path = kwargs.get('path')         
        upgrade = kwargs.get('upgrade')
        chmod = kwargs.get('chmod')
        check_driver_is_up_to_date = kwargs.get('check_driver_is_up_to_date')
        filename = kwargs.get('filename')
        version = kwargs.get('version')
        check_browser_is_up_to_date = kwargs.get('check_browser_is_up_to_date')
        info_messages = kwargs.get('info_messages')
        driver_path : str = ''

        try:

            if DriverUpdater.chromedriver == driver_name:

                chrome_driver = ChromeDriver(path=path, upgrade=upgrade, chmod=chmod, 
                                            check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                            filename=filename, version=version,
                                            check_browser_is_up_to_date=check_browser_is_up_to_date, info_messages=info_messages)
                result, message, driver_path = chrome_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.geckodriver == driver_name:

                gecko_driver = GeckoDriver(path=path, upgrade=upgrade, chmod=chmod, 
                                        check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                        filename=filename, version=version,
                                        check_browser_is_up_to_date=check_browser_is_up_to_date, info_messages=info_messages)
                result, message, driver_path = gecko_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.operadriver == driver_name:

                opera_driver = OperaDriver(path=path, upgrade=upgrade, chmod=chmod, 
                                        check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                        filename=filename, version=version,
                                        check_browser_is_up_to_date=check_browser_is_up_to_date, info_messages=info_messages)
                result, message, driver_path = opera_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.edgedriver == driver_name:

                edge_driver = EdgeDriver(path=path, upgrade=upgrade, chmod=chmod, 
                                    check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                    filename=filename, version=version,
                                    check_browser_is_up_to_date=check_browser_is_up_to_date, info_messages=info_messages)
                result, message, driver_path = edge_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.chromium_chromedriver == driver_name:

                chromium_chromedriver = ChromiumChromeDriver(check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                                            check_browser_is_up_to_date=check_browser_is_up_to_date, info_messages=info_messages)
                result, message, driver_path = chromium_chromedriver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.phantomjs == driver_name:

                phantomjs = PhantomJS(path=path, upgrade=upgrade, chmod=chmod, 
                                    check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                    filename=filename, version=version, info_messages=info_messages)
                result, message, driver_path = phantomjs.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path