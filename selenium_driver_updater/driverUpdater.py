#Standart library imports
from dataclasses import dataclass, asdict
from pathlib import Path
import os
import traceback
from typing import Tuple, Any
import time
import sys

# Local imports
from selenium_driver_updater._chromeDriver import ChromeDriver
from selenium_driver_updater._geckoDriver import GeckoDriver
from selenium_driver_updater._operaDriver import OperaDriver
from selenium_driver_updater._edgeDriver import EdgeDriver
from selenium_driver_updater._chromiumChromeDriver import ChromiumChromeDriver
from selenium_driver_updater._phantomJS import PhantomJS

_all_drivers: Any= {
    "chromedriver" : ChromeDriver,
    "geckodriver" : GeckoDriver,
    "operadriver" : OperaDriver,
    "edgedriver" : EdgeDriver,
    "chromium_chromedriver" : ChromiumChromeDriver,
    "phantomjs" : PhantomJS,
}

from selenium_driver_updater._setting import setting

from selenium_driver_updater.util.requests_getter import RequestsGetter

from selenium_driver_updater.util.logger import logger
from selenium_driver_updater.util.logger import levels

@dataclass
class _info():

    driver_name : Any = ''

    path = ''
    filename = ''
    version = ''
    system_name = ''

    upgrade = False
    chmod = True
    check_driver_is_up_to_date = True
    info_messages = False

    check_browser_is_up_to_date = False
    enable_library_update_check = True

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

            old_return (bool) : If false, it will not return old variables like "result and message". Defaults to True.

        Returns:
            str

            driver_path (str)       : Path where Selenium driver binary was downloaded or updated.

        Raises:
            Except: If unexpected error raised.

        """

        #Initialize all variables
        driver_path = ''

        old_return = kwargs.get('old_return', True)

        _info.driver_name = driver_name

        _info.info_messages = bool(kwargs.get('info_messages', True))

        if _info.info_messages:
            logger.setLevel(levels['info'])
        else:
            logger.setLevel(levels['error'])

        path = kwargs.get('path')
        if not path:
            path = sys.path[0]
            logger.info('You have not specified the path - so used default folder path instead')

        _info.path = str(os.path.abspath(path) + os.path.sep)

        _info.filename = str(kwargs.get('filename', '')).replace('.', '') if type(kwargs.get('filename', '')) not in [list, dict, tuple] else kwargs.get('filename', '')

        _info.enable_library_update_check = bool(kwargs.get('enable_library_update_check', True))
        _info.upgrade = bool(kwargs.get('upgrade', False))
        _info.chmod = bool(kwargs.get('chmod', True))
        _info.check_driver_is_up_to_date = bool(kwargs.get('check_driver_is_up_to_date', False))

        _info.version = str(kwargs.get('version', '')) if type(kwargs.get('version', '')) not in [list, dict, tuple] else kwargs.get('version', '')

        _info.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date', False))

        _info.system_name = kwargs.get('system_name', '')

        DriverUpdater.__check_enviroment_and_variables()

        if isinstance(_info.driver_name, str):

            driver_path = DriverUpdater.__run_specific_driver()

        elif isinstance(_info.driver_name, list):

            list_of_paths : list[str] = []

            for driver in _info.driver_name:

                time.sleep(1) #small sleep

                try:
                    filename_driver = str(_info.filename[_info.driver_name.index(driver)])
                    filename_driver = filename_driver.replace('.', '')
                except IndexError:
                    filename_driver = ''

                try:
                    system_name_driver = str(_info.system_name[_info.driver_name.index(driver)])
                except IndexError:
                    system_name_driver = ''

                try:
                    version_driver = str(_info.version[_info.driver_name.index(driver)])
                except IndexError:
                    version_driver = ''

                driver_path = DriverUpdater.__run_specific_driver(driver_name=driver, filename=filename_driver, system_name=system_name_driver, version=version_driver)
                list_of_paths.append(driver_path)

                driver_path = list_of_paths

        if old_return:
            return True, '', driver_path
        else:
            return driver_path

    @staticmethod
    def __check_all_input_parameteres() -> None:
        """Private function for checking all input parameters

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.

        Raises:
            Except: If unexpected error raised.
        """


        if not Path(_info.path).exists():
            message = f"The specified path does not exist current path is: {_info.path}"
            raise ValueError(message)

        if not Path(_info.path).is_dir():
            message = f"The specified path is not a folder current path is: {_info.path}"
            raise ValueError(message)

        if isinstance(_info.driver_name,(list, str)):

            if _info.filename:

                DriverUpdater.__check_parameter_type_is_valid(_info.filename, type(_info.driver_name), 'filename')

            if _info.system_name:

                DriverUpdater.__check_parameter_type_is_valid(_info.system_name, type(_info.driver_name), 'system_name')

            if _info.version:
                pass
                #DriverUpdater.__check_parameter_type_is_valid(_info.version, type(_info.driver_name), 'version')

            if isinstance(_info.driver_name, str):

                DriverUpdater.__check_driver_name_is_valid(driver_name=_info.driver_name)

                if _info.system_name:

                    DriverUpdater.__check_system_name_is_valid(system_name=_info.system_name)

            elif isinstance(_info.driver_name, list):
                for driver in _info.driver_name:

                    DriverUpdater.__check_driver_name_is_valid(driver_name=driver)
                    # if not result:
                    #     message = message + f' at index: {_info.driver_name.index(driver)}'
                    #     logger.error(message)
                    #     return result, message

                if _info.system_name:

                    for os_system in _info.system_name:

                        DriverUpdater.__check_system_name_is_valid(system_name=os_system)
                        # if not result:
                        #     message = message + f' at index: {_info.system_name.index(os_system)}'
                        #     logger.error(message)
                        #     return result, message

        else:

            message = f'The type of "driver_name" must be a list or str current type is: {type(_info.driver_name)}'
            raise ValueError(message)


    @staticmethod
    def __check_library_is_up_to_date() -> None:
        """Private function for comparing latest version and current version of program

        Raises:
            Except: If unexpected error raised.

        """

        url : str = str(setting["PyPi"]["urlProjectJson"])

        if 'b' not in str(setting["Program"]["version"]).lower():

            json_data = RequestsGetter.get_result_by_request(url=url, is_json=True)

            current_version = str(setting["Program"]["version"])
            latest_version = json_data.get('info').get('version')

            current_version_tuple = tuple(map(int, (current_version.split("."))))
            latest_version_tuple = tuple(map(int, (latest_version.split("."))))

            if latest_version_tuple > current_version_tuple:
                message = ('Your selenium-driver-updater library is out of date,'
                        'please update it via "pip install selenium-driver-updater --upgrade" '
                        f'current_version: {current_version} latest_version: {latest_version} ')
                logger.warning(message)

            elif latest_version_tuple == current_version_tuple:
                message = 'Your selenium-driver-updater library is up to date.'
                logger.info(message)

            else:
                message = 'Unable to compare the latest version and the current version of the library.'
                logger.error(message)

        else:

            message = ('Thanks for participating in beta releases for selenium-driver-updater library,' 
                        f'you are using the beta version {str(setting["Program"]["version"])}')
            logger.info(message)
            message = 'Note that beta version does not guarantee errors avoiding. If something goes wrong - please create an issue on github repository'
            logger.info(message)

    @staticmethod
    def __check_is_python_version_compatible_for_library() -> None:
        """Private function for checking if python version if compatible with python version 3+

        Raises:
            Except: If unexpected error raised.

        """

        major = str(sys.version_info[0])
        minor = str(sys.version_info[1])
        patch = str(sys.version_info[2])

        python_version = f"{major}.{minor}.{patch}"

        if major != "3":
            message = (f"selenium-driver-updater works only on Python 3, you are using {python_version} which is unsupported by this library, "
                        f"you may have some troubles or errors if you will proceed.")
            logger.warning(message)

    @staticmethod
    def __check_enviroment_and_variables() -> None:
        """Private function for checking all input parameters and enviroment

        Raises:
            Except: If unexpected error raised.

        """

        DriverUpdater.__check_is_python_version_compatible_for_library()

        if _info.enable_library_update_check:

            DriverUpdater.__check_library_is_up_to_date()

        DriverUpdater.__check_all_input_parameteres()

    @staticmethod
    def __run_specific_driver(**kwargs) -> str:
        """Private function for run download or update for specific driver

        Args:
            driver_name (Union[str, list[str]]) : Specified driver name/names which will be downloaded or updated. Like "DriverUpdater.chromedriver" or etc.
            filename (str)                      : Specific name for chromedriver. If given, it will replace name for chromedriver. Defaults to empty string.
            version (str)                       : Specific version for chromedriver. If given, it will downloads given version. Defaults to empty string.
            system_name (Union[str, list[str]]) : Specific OS for driver. Defaults to empty string.

        Returns:
            str

            driver_path (str) : Path where specific driver located

        Raises:
            Except: If unexpected error raised.

        """

        driver_path : str = ''

        driver_name = kwargs.get('driver_name', _info.driver_name)
        filename = kwargs.get('filename', _info.filename)
        version = kwargs.get('version', _info.version)
        system_name = kwargs.get('system_name', _info.system_name)

        parametres = dict(  path=_info.path, upgrade=_info.upgrade, chmod=_info.chmod,
                            check_driver_is_up_to_date=_info.check_driver_is_up_to_date,
                            filename=filename, version=version,
                            check_browser_is_up_to_date=_info.check_browser_is_up_to_date,
                            info_messages=_info.info_messages,
                            system_name=system_name )

        if _info.system_name:
            setting['Program']['DriversFileFormat'] = '.exe' if 'win' in _info.system_name or 'arm' in _info.system_name else ''

        driver = _all_drivers.get(driver_name)(**parametres)
        driver_path = driver.main()

        return driver_path

    @staticmethod
    def __check_driver_name_is_valid(driver_name) -> None:
        """Private function for checking if specified driver_name is exists and valid

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.

        Raises:
            Except: If unexpected error raised.

        """

        driver_name_check = _all_drivers.get(driver_name)

        if not driver_name_check:
            message = f'Unknown driver name was specified current driver_name is: {driver_name}'
            raise ValueError(message)

    @staticmethod
    def __check_system_name_is_valid(system_name) -> None:
        """Private function for checking if specified system_name is exists and valid

        Raises:
            Except: If unexpected error raised.

        """

        system_name_check = system_name in [DriverUpdater.__dict__[item] for item in DriverUpdater.__dict__]

        if not system_name_check:
            message = f'Unknown system name was specified current system_name is: {system_name}'
            raise ValueError(message)

    @staticmethod
    def __check_parameter_type_is_valid(parameter, needed_type, parameter_name) -> None:

        if not isinstance(parameter, needed_type):
            message = f'The type of {parameter_name} must be a {needed_type} current type is: {type(parameter)}'
            raise TypeError(message)
