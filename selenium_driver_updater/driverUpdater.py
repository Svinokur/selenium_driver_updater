#Standart library imports
from dataclasses import dataclass
from pathlib import Path
import logging
import os
import traceback
from typing import Tuple
import time

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Local imports
from _chromeDriver import ChromeDriver
from _geckoDriver import GeckoDriver
from _operaDriver import OperaDriver
from _edgeDriver import EdgeDriver
from _chromiumChromeDriver import ChromiumChromeDriver
from _phantomJS import PhantomJS
from _setting import setting

from util.requests_getter import RequestsGetter

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

#pylint: disable=protected-access
class DriverUpdater():

    #DRIVERS
    chromedriver = 'chromedriver'
    geckodriver = 'geckodriver'
    operadriver = 'operadriver'
    edgedriver = 'edgedriver'
    chromium_chromedriver = 'chromium_chromedriver'
    phantomjs = 'phantomjs'

    #OS'S
    windows = 'win64'
    windows32 = 'win32'
    windows64 = 'win64'

    linux = 'linux64'
    linux32 = 'linux32'
    linux64 = 'linux64'

    macos = 'mac64'
    macos_m1 = 'mac64_m1'

    arm = 'arm64'

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

        path = kwargs.get('path')
        if not path:
            path = sys.path[0]
            logging.info('You have not specified the path - so used default folder path instead')

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

            if isinstance(info._driver_name, str):

                result, message, driver_path = DriverUpdater.__run_specific_driver()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif isinstance(info._driver_name, list):

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

        except Exception:
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

            if not Path(info._path).exists():
                message = f"The specified path does not exist current path is: {info._path}"
                logging.error(message)
                return result_run, message

            if not Path(info._path).is_dir():
                message = f"The specified path is not a folder current path is: {info._path}"
                logging.error(message)
                return result_run, message

            if isinstance(info._driver_name,(list, str)):

                if info._filename:

                    result, message = DriverUpdater.__check_parameter_type_is_valid(info._filename, type(info._driver_name), 'filename')
                    if not result:
                        logging.error(message)
                        return result, message

                if info._system_name:

                    result, message = DriverUpdater.__check_parameter_type_is_valid(info._system_name, type(info._driver_name), 'system_name')
                    if not result:
                        logging.error(message)
                        return result, message


                if isinstance(info._driver_name, str):

                    result, message = DriverUpdater.__check_driver_name_is_valid(driver_name=info._driver_name)
                    if not result:
                        logging.error(message)
                        return result, message

                    if info._system_name:

                        result, message = DriverUpdater.__check_system_name_is_valid(system_name=info._system_name)
                        if not result:
                            logging.error(message)
                            return result, message

                elif isinstance(info._driver_name, list):

                    for driver in info._driver_name:

                        result, message = DriverUpdater.__check_driver_name_is_valid(driver_name=driver)
                        if not result:
                            message = message + f' at index: {info._driver_name.index(driver)}'
                            logging.error(message)
                            return result, message

                    if info._system_name:

                        for os_system in info._system_name:

                            result, message = DriverUpdater.__check_system_name_is_valid(system_name=os_system)
                            if not result:
                                message = message + f' at index: {info._system_name.index(os_system)}'
                                logging.error(message)
                                return result, message

            else:

                message = f'The type of "driver_name" must be a list or str current type is: {type(info._driver_name)}'
                logging.error(message)
                return result_run, message

            result_run = True

        except Exception:
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

        except Exception:
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

        except Exception:
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

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    @staticmethod
    def __run_specific_driver(**kwargs) -> Tuple[bool, str, str]:
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

            driver_name = kwargs.get('driver_name', info._driver_name)
            filename = kwargs.get('filename', info._filename)
            version = kwargs.get('version', info._version)
            system_name = kwargs.get('system_name', info._system_name)

            parametres = dict(  path=info._path, upgrade=info._upgrade, chmod=info._chmod,
                                check_driver_is_up_to_date=info._check_driver_is_up_to_date,
                                filename=filename, version=version,
                                check_browser_is_up_to_date=info._check_browser_is_up_to_date,
                                info_messages=info._info_messages,
                                system_name=system_name )

            if system_name:
                setting['Program']['DriversFileFormat'] = '.exe' if 'win' in system_name or 'arm' in system_name else ''

            if DriverUpdater.chromedriver == driver_name:

                chrome_driver = ChromeDriver(**parametres)
                result, message, driver_path = chrome_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.geckodriver == driver_name:

                gecko_driver = GeckoDriver(**parametres)
                result, message, driver_path = gecko_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.operadriver == driver_name:

                opera_driver = OperaDriver(**parametres)
                result, message, driver_path = opera_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.edgedriver == driver_name:

                edge_driver = EdgeDriver(**parametres)
                result, message, driver_path = edge_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.chromium_chromedriver == driver_name:

                chromium_chromedriver = ChromiumChromeDriver(**parametres)
                result, message, driver_path = chromium_chromedriver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.phantomjs == driver_name:

                phantomjs = PhantomJS(**parametres)
                result, message, driver_path = phantomjs.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result_run = True

        except Exception:
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

            driver_name_check = driver_name in list(vars(DriverUpdater))

            if not driver_name_check:
                message = f'Unknown driver name was specified current driver_name is: {driver_name}'
                logging.error(message)
                return result_run, message

            result_run = True

        except Exception:
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

            system_name_check = system_name in [DriverUpdater.__dict__[item] for item in DriverUpdater.__dict__]

            if not system_name_check:
                message = f'Unknown system name was specified current system_name is: {system_name}'
                logging.error(message)
                return result_run, message

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    @staticmethod
    def __check_parameter_type_is_valid(parameter, needed_type, parameter_name):
        result_run : bool = False
        message_run : str = ''

        try:

            if not isinstance(parameter, needed_type):
                message = f'The type of {parameter_name} must be a {needed_type} current type is: {type(parameter)}'
                logging.error(message)
                return result_run, message

            result_run = True

        except Exception:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
