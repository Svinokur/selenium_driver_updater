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

from dataclasses import dataclass

@dataclass
class info():
    
    _driver_name = ''

    _path = ''
    _filename = ''
    _version = ''
    _system_name = ''

    _upgrade = False
    _chmod = True
    _check_driver_is_up_to_date = True
    _info_messages = False

    _check_browser_is_up_to_date = False
    _enable_library_update_check = True

class DriverUpdater():
    
    #DRIVERS
    chromedriver = 'chromedriver'
    geckodriver = 'geckodriver'
    operadriver = 'operadriver'
    edgedriver = 'edgedriver'
    chromium_chromedriver = 'chromium-chromedriver'
    phantomjs = 'phantomjs'

    #OS'S
    windows = 'windows'
    windows32 = 'windows32'
    windows64 = 'windows64'

    linux = 'linux'
    linux32 = 'linux32'
    linux64 = 'linux64'

    macos = 'macos'
    macos_m1 = 'macos_m1'
        
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
            system_name (Union[str, list[str]]) : Specific OS for driver. Defaults to empty string.

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

        info._driver_name = driver_name

        info._info_messages = bool(kwargs.get('info_messages', True))

        if info._info_messages:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.ERROR)

        path = kwargs.get('path', sys.path[0])
        logging.info('You have not specified the path - so used default folder path instead') if not kwargs.get('path') else ''
        info._path = str(os.path.abspath(path) + os.path.sep)

        info._filename = str(kwargs.get('filename', '')).replace('.', '') if type(kwargs.get('filename', '')) == str else\
                         kwargs.get('filename', '') if type(kwargs.get('filename', '')) == list else ''

        info._enable_library_update_check = bool(kwargs.get('enable_library_update_check', True))
        info._upgrade = bool(kwargs.get('upgrade', False))
        info._chmod = bool(kwargs.get('chmod', True))
        info._check_driver_is_up_to_date = bool(kwargs.get('check_driver_is_up_to_date', False))

        info._version = str(kwargs.get('version', '')) if type(kwargs.get('version', '')) == str else\
                        kwargs.get('version', '') if type(kwargs.get('version', '')) == list else ''

        info._check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date', False))
        
        info._system_name = str(kwargs.get('system_name', '')) if type(kwargs.get('system_name', '')) == str else\
                        kwargs.get('system_name', '') if type(kwargs.get('system_name', '')) == list else ''

        try:

            result, message = DriverUpdater.__check_enviroment_and_variables()
            if not result:
                logging.error(message)
                return result, message, driver_path

            if type(info._driver_name) == str:

                result, message, driver_path = DriverUpdater.__run_specific_driver()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif type(info._driver_name) == list:

                list_of_paths : list[str] = []
                
                for driver in info._driver_name:

                    time.sleep(1) #small sleep

                    filename_driver = str(info._filename[info._driver_name.index(driver)]) if len(info._filename) > info._driver_name.index(driver) and info._filename else ''
                    filename_driver = filename_driver.replace('.', '')

                    system_name_driver = str(info._system_name[info._driver_name.index(driver)]) if len(info._system_name) > info._driver_name.index(driver) and info._system_name else ''

                    version_driver = str(info._version[info._driver_name.index(driver)]) if len(info._version) > info._driver_name.index(driver) and info._version else ''

                    result, message, driver_path = DriverUpdater.__run_specific_driver(driver_name=driver, filename=filename_driver, system_name=system_name_driver, version=version_driver)
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
    def __check_all_input_parameteres() -> Tuple[bool, str]:
        """Private function for checking all input parameters

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

            if not info._path:
                message = f"Please specify path to folder current path is: {info._path}"
                logging.error(message)
                return result_run, message

            if not os.path.exists(info._path):
                message = f"The specified path does not exist current path is: {info._path}"
                logging.error(message)
                return result_run, message

            if not os.path.isdir(info._path):
                message = f"The specified path is not a folder current path is: {info._path}"
                logging.error(message)
                return result_run, message

            if type(info._driver_name) == str:

                result, message = DriverUpdater.__check_driver_name_is_valid(driver_name=info._driver_name)
                if not result:
                    logging.error(message)
                    return result, message

                if info._filename:

                    if type(info._filename) != str:
                        message = f'Unknown type of filename was specificed type(filename): {type(info._filename)}, but must be str, if one driver is given'
                        logging.error(message)
                        return result_run, message

                if info._system_name:

                    if type(info._system_name) != str:
                        message = f'Unknown type of system_name was specificed type(system_name): {type(info._system_name)}, but must be str, if one driver is given'
                        logging.error(message)
                        return result_run, message

                    result, message = DriverUpdater.__check_system_name_is_valid(system_name=info._system_name)
                    if not result:
                        logging.error(message)
                        return result, message

            elif type(info._driver_name) == list:

                for driver in info._driver_name:

                    result, message = DriverUpdater.__check_driver_name_is_valid(driver_name=driver)
                    if not result:
                        message = message + f' at index: {info._driver_name.index(driver)}'
                        logging.error(message)
                        return result, message

                if info._filename:

                    if type(info._filename) != list:
                        message = f'Unknown type of filename was specificed type(filename): {type(info._filename)}, but must be list[str], if multiply drivers were given'
                        logging.error(message)
                        return result_run, message

                if info._system_name:

                    if type(info._system_name) != list:
                        message = f'Unknown type of system_name was specificed type(system_name): {type(info._system_name)}, but must be list[str], if multiply drivers were given'
                        logging.error(message)
                        return result_run, message

                    for os_system in info._system_name:

                        result, message = DriverUpdater.__check_system_name_is_valid(system_name=os_system)
                        if not result:
                            message = message + f' at index: {info._system_name.index(os_system)}'
                            logging.error(message)
                            return result, message

            else:

                message = f'Unknown type of driver name was specified, this library only supports str or list[str], current type is: {type(info._driver_name)}'
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
        url : str = str(setting["PyPi"]["urlProjectJson"])

        try:
            
            result, message, status_code, json_data = RequestsGetter.get_result_by_request(url=url, is_json=True)
            if not result:
                logging.error(message)
                return result, message

            current_version = str(setting["Program"]["version"]).replace('b', '')
            latest_version = json_data.get('info').get('version')

            current_version_tuple = tuple(map(int, (current_version.split("."))))
            latest_version_tuple = tuple(map(int, (latest_version.split("."))))

            if latest_version_tuple > current_version_tuple:
                message = ('Your selenium-driver-updater library is out of date, please update it via "pip install selenium-driver-updater --upgrade" '
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
    def __check_enviroment_and_variables() -> Tuple[bool, str]:
        """Private function for checking all input parameters and enviroment

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

            if info._enable_library_update_check:

                result, message = DriverUpdater.__check_library_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message

            result, message = DriverUpdater.__check_all_input_parameteres()
            if not result:
                logging.error(message)
                return result, message

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
    
    @staticmethod
    def __run_specific_driver(driver_name = '', filename = '', version = '', system_name = '') -> Tuple[bool, str, str]:
        """Private function for run download or update for specific driver

        Args:
            driver_name (Union[str, list[str]]) : Specified driver name/names which will be downloaded or updated. Like "DriverUpdater.chromedriver" or etc.
            filename (str)                      : Specific name for chromedriver. If given, it will replace name for chromedriver. Defaults to empty string.
            version (str)                       : Specific version for chromedriver. If given, it will downloads given version. Defaults to empty string.
            system_name (Union[str, list[str]]) : Specific OS for driver. Defaults to empty string.

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.

        Raises:
            Except: If unexpected error raised. 

        """
        

        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''

        try:

            if not driver_name:
                driver_name = info._driver_name

            if not filename:
                filename = info._filename

            if not version:
                version = info._version

            if not system_name:
                system_name = info._system_name

            if DriverUpdater.chromedriver == driver_name:

                chrome_driver = ChromeDriver(path=info._path, upgrade=info._upgrade, chmod=info._chmod, 
                                            check_driver_is_up_to_date=info._check_driver_is_up_to_date, 
                                            filename=filename, version=version,
                                            check_browser_is_up_to_date=info._check_browser_is_up_to_date, info_messages=info._info_messages,
                                            system_name=system_name)
                result, message, driver_path = chrome_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.geckodriver == driver_name:

                gecko_driver = GeckoDriver(path=info._path, upgrade=info._upgrade, chmod=info._chmod, 
                                        check_driver_is_up_to_date=info._check_driver_is_up_to_date, 
                                        filename=filename, version=version,
                                        check_browser_is_up_to_date=info._check_browser_is_up_to_date, info_messages=info._info_messages,
                                        system_name=system_name)
                result, message, driver_path = gecko_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.operadriver == driver_name:

                opera_driver = OperaDriver(path=info._path, upgrade=info._upgrade, chmod=info._chmod, 
                                        check_driver_is_up_to_date=info._check_driver_is_up_to_date, 
                                        filename=filename, version=version,
                                        check_browser_is_up_to_date=info._check_browser_is_up_to_date, info_messages=info._info_messages,
                                        system_name=system_name)
                result, message, driver_path = opera_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.edgedriver == driver_name:

                edge_driver = EdgeDriver(path=info._path, upgrade=info._upgrade, chmod=info._chmod, 
                                    check_driver_is_up_to_date=info._check_driver_is_up_to_date, 
                                    filename=filename, version=version,
                                    check_browser_is_up_to_date=info._check_browser_is_up_to_date, info_messages=info._info_messages,
                                    system_name=system_name)
                result, message, driver_path = edge_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.chromium_chromedriver == driver_name:

                chromium_chromedriver = ChromiumChromeDriver(check_driver_is_up_to_date=info._check_driver_is_up_to_date, 
                                                            check_browser_is_up_to_date=info._check_browser_is_up_to_date, info_messages=info._info_messages)
                result, message, driver_path = chromium_chromedriver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.phantomjs == driver_name:

                phantomjs = PhantomJS(path=info._path, upgrade=info._upgrade, chmod=info._chmod, 
                                    check_driver_is_up_to_date=info._check_driver_is_up_to_date, 
                                    filename=filename, version=version, info_messages=info._info_messages,
                                    system_name=system_name)
                result, message, driver_path = phantomjs.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    @staticmethod
    def __check_driver_name_is_valid(driver_name):
        """Private function for checking if specified driver_name is exists and valid

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

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    @staticmethod
    def __check_system_name_is_valid(system_name):
        """Private function for checking if specified system_name is exists and valid

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

            system_name_check =  DriverUpdater.windows if DriverUpdater.windows == system_name else\
                                DriverUpdater.windows64 if DriverUpdater.windows64 == system_name else\
                                DriverUpdater.windows32 if DriverUpdater.windows32 == system_name else\
                                DriverUpdater.linux if DriverUpdater.linux == system_name else\
                                DriverUpdater.linux64 if DriverUpdater.linux64 == system_name else\
                                DriverUpdater.linux32 if DriverUpdater.linux32 == system_name else\
                                DriverUpdater.macos if DriverUpdater.macos == system_name else\
                                DriverUpdater.macos_m1 if DriverUpdater.macos_m1 == system_name else ''

            if not system_name_check:
                message = f'Unknown system name was specified current system_name is: {system_name}'
                logging.error(message)
                return result_run, message

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
