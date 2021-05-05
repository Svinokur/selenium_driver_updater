import unittest
import sys
import time
import platform
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from _setting import setting

base_dir = os.path.dirname(os.path.abspath(__file__))[:-5] + os.path.sep

os_bit = platform.architecture()[0][:-3]

latest_release = 'https://chromedriver.storage.googleapis.com/{}/'

chromedriver_latest_release =   latest_release + f"chromedriver_win32.zip" if platform.system() == 'Windows' else\
                                latest_release + "chromedriver_linux64.zip" if platform.system() == "Linux" else\
                                latest_release + "chromedriver_mac64_m1.zip" if 'ARM' in str(os.uname()) and platform.system() == 'Darwin' else\
                                latest_release + "chromedriver_mac64.zip"

chromedriver_platform_release = "chromedriver.exe" if platform.system() == 'Windows' else\
                                "chromedriver"

geckodriver_platform_release = f"win{os_bit}" if platform.system() == 'Windows' else\
                    f"linux{os_bit}" if platform.system() == "Linux" else\
                    "macos-aarch64" if 'ARM64' in str(os.uname()) else\
                    "macos"

geckodriver_platform_last_release = "geckodriver.exe" if platform.system() == 'Windows' else\
                                "geckodriver"

operadriver_latest_release =    f"operadriver_win{os_bit}.zip" if platform.system() == 'Windows' else\
                                "operadriver_linux64.zip" if platform.system() == "Linux" else\
                                "operadriver_mac64.zip"

operadriver_platform_release = "operadriver.exe" if platform.system() == 'Windows' else\
                                    "operadriver"

latest_release_edgedriver = 'https://msedgedriver.azureedge.net/{}/'
edgedriver_latest_release =     latest_release_edgedriver + f"edgedriver_win{os_bit}.zip" if platform.system() == 'Windows' else\
                                latest_release_edgedriver + "edgedriver_linux64.zip" if platform.system() == "Linux" else\
                                latest_release_edgedriver + "edgedriver_mac64.zip" if platform.system() == 'Darwin' else\
                                latest_release_edgedriver + "edgedriver_arm64.zip"
                                
edgedriver_platform_release =  "msedgedriver.exe" if platform.system() == 'Windows' else\
                             "msedgedriver"

chrome_browser_updater = fr'"C:\Program Files (x86)\Google\Update\GoogleUpdate.exe"' if platform.system() == 'Windows' else \
'open "/Library/Google/GoogleSoftwareUpdate/GoogleSoftwareUpdate.bundle/Contents/Helpers/GoogleSoftwareUpdateAgent.app"' if platform.system() == 'Darwin' else ''

chrome_browser_updater_path = r"C:\Program Files (x86)\Google\Update\GoogleUpdate.exe" if platform.system() == 'Windows' else \
'/Library/Google/GoogleSoftwareUpdate/GoogleSoftwareUpdate.bundle/Contents/Helpers/GoogleSoftwareUpdateAgent.app' if platform.system() == 'Darwin' else ''

firefox_browser_updater = r'"C:\Program Files\Mozilla Firefox\updater.exe"' if platform.system() == 'Windows' else \
'open "/Applications/Firefox.app/Contents/MacOS/updater.app"' if platform.system() == 'Darwin' else ''

firefox_browser_updater_path = r"C:\Program Files\Mozilla Firefox\updater.exe" if platform.system() == 'Windows' else \
'/Applications/Firefox.app/Contents/MacOS/updater.app' if platform.system() == 'Darwin' else ''

edge_browser_updater = fr'"C:\Program Files (x86)\Microsoft\EdgeUpdate\MicrosoftEdgeUpdate.exe"' if platform.system() == 'Windows' else \
'open "/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/Microsoft Update Assistant.app"' if platform.system() == 'Darwin' else ''

edge_browser_updater_path = fr"C:\Program Files (x86)\Microsoft\EdgeUpdate\MicrosoftEdgeUpdate.exe" if platform.system() == 'Windows' else \
'/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/Microsoft Update Assistant.app' if platform.system() == 'Darwin' else ''

opera_browser_updater = fr'"C:\\Users\\{os.getenv("username")}\\AppData\Local\Programs\Opera\launcher.exe" --scheduledautoupdate $(Arg0)' if platform.system() == 'Windows' else \
'open -a "/Applications/Opera.app/Contents/MacOS/opera_autoupdate"' if platform.system() == 'Darwin' else ''

opera_browser_updater_path = fr"C:\\Users\\{os.getenv('username')}\\AppData\Local\Programs\Opera\launcher.exe" if platform.system() == 'Windows' else \
'/Applications/Opera.app/Contents/MacOS/opera_autoupdate' if platform.system() == 'Darwin' else ''

class testSetting(unittest.TestCase): 
    """Class for unit-testing settings

    Attributes:
        setting (dict[str]) : Dict of all additional parametres
        startTime (float)   : Time of starting unit-tests

    """

    def setUp(self):
        self.setting = setting
        
        self.startTime : float = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_checkCountMainParam(self):
        self.assertEqual(len(self.setting), 10)

    #@unittest.skip('Temporary not needed')
    def test02_checkCountParams(self):
        self.assertEqual(len(self.setting["ChromeDriver"]), 4)
        self.assertEqual(len(self.setting["GeckoDriver"]), 4)
        self.assertEqual(len(self.setting["OperaDriver"]), 4)
        self.assertEqual(len(self.setting["EdgeDriver"]), 3)
        self.assertEqual(len(self.setting["ChromeBrowser"]), 3)
        self.assertEqual(len(self.setting["FirefoxBrowser"]), 3)
        self.assertEqual(len(self.setting["EdgeBrowser"]), 3)
        self.assertEqual(len(self.setting["OperaBrowser"]), 4)
        self.assertEqual(len(self.setting["JsonSchema"]), 2)
        self.assertEqual(len(self.setting["Github"]), 2)
    
    #@unittest.skip('Temporary not needed')
    def test03_checkValuesParams(self):

        self.assertEqual(self.setting["ChromeDriver"]["LinkLastRelease"], "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
        self.assertEqual(self.setting["ChromeDriver"]["LinkLastReleaseFile"], chromedriver_latest_release)
        self.assertEqual(self.setting["ChromeDriver"]["LastReleasePlatform"], chromedriver_platform_release)
        self.assertEqual(self.setting["ChromeDriver"]["LinkLatestReleaseSpecificVersion"], "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{}")

        self.assertEqual(self.setting["GeckoDriver"]["LinkLastRelease"], 'https://api.github.com/repos/mozilla/geckodriver/releases/latest')
        self.assertEqual(self.setting["GeckoDriver"]["LinkLastReleasePlatform"], geckodriver_platform_release)
        self.assertEqual(self.setting["GeckoDriver"]["LastReleasePlatform"], geckodriver_platform_last_release)
        self.assertEqual(self.setting["GeckoDriver"]["LinkAllReleases"], 'https://api.github.com/repos/mozilla/geckodriver/releases')

        self.assertEqual(self.setting["OperaDriver"]["LinkLastRelease"], 'https://api.github.com/repos/operasoftware/operachromiumdriver/releases/latest')
        self.assertEqual(self.setting["OperaDriver"]["LinkLastReleasePlatform"], operadriver_latest_release)
        self.assertEqual(self.setting["OperaDriver"]["LastReleasePlatform"], operadriver_platform_release)
        self.assertEqual(self.setting["OperaDriver"]["LinkAllReleases"], 'https://api.github.com/repos/operasoftware/operachromiumdriver/releases')

        self.assertEqual(self.setting["EdgeDriver"]["LinkLastRelease"], 'https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/')
        self.assertEqual(self.setting["EdgeDriver"]["LinkLastReleaseFile"], edgedriver_latest_release)
        self.assertEqual(self.setting["EdgeDriver"]["LastReleasePlatform"], edgedriver_platform_release)

        self.assertEqual(self.setting["ChromeBrowser"]["LinkAllLatestRelease"], 'https://chromereleases.googleblog.com')
        self.assertEqual(self.setting["ChromeBrowser"]["ChromeBrowserUpdater"], chrome_browser_updater)
        self.assertEqual(self.setting["ChromeBrowser"]["ChromeBrowserUpdaterPath"], chrome_browser_updater_path)

        self.assertEqual(self.setting["FirefoxBrowser"]["LinkAllLatestReleases"], 'https://www.mozilla.org/en-US/firefox/releases/')
        self.assertEqual(self.setting["FirefoxBrowser"]["FirefoxBrowserUpdater"], firefox_browser_updater)
        self.assertEqual(self.setting["FirefoxBrowser"]["FirefoxBrowserUpdaterPath"], firefox_browser_updater_path)

        self.assertEqual(self.setting["EdgeBrowser"]["LinkAllLatestRelease"], 'https://docs.microsoft.com/en-us/deployedge/microsoft-edge-relnote-stable-channel')
        self.assertEqual(self.setting["EdgeBrowser"]["EdgeBrowserUpdater"], edge_browser_updater)
        self.assertEqual(self.setting["EdgeBrowser"]["EdgeBrowserUpdaterPath"], edge_browser_updater_path)

        self.assertEqual(self.setting["OperaBrowser"]["LinkAllReleases"], 'https://blogs.opera.com/desktop/?s=changelog')
        self.assertEqual(self.setting["OperaBrowser"]["LinkSpecificReleaseChangelog"], 'https://blogs.opera.com/desktop/changelog-for-{}/')
        self.assertEqual(self.setting["OperaBrowser"]["OperaBrowserUpdater"], opera_browser_updater)
        self.assertEqual(self.setting["OperaBrowser"]["OperaBrowserUpdaterPath"], opera_browser_updater_path)

        self.assertEqual(self.setting["JsonSchema"]["githubAssetSchema"], base_dir + 'schemas' + os.path.sep + 'github_asset_schema.json')
        self.assertEqual(self.setting["JsonSchema"]["githubReleaseSchema"], base_dir + 'schemas' + os.path.sep + 'github_release_schema.json')

        self.assertEqual(self.setting["Github"]["linkLatestReleaseBySpecificRepoName"], 'https://api.github.com/repos/{}/releases/latest')
        self.assertEqual(self.setting["Github"]["linkAllReleasesBySpecificRepoName"], 'https://api.github.com/repos/{}/releases')

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)