from .chromeDriver import ChromeDriver
import logging
import os

class DriverUpdater():

    chromedriver = 'chromedriver'
    geckodriver = 'geckodriver'

    def __init__(self, path : str, driver_name : str):
        self.path = path
        self.driver_name : str = DriverUpdater.chromedriver if DriverUpdater.chromedriver == driver_name else \
                                 DriverUpdater.geckodriver  if DriverUpdater.geckodriver == driver_name else ''

        if not self.driver_name:
            message = 'Unknown driver name was specified'
            logging.error(message)
            return
        

    def install(self, upgrade : bool = False, chmod : bool = True):
        file_name : str = ''

        if not os.path.exists(self.path):
            message = f"The specified path does not exists current path is : {self.path}"
            logging.error(message)
            return file_name

        if DriverUpdater.chromedriver == self.driver_name:

            chrome_driver = ChromeDriver(path=self.path, upgrade=upgrade, chmod=chmod)
            result, message, file_name = chrome_driver.check_if_chromedriver_is_up_to_date()
            if not result:
                logging.error(message)
                
            return file_name