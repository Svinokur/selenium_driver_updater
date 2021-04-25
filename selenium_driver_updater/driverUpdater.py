from .chromeDriver import ChromeDriver
from .geckoDriver import GeckoDriver
from .operaDriver import OperaDriver
from .edgeDriver import EdgeDriver

import logging
import os
import traceback
from typing import Tuple

class DriverUpdater():

    chromedriver = 'chromedriver'
    geckodriver = 'geckodriver'
    operadriver = 'operadriver'
    edgedriver = 'edgedriver'
        
    @staticmethod
    def install(path : str, driver_name : str, upgrade : bool = False, chmod : bool = True, check_driver_is_up_to_date : bool = False, 
                info_messages : bool = True, filename : str = '', version : str = '') -> Tuple[bool, str, str]:
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

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str) : Path where Selenium driver binary was downloaded or updated.

        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''

        path = os.path.abspath(path) + os.path.sep

        driver_name =   DriverUpdater.chromedriver if DriverUpdater.chromedriver == driver_name else \
                        DriverUpdater.geckodriver  if DriverUpdater.geckodriver == driver_name else \
                        DriverUpdater.operadriver if DriverUpdater.operadriver == driver_name else \
                        DriverUpdater.edgedriver if DriverUpdater.edgedriver == driver_name else '' 

        filename = filename.replace('.', '')

        try:

            result, message = DriverUpdater.__check_all_input_parameteres(path=path, driver_name=driver_name)
            if not result:
                logging.error(message)
                return result, message, driver_path

            if DriverUpdater.chromedriver == driver_name:

                chrome_driver = ChromeDriver(path=path, upgrade=upgrade, chmod=chmod, 
                                            check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                            info_messages=info_messages, filename=filename, version=version)
                result, message, driver_path = chrome_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.geckodriver == driver_name:

                gecko_driver = GeckoDriver(path=path, upgrade=upgrade, chmod=chmod, 
                                        check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                        info_messages=info_messages, filename=filename, version=version)
                result, message, driver_path = gecko_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.operadriver == driver_name:

                opera_driver = OperaDriver(path=path, upgrade=upgrade, chmod=chmod, 
                                        check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                        info_messages=info_messages, filename=filename, version=version)
                result, message, driver_path = opera_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            elif DriverUpdater.edgedriver == driver_name:

                edge_driver = EdgeDriver(path=path, upgrade=upgrade, chmod=chmod, 
                                    check_driver_is_up_to_date=check_driver_is_up_to_date, 
                                    info_messages=info_messages, filename=filename, version=version)
                result, message, driver_path = edge_driver.main()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
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
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run