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

    def __init__(self, path : str, driver_name : str):
        """Class for working with Selenium driver binaries

        Args:
            path (str)          : Specified path which will used for downloading or updating Selenium driver binary. Must be folder path.
            driver_name (str)   : Specified driver name which will be downloaded or updated. Like "DriverUpdater.chromedriver" or etc.
        """
        
        self.path = os.path.abspath(path) + os.path.sep

        self.driver_name : str =    DriverUpdater.chromedriver if DriverUpdater.chromedriver == driver_name else \
                                    DriverUpdater.geckodriver  if DriverUpdater.geckodriver == driver_name else \
                                    DriverUpdater.operadriver if DriverUpdater.operadriver == driver_name else \
                                    DriverUpdater.edgedriver if DriverUpdater.edgedriver == driver_name else '' 
        

    def install(self, upgrade : bool = False, chmod : bool = True, check_driver_is_up_to_date : bool = False, 
                info_messages : bool = True) -> str:
        """Function for install or update Selenium driver binary

        Args:
            upgrade (bool)                      : If true, it will overwrite existing driver in the folder. Defaults to False.
            chmod (bool)                        : If true, it will make chromedriver binary executable. Defaults to True.
            check_driver_is_up_to_date (bool)   : If true, it will check driver version before and after upgrade. Defaults to False.
            info_messages (bool)                : If false, it will disable all info messages. Defaults to True.

        Returns:
            file_name (str) : Path where Selenium driver binary was downloaded or updated.

        Raises:
            Except: If unexpected error raised. 

        """

        file_name : str = ''

        try:

            result, message = self.__check_all_input_parameteres()
            if not result:
                logging.error(message)
                return file_name

            if DriverUpdater.chromedriver == self.driver_name:

                chrome_driver = ChromeDriver(path=self.path, upgrade=upgrade, chmod=chmod, check_driver_is_up_to_date=check_driver_is_up_to_date, info_messages=info_messages)
                result, message, file_name = chrome_driver.check_if_chromedriver_is_up_to_date()
                if not result:
                    logging.error(message)
                    return file_name

            elif DriverUpdater.geckodriver == self.driver_name:

                gecko_driver = GeckoDriver(path=self.path, upgrade=upgrade, chmod=chmod, check_driver_is_up_to_date=check_driver_is_up_to_date, info_messages=info_messages)
                result, message, file_name = gecko_driver.check_if_geckodriver_is_up_to_date()
                if not result:
                    logging.error(message)
                    return file_name

            elif DriverUpdater.operadriver == self.driver_name:

                opera_driver = OperaDriver(path=self.path, upgrade=upgrade, chmod=chmod, check_driver_is_up_to_date=check_driver_is_up_to_date, info_messages=info_messages)
                result, message, file_name = opera_driver.check_if_operadriver_is_up_to_date()
                if not result:
                    logging.error(message)
                    return file_name

            elif DriverUpdater.edgedriver == self.driver_name:

                edge_driver = EdgeDriver(path=self.path, upgrade=upgrade, chmod=chmod, check_driver_is_up_to_date=check_driver_is_up_to_date, info_messages=info_messages)
                result, message, file_name = edge_driver.check_if_edgedriver_is_up_to_date()
                if not result:
                    logging.error(message)
                    return file_name

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return file_name

    def __check_all_input_parameteres(self) -> Tuple[bool, str]:
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

            if not os.path.exists(self.path):
                message = f"The specified path does not exist current path is: {self.path}"
                logging.error(message)
                return result_run, message

            if not os.path.isdir(self.path):
                message = f"The specified path is not a folder current path is: {self.path}"
                logging.error(message)
                return result_run, message

            if not self.driver_name:
                message = f'Unknown driver name was specified current driver_name is: {self.driver_name}'
                logging.error(message)
                return result_run, message

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run