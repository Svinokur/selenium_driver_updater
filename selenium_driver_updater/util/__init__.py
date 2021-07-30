from selenium_driver_updater._chromeDriver import ChromeDriver
from selenium_driver_updater._geckoDriver import GeckoDriver
from selenium_driver_updater._operaDriver import OperaDriver
from selenium_driver_updater._edgeDriver import EdgeDriver
from selenium_driver_updater._chromiumChromeDriver import ChromiumChromeDriver
from selenium_driver_updater._phantomJS import PhantomJS

ALL_DRIVERS= {
    "chromedriver" : ChromeDriver,
    "geckodriver" : GeckoDriver,
    "operadriver" : OperaDriver,
    "edgedriver" : EdgeDriver,
    "chromium_chromedriver" : ChromiumChromeDriver,
    "phantomjs" : PhantomJS,
}
