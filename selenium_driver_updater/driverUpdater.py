import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from chromeDriver import ChromeDriver
from geckoDriver import GeckoDriver
from operaDriver import OperaDriver
from edgeDriver import EdgeDriver
from _setting import setting

import logging
import os
import traceback
from typing import Tuple

import requests
import json

class DriverUpdater():

    chromedriver = 'chromedriver'
    geckodriver = 'geckodriver'
    operadriver = 'operadriver'
    edgedriver = 'edgedriver'
        
    @staticmethod
    def install(path : str, driver_name : str, **kwargs):
        """Function for install or update Selenium driver binary

        Args:
            path (str)                          : Specified path which will used for downloading or updating Selenium driver binary. Must be folder path.
            driver_name (str)                   : Specified driver name which will be downloaded or updated. Like "DriverUpdater.chromedriver" or etc.
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

        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''

        info_messages = bool(kwargs.get('info_messages', True))
        if info_messages:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.ERROR)

        enable_library_update_check = bool(kwargs.get('enable_library_update_check', True))

        if enable_library_update_check:

            result, message = DriverUpdater.__check_library_is_up_to_date()
            if not result:
                logging.error(message)

        path = os.path.abspath(path) + os.path.sep

        driver_name =   DriverUpdater.chromedriver if DriverUpdater.chromedriver == driver_name else \
                        DriverUpdater.geckodriver  if DriverUpdater.geckodriver == driver_name else \
                        DriverUpdater.operadriver if DriverUpdater.operadriver == driver_name else \
                        DriverUpdater.edgedriver if DriverUpdater.edgedriver == driver_name else '' 

        filename : str = str(kwargs.get('filename', '')).replace('.', '')

        try:

            result, message = DriverUpdater.__check_all_input_parameteres(path=path, driver_name=driver_name)
            if not result:
                logging.error(message)
                return result, message, driver_path

            upgrade = kwargs.get('upgrade', False)
            chmod = kwargs.get('chmod', True)
            check_driver_is_up_to_date = kwargs.get('check_driver_is_up_to_date', False)
            version = kwargs.get('version', '')
            check_browser_is_up_to_date = kwargs.get('check_browser_is_up_to_date', False)

            if DriverUpdater.chromedriver == driver_name:

                chrome_driver = ChromeDriver(path=path, upgrade=upgrade, chmod=chmod, 
                                            check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                            filename=filename, version=version,
                                            check_browser_is_up_to_date=check_browser_is_up_to_date)
                result, message, driver_path = chrome_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.geckodriver == driver_name:

                gecko_driver = GeckoDriver(path=path, upgrade=upgrade, chmod=chmod, 
                                        check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                        filename=filename, version=version,
                                        check_browser_is_up_to_date=check_browser_is_up_to_date)
                result, message, driver_path = gecko_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.operadriver == driver_name:

                opera_driver = OperaDriver(path=path, upgrade=upgrade, chmod=chmod, 
                                        check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                        filename=filename, version=version,
                                        check_browser_is_up_to_date=check_browser_is_up_to_date)
                result, message, driver_path = opera_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.edgedriver == driver_name:

                edge_driver = EdgeDriver(path=path, upgrade=upgrade, chmod=chmod, 
                                    check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                    filename=filename, version=version,
                                    check_browser_is_up_to_date=check_browser_is_up_to_date)
                result, message, driver_path = edge_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    @staticmethod
    def __check_all_input_parameteres(path, driver_name) -> Tuple[bool, str]:
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

            if not driver_name:
                message = f'Unknown driver name was specified current driver_name is: {driver_name}'
                logging.error(message)
                return result_run, message

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
    
    @staticmethod
    def __check_library_is_up_to_date() -> Tuple[bool, str]:
        

        result_run : bool = False
        message_run : str = ''

        try:
            
            url = setting["PyPi"]["urlProjectJson"]
            request = requests.get(url=url)
            status_code = request.status_code

            if status_code != 200:
                message = f'Could not determine latest version of library, status_code not equal 200 status_code : {status_code} request_text: {request.text}'
                return result_run, message

            request_text = request.text
            json_data = json.loads(request_text)

            current_version = setting["Program"]["version"]
            latest_version = json_data.get('info').get('version')

            if latest_version != current_version:
                message = ('Your selenium-driver-updater library is out of date, please update it. '
                           f'current_version: {current_version} latest_version: {latest_version} ')
                logging.warning(message)

            elif latest_version == current_version:
                message = 'Your selenium-driver-updater library is up to date.'
                logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run