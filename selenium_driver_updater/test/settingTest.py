import unittest
import sys
import time
import platform
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))

from selenium_driver_updater._setting import setting
from selenium_driver_updater._setting import info

#pylint: disable=invalid-name
base_dir = os.path.dirname(os.path.abspath(__file__))[:-5] + os.path.sep

os_bit = platform.architecture()[0][:-3]

latest_release = 'https://chromedriver.storage.googleapis.com/{}/'

chromedriver_latest_release =   "chromedriver_win32.zip" if platform.system() == 'Windows' else\
                                "chromedriver_linux64.zip" if platform.system() == "Linux" else\
                                "chromedriver_mac64_m1.zip" if 'arm' in str(os.uname().machine)\
                                and platform.system() == 'Darwin' else\
                                "chromedriver_mac64.zip"
chromedriver_latest_release = latest_release + chromedriver_latest_release


latest_release_geckodriver = 'https://github.com/mozilla/geckodriver/releases/download/v{}/'
geckodriver_platform_release =  "geckodriver-v{}-" + f"win{os_bit}.zip" if platform.system() == 'Windows' else\
                                "geckodriver-v{}-" + f"linux{os_bit}.tar.gz" if platform.system() == "Linux" else\
                                "geckodriver-v{}-macos-aarch64.tar.gz" if 'arm' in str(os.uname().machine)\
                                and platform.system() == 'Darwin' else\
                                "geckodriver-v{}-macos.tar.gz"
geckodriver_platform_release = latest_release_geckodriver + geckodriver_platform_release


latest_release_operadriver = 'https://github.com/operasoftware/operachromiumdriver/releases/download/v.{}/'
operadriver_latest_release =    f"operadriver_win{os_bit}.zip" if platform.system() == 'Windows' else\
                                "operadriver_linux64.zip" if platform.system() == "Linux" else\
                                "operadriver_mac64.zip"
operadriver_latest_release = latest_release_operadriver + operadriver_latest_release

latest_release_edgedriver = 'https://msedgedriver.azureedge.net/{}/'
edgedriver_latest_release =     f"edgedriver_win{os_bit}.zip" if platform.system() == 'Windows' else\
                                "edgedriver_mac64.zip" if platform.system() == 'Darwin' else\
                                "edgedriver_linux64" if platform.system() == 'Linux' else\
                                "edgedriver_arm64.zip"
edgedriver_latest_release = latest_release_edgedriver + edgedriver_latest_release


url_release_phantomjs = "https://api.bitbucket.org/2.0/repositories/ariya/phantomjs/downloads/"
os_bit_linux = 'x86_64' if os_bit == '64' else "i686"
phantomjs_latest_release =  "phantomjs-{}-windows.zip" if platform.system() == 'Windows' else\
                            "phantomjs-{}-" + f"linux-{os_bit_linux}.tar.bz2" if platform.system() == "Linux" else\
                            "phantomjs-{}-macosx.zip"
phantomjs_latest_release = url_release_phantomjs + phantomjs_latest_release

#
# BROWSERS AND THEIR UPDATERS
#   

chrome_browser_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' if platform.system() == 'Darwin' else \
['reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
r'reg query "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome" /v version'] if platform.system() == 'Windows' else \
"google-chrome-stable" if platform.system() == 'Linux' else ''

chrome_browser_updater = r'"C:\Program Files (x86)\Google\Update\GoogleUpdate.exe"' if platform.system() == 'Windows' else \
'open "/Library/Google/GoogleSoftwareUpdate/GoogleSoftwareUpdate.bundle/Contents/Helpers/GoogleSoftwareUpdateAgent.app"' if platform.system() == 'Darwin' else\
"sudo apt-get install google-chrome-stable" if platform.system() == 'Linux' else ''

chrome_browser_updater_path = r"C:\Program Files (x86)\Google\Update\GoogleUpdate.exe" if platform.system() == 'Windows' else \
'/Library/Google/GoogleSoftwareUpdate/GoogleSoftwareUpdate.bundle/Contents/Helpers/GoogleSoftwareUpdateAgent.app' if platform.system() == 'Darwin' else ''


firefox_browser_path = '/Applications/Firefox.app/Contents/MacOS/firefox' if platform.system() == 'Darwin' else \
['reg query "HKEY_CURRENT_USER\Software\Mozilla\Mozilla Firefox" /v CurrentVersion',
'reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Mozilla\Mozilla Firefox" /v CurrentVersion',
r"Powershell (Get-Item (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe').'(Default)').VersionInfo.ProductVersion"] if platform.system() == 'Windows' else\
"firefox" if platform.system() == 'Linux' else ''

firefox_browser_updater = r'"C:\Program Files\Mozilla Firefox\updater.exe"' if platform.system() == 'Windows' else \
'open "/Applications/Firefox.app/Contents/MacOS/updater.app"' if platform.system() == 'Darwin' else\
"sudo apt-get install firefox" if platform.system() == 'Linux' else ''

firefox_browser_updater_path = r"C:\Program Files\Mozilla Firefox\updater.exe" if platform.system() == 'Windows' else \
'/Applications/Firefox.app/Contents/MacOS/updater.app' if platform.system() == 'Darwin' else ''



edge_browser_path = '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge' if platform.system() == 'Darwin' else\
'reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Edge\BLBeacon" /v version' if platform.system() == 'Windows' else ''

edge_browser_updater = r'"C:\Program Files (x86)\Microsoft\EdgeUpdate\MicrosoftEdgeUpdate.exe"' if platform.system() == 'Windows' else \
'open "/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/Microsoft Update Assistant.app"' if platform.system() == 'Darwin' else ''

edge_browser_updater_path = r"C:\Program Files (x86)\Microsoft\EdgeUpdate\MicrosoftEdgeUpdate.exe" if platform.system() == 'Windows' else \
'/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/Microsoft Update Assistant.app' if platform.system() == 'Darwin' else ''


opera_browser_path = r'reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall" /f Opera' if platform.system() == 'Windows' else \
'/Applications/Opera.app/Contents/MacOS/Opera' if platform.system() == 'Darwin' else\
"opera" if platform.system() == 'Linux' else ''

opera_browser_updater = fr'"C:\\Users\\{os.getenv("username")}\\AppData\Local\Programs\Opera\launcher.exe" --scheduledautoupdate $(Arg0)' if platform.system() == 'Windows' else \
'open -a "/Applications/Opera.app/Contents/MacOS/opera_autoupdate"' if platform.system() == 'Darwin' else\
"sudo apt-get install opera-stable" if platform.system() == 'Linux' else ''

opera_browser_updater_path = fr"C:\\Users\\{os.getenv('username')}\\AppData\Local\Programs\Opera\launcher.exe" if platform.system() == 'Windows' else \
'/Applications/Opera.app/Contents/MacOS/opera_autoupdate' if platform.system() == 'Darwin' else ''

chromiumbrowser_path = "chromium-browser"

chromiumbrowser_updater = "sudo apt-get install chromium-browser"

chromiumchromedriver_updater = "sudo apt-get install chromedriver"

# pylint: disable=missing-function-docstring
class testSetting(unittest.TestCase): 
    """Class for unit-testing settings

    Attributes:
        setting (dict[str]) : Dict of all additional parametres
        startTime (float)   : Time of starting unit-tests

    """

    @classmethod
    def setUpClass(cls):

        cls.setting = setting

    def setUp(self):

        self.start_time : float = time.time()

    def tearDown(self):
        end_time = time.time() - self.start_time
        print("%.3f" % end_time)

    #@unittest.skip('Temporary not needed')
    def test01_check_count_main_param(self):
        self.assertEqual(len(self.setting), 16)

    #@unittest.skip('Temporary not needed')
    def test02_check_count_params(self):
        self.assertEqual(len(self.setting["Program"]), 4)
        self.assertEqual(len(self.setting["ChromeDriver"]), 5)
        self.assertEqual(len(self.setting["GeckoDriver"]), 2)
        self.assertEqual(len(self.setting["OperaDriver"]), 2)
        self.assertEqual(len(self.setting["EdgeDriver"]), 5)
        self.assertEqual(len(self.setting["ChromiumChromeDriver"]), 1)
        self.assertEqual(len(self.setting["PhantomJS"]), 3)
        self.assertEqual(len(self.setting["SafariDriver"]), 2)

        self.assertEqual(len(self.setting["ChromeBrowser"]), 4)
        self.assertEqual(len(self.setting["FirefoxBrowser"]), 4)
        self.assertEqual(len(self.setting["EdgeBrowser"]), 4)
        self.assertEqual(len(self.setting["OperaBrowser"]), 5)
        self.assertEqual(len(self.setting["ChromiumBrowser"]), 2)

        self.assertEqual(len(self.setting["JsonSchema"]), 3)
        self.assertEqual(len(self.setting["Github"]), 3)
        self.assertEqual(len(self.setting["PyPi"]), 1)

    #@unittest.skip('Temporary not needed')
    def test03_check_values_params(self):

        self.assertEqual(self.setting["Program"]["version"], info.version)
        self.assertEqual(self.setting["Program"]["wedriverVersionPattern"], r'([0-9.]*\.[0-9]+)')
        self.assertEqual(self.setting["Program"]["driversPath"], base_dir + 'test' + os.path.sep + 'drivers' + os.path.sep)
        self.assertEqual(self.setting["Program"]["DriversFileFormat"], ".exe" if platform.system() == 'Windows' else '')

        self.assertEqual(self.setting["ChromeDriver"]["LinkLastRelease"], "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
        self.assertEqual(self.setting["ChromeDriver"]["LinkLastReleaseFile"], chromedriver_latest_release)
        self.assertEqual(self.setting["ChromeDriver"]["LastReleasePlatform"], 'chromedriver')
        self.assertEqual(self.setting["ChromeDriver"]["LinkLatestReleaseSpecificVersion"], "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{}")
        self.assertEqual(self.setting["ChromeDriver"]["LinkCheckVersionIsValid"], "https://chromedriver.storage.googleapis.com/?delimiter=/&prefix={}/")

        self.assertEqual(self.setting["GeckoDriver"]["LinkLastReleasePlatform"], geckodriver_platform_release)
        self.assertEqual(self.setting["GeckoDriver"]["LastReleasePlatform"], 'geckodriver')

        self.assertEqual(self.setting["OperaDriver"]["LinkLastReleasePlatform"], operadriver_latest_release)
        self.assertEqual(self.setting["OperaDriver"]["LastReleasePlatform"], 'operadriver')  

        self.assertEqual(self.setting["EdgeDriver"]["LinkLastRelease"], 'https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver/LATEST_STABLE')
        self.assertEqual(self.setting["EdgeDriver"]["LinkLastReleaseFile"], edgedriver_latest_release)
        self.assertEqual(self.setting["EdgeDriver"]["LastReleasePlatform"], 'msedgedriver')
        self.assertEqual(self.setting["EdgeDriver"]["LinkCheckVersionIsValid"], "https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver?prefix={}%2F&delimiter=%2F&maxresults=100&restype=container&comp=list&_=1622714933676&timeout=60000")
        self.assertEqual(self.setting["EdgeDriver"]["LinkLatestReleaseSpecificVersion"], "https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver/LATEST_RELEASE_{}")

        self.assertEqual(self.setting["ChromiumChromeDriver"]["ChromiumChromeDriverUpdater"], chromiumchromedriver_updater)

        self.assertEqual(self.setting["PhantomJS"]["LinkLastReleaseFile"], phantomjs_latest_release)
        self.assertEqual(self.setting["PhantomJS"]["LastReleasePlatform"], 'phantomjs')
        self.assertEqual(self.setting["PhantomJS"]["LinkAllReleases"], url_release_phantomjs)

        self.assertEqual(self.setting["SafariDriver"]["LinkLastRelease"], 'https://support.apple.com/en-us/HT201222')
        self.assertEqual(self.setting["SafariDriver"]["LastReleasePlatform"], 'safaridriver')

        self.assertEqual(self.setting["ChromeBrowser"]["Path"], chrome_browser_path)
        self.assertEqual(self.setting["ChromeBrowser"]["LinkAllLatestRelease"], 'https://chromereleases.googleblog.com/search/label/Stable%20updates')
        self.assertEqual(self.setting["ChromeBrowser"]["ChromeBrowserUpdater"], chrome_browser_updater)
        self.assertEqual(self.setting["ChromeBrowser"]["ChromeBrowserUpdaterPath"], chrome_browser_updater_path)

        self.assertEqual(self.setting["FirefoxBrowser"]["Path"], firefox_browser_path)
        self.assertEqual(self.setting["FirefoxBrowser"]["LinkAllLatestReleases"], 'https://www.mozilla.org/en-US/firefox/releases/')
        self.assertEqual(self.setting["FirefoxBrowser"]["FirefoxBrowserUpdater"], firefox_browser_updater)
        self.assertEqual(self.setting["FirefoxBrowser"]["FirefoxBrowserUpdaterPath"], firefox_browser_updater_path)

        self.assertEqual(self.setting["EdgeBrowser"]["Path"], edge_browser_path)
        self.assertEqual(self.setting["EdgeBrowser"]["LinkAllLatestRelease"], 'https://docs.microsoft.com/en-us/deployedge/microsoft-edge-relnote-stable-channel')
        self.assertEqual(self.setting["EdgeBrowser"]["EdgeBrowserUpdater"], edge_browser_updater)
        self.assertEqual(self.setting["EdgeBrowser"]["EdgeBrowserUpdaterPath"], edge_browser_updater_path)

        self.assertEqual(self.setting["OperaBrowser"]["Path"], opera_browser_path)
        self.assertEqual(self.setting["OperaBrowser"]["LinkAllReleases"], 'https://blogs.opera.com/desktop/?s=Stable+update')
        self.assertEqual(self.setting["OperaBrowser"]["LinkSpecificReleaseChangelog"], 'https://blogs.opera.com/desktop/changelog-for-{}/')
        self.assertEqual(self.setting["OperaBrowser"]["OperaBrowserUpdater"], opera_browser_updater)
        self.assertEqual(self.setting["OperaBrowser"]["OperaBrowserUpdaterPath"], opera_browser_updater_path)

        self.assertEqual(self.setting["ChromiumBrowser"]["Path"], chromiumbrowser_path)
        self.assertEqual(self.setting["ChromiumBrowser"]["ChromiumBrowserUpdater"], chromiumbrowser_updater)


        self.assertEqual(self.setting["JsonSchema"]["githubAssetSchema"], base_dir + 'schemas' + os.path.sep + 'github_asset_schema.json')
        self.assertEqual(self.setting["JsonSchema"]["githubReleaseSchema"], base_dir + 'schemas' + os.path.sep + 'github_release_schema.json')
        self.assertEqual(self.setting["JsonSchema"]["githubReleaseTagSchema"], base_dir + 'schemas' + os.path.sep + 'github_release_tag_schema.json')

        self.assertEqual(self.setting["Github"]["linkLatestReleaseBySpecificRepoName"], 'https://api.github.com/repos/{}/releases/latest')
        self.assertEqual(self.setting["Github"]["linkAllReleasesTags"], 'https://api.github.com/repos/{}/git/refs/tags')
        self.assertEqual(self.setting["Github"]["linkAllReleases"], 'https://api.github.com/repos/{}/releases')

        self.assertEqual(self.setting["PyPi"]["urlProjectJson"], 'https://pypi.python.org/pypi/selenium-driver-updater/json')

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)
    