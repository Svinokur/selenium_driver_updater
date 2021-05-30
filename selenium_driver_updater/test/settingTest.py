import unittest
import sys
import time
import platform
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from _setting import setting
from _setting import info

base_dir = os.path.dirname(os.path.abspath(__file__))[:-5] + os.path.sep

os_bit = platform.architecture()[0][:-3]

latest_release = 'https://chromedriver.storage.googleapis.com/{}/'

chromedriver_latest_release =   latest_release + f"chromedriver_win32.zip" if platform.system() == 'Windows' else\
                                latest_release + "chromedriver_linux64.zip" if platform.system() == "Linux" else\
                                latest_release + "chromedriver_mac64_m1.zip" if 'arm' in str(os.uname().machine) and platform.system() == 'Darwin' else\
                                latest_release + "chromedriver_mac64.zip"

chromedriver_platform_release = "chromedriver.exe" if platform.system() == 'Windows' else\
                                "chromedriver"



geckodriver_platform_release = f"win{os_bit}" if platform.system() == 'Windows' else\
                    f"linux{os_bit}" if platform.system() == "Linux" else\
                    "macos-aarch64" if 'arm' in str(os.uname().machine) and platform.system() == 'Darwin' else\
                    "macos"

geckodriver_platform_last_release = "geckodriver.exe" if platform.system() == 'Windows' else\
                                "geckodriver"



operadriver_latest_release =    f"operadriver_win{os_bit}.zip" if platform.system() == 'Windows' else\
                                "operadriver_linux64.zip" if platform.system() == "Linux" else\
                                "operadriver_mac64.zip"

operadriver_platform_release = "operadriver.exe" if platform.system() == 'Windows' else\
                                    "operadriver"

operadriver_name_platform_release = f"operadriver_win{os_bit}" if platform.system() == 'Windows' else\
                                    "operadriver_linux64" if platform.system() == "Linux" else\
                                    "operadriver_mac64"



latest_release_edgedriver = 'https://msedgedriver.azureedge.net/{}/'
edgedriver_latest_release =     latest_release_edgedriver + f"edgedriver_win{os_bit}.zip" if platform.system() == 'Windows' else\
                                latest_release_edgedriver + "edgedriver_mac64.zip" if platform.system() == 'Darwin' else\
                                latest_release_edgedriver + "edgedriver_linux64" if platform.system() == 'Linux' else\
                                latest_release_edgedriver + "edgedriver_arm64.zip"
                                
edgedriver_platform_release =  "msedgedriver.exe" if platform.system() == 'Windows' else\
                             "msedgedriver"

url_release_phantomjs = "https://bitbucket.org/ariya/phantomjs/downloads/"
os_bit_linux = 'x86_64' if os_bit == '64' else "i686"
phantomjs_latest_release =      url_release_phantomjs + "phantomjs-{}-windows.zip" if platform.system() == 'Windows' else\
                                url_release_phantomjs + "phantomjs-{}-linux-{}.tar.bz2".format({}, os_bit_linux) if platform.system() == "Linux" else\
                                url_release_phantomjs + "phantomjs-{}-macosx.zip"

phantomjs_platform_release = "phantomjs.exe" if platform.system() == 'Windows' else\
                                "phantomjs"


#
# UPDATERS
#                 

chrome_browser_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' if platform.system() == 'Darwin' else \
'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version' if platform.system() == 'Windows' else \
"google-chrome-stable" if platform.system() == 'Linux' else ''

chrome_browser_updater = fr'"C:\Program Files (x86)\Google\Update\GoogleUpdate.exe"' if platform.system() == 'Windows' else \
'open "/Library/Google/GoogleSoftwareUpdate/GoogleSoftwareUpdate.bundle/Contents/Helpers/GoogleSoftwareUpdateAgent.app"' if platform.system() == 'Darwin' else\
"sudo apt-get install google-chrome-stable" if platform.system() == 'Linux' else ''

chrome_browser_updater_path = r"C:\Program Files (x86)\Google\Update\GoogleUpdate.exe" if platform.system() == 'Windows' else \
'/Library/Google/GoogleSoftwareUpdate/GoogleSoftwareUpdate.bundle/Contents/Helpers/GoogleSoftwareUpdateAgent.app' if platform.system() == 'Darwin' else ''


firefox_browser_path = '/Applications/Firefox.app/Contents/MacOS/firefox' if platform.system() == 'Darwin' else \
['reg query "HKEY_CURRENT_USER\Software\Mozilla\Mozilla Firefox" /v CurrentVersion',
'reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Mozilla\Mozilla Firefox" /v CurrentVersion'] if platform.system() == 'Windows' else\
"firefox" if platform.system() == 'Linux' else ''

firefox_browser_updater = r'"C:\Program Files\Mozilla Firefox\updater.exe"' if platform.system() == 'Windows' else \
'open "/Applications/Firefox.app/Contents/MacOS/updater.app"' if platform.system() == 'Darwin' else\
"sudo apt-get install firefox" if platform.system() == 'Linux' else ''

firefox_browser_updater_path = r"C:\Program Files\Mozilla Firefox\updater.exe" if platform.system() == 'Windows' else \
'/Applications/Firefox.app/Contents/MacOS/updater.app' if platform.system() == 'Darwin' else ''



edge_browser_path = '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge' if platform.system() == 'Darwin' else\
'reg query "HKEY_USERS\S-1-5-21-3790059719-4236911619-2548269985-1000\Software\Microsoft\Edge\BLBeacon" /v version' if platform.system() == 'Windows' else ''

edge_browser_updater = fr'"C:\Program Files (x86)\Microsoft\EdgeUpdate\MicrosoftEdgeUpdate.exe"' if platform.system() == 'Windows' else \
'open "/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/Microsoft Update Assistant.app"' if platform.system() == 'Darwin' else ''

edge_browser_updater_path = fr"C:\Program Files (x86)\Microsoft\EdgeUpdate\MicrosoftEdgeUpdate.exe" if platform.system() == 'Windows' else \
'/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/Microsoft Update Assistant.app' if platform.system() == 'Darwin' else ''


opera_browser_path = r'REG QUERY "HKEY_USERS\S-1-5-21-3790059719-4236911619-2548269985-1000\Software\Microsoft\Windows\CurrentVersion\Uninstall"' if platform.system() == 'Windows' else \
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
        
        self.startTime : float = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_check_count_main_param(self):
        self.assertEqual(len(self.setting), 15)

    #@unittest.skip('Temporary not needed')
    def test02_check_count_params(self):
        self.assertEqual(len(self.setting["Program"]), 2)
        self.assertEqual(len(self.setting["ChromeDriver"]), 4)
        self.assertEqual(len(self.setting["GeckoDriver"]), 5)
        self.assertEqual(len(self.setting["OperaDriver"]), 5)
        self.assertEqual(len(self.setting["EdgeDriver"]), 3)
        self.assertEqual(len(self.setting["ChromiumChromeDriver"]), 1)
        self.assertEqual(len(self.setting["PhantomJS"]), 2)

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
        self.assertEqual(self.setting["Program"]["wedriverVersionPattern"], '[0-9]+.[0-9]+.[0-9]+.[0-9]+')

        self.assertEqual(self.setting["ChromeDriver"]["LinkLastRelease"], "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
        self.assertEqual(self.setting["ChromeDriver"]["LinkLastReleaseFile"], chromedriver_latest_release)
        self.assertEqual(self.setting["ChromeDriver"]["LastReleasePlatform"], chromedriver_platform_release)
        self.assertEqual(self.setting["ChromeDriver"]["LinkLatestReleaseSpecificVersion"], "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{}")

        self.assertEqual(self.setting["GeckoDriver"]["LinkLastRelease"], 'https://api.github.com/repos/mozilla/geckodriver/releases/latest')
        self.assertEqual(self.setting["GeckoDriver"]["LinkLastReleasePlatform"], geckodriver_platform_release)
        self.assertEqual(self.setting["GeckoDriver"]["LastReleasePlatform"], geckodriver_platform_last_release)
        self.assertEqual(self.setting["GeckoDriver"]["LinkAllReleases"], 'https://api.github.com/repos/mozilla/geckodriver/releases')
        self.assertEqual(self.setting["GeckoDriver"]["geckodriverVersionPattern"], "[0-9]+.[0-9]+.[0-9]+")

        self.assertEqual(self.setting["OperaDriver"]["LinkLastRelease"], 'https://api.github.com/repos/operasoftware/operachromiumdriver/releases/latest')
        self.assertEqual(self.setting["OperaDriver"]["LinkLastReleasePlatform"], operadriver_latest_release)
        self.assertEqual(self.setting["OperaDriver"]["LastReleasePlatform"], operadriver_platform_release)
        self.assertEqual(self.setting["OperaDriver"]["LinkAllReleases"], 'https://api.github.com/repos/operasoftware/operachromiumdriver/releases')
        self.assertEqual(self.setting["OperaDriver"]["NamePlatformRelease"], operadriver_name_platform_release)

        self.assertEqual(self.setting["EdgeDriver"]["LinkLastRelease"], 'https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/')
        self.assertEqual(self.setting["EdgeDriver"]["LinkLastReleaseFile"], edgedriver_latest_release)
        self.assertEqual(self.setting["EdgeDriver"]["LastReleasePlatform"], edgedriver_platform_release)

        self.assertEqual(self.setting["ChromiumChromeDriver"]["ChromiumChromeDriverUpdater"], chromiumchromedriver_updater)

        self.assertEqual(self.setting["PhantomJS"]["LinkLastReleaseFile"], phantomjs_latest_release)
        self.assertEqual(self.setting["PhantomJS"]["LastReleasePlatform"], phantomjs_platform_release)

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
        self.assertEqual(self.setting["Github"]["linkAllReleasesBySpecificRepoName"], 'https://api.github.com/repos/{}/releases')
        self.assertEqual(self.setting["Github"]["linkAllReleasesTags"], 'https://api.github.com/repos/{}/git/refs/tags')

        self.assertEqual(self.setting["PyPi"]["urlProjectJson"], 'https://pypi.python.org/pypi/selenium-driver-updater/json')

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)