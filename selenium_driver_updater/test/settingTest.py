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
os_bit_phantom_js = 'x86_64' if os_bit == '64' else "i686"

is_arm = 'arm' in platform.processor().lower()
if os.name != 'nt':  # Check if not on Windows
    is_arm = is_arm or 'arm' in str(os.uname().machine)

os_type = {
    'Windows': {
        'chromedriver': f"win{os_bit}",
        'geckodriver': f"win{os_bit}.zip" if not is_arm else "win-aarch64.zip",
        'operadriver': f"win{os_bit}",
        'edgedriver': f"win{os_bit}",
        'phantomjs': "windows.zip",
    },
    'Linux': {
        'chromedriver': "linux64",
        'geckodriver': f"linux{os_bit}.tar.gz" if not is_arm else "linux-aarch64.tar.gz",
        'operadriver': "linux64",
        'edgedriver': "linux64",
        'phantomjs': f"linux-{os_bit_phantom_js}.tar.bz2",
    },
    'Darwin': {
        'chromedriver': "mac-x64" if not is_arm else "mac-arm64",
        'geckodriver': "macos.tar.gz" if not is_arm else "macos-aarch64.tar.gz",
        'operadriver': "mac64",
        'edgedriver': "mac64" if not is_arm else "mac64_m1",
        'phantomjs': "macosx",
    },
    'Other': {
        'edgedriver': "arm64" if is_arm else None,
    }
}

os_name = platform.system()
if os_name not in ['Darwin', 'Linux', 'Windows']:
    os_name = 'Other'

latest_release = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{}/"
chromedriver_latest_release = f'{latest_release}{os_type[os_name]["chromedriver"]}' + f"/chromedriver-{os_type[os_name]['chromedriver']}.zip"

latest_release_geckodriver = 'https://github.com/mozilla/geckodriver/releases/download/v{}/'
geckodriver_platform_release = f'{latest_release_geckodriver}geckodriver-v{{}}-{os_type[os_name]["geckodriver"]}'

latest_release_operadriver = 'https://github.com/operasoftware/operachromiumdriver/releases/download/v.{}/'
operadriver_latest_release = f'{latest_release_operadriver}operadriver_{os_type[os_name]["operadriver"]}.zip'

latest_release_edgedriver = 'https://msedgedriver.azureedge.net/{}/'
edgedriver_latest_release = f'{latest_release_edgedriver}edgedriver_{os_type[os_name]["edgedriver"]}.zip'

url_release_phantomjs = "https://api.bitbucket.org/2.0/repositories/ariya/phantomjs/downloads/"
phantomjs_latest_release = f'{url_release_phantomjs}phantomjs-{{}}-{os_type[os_name]["phantomjs"]}.zip'

#
# BROWSERS AND THEIR UPDATERS
#                                 

browser_paths = {
    'Darwin': {
        'chrome': ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                   "/Applications/Chromium.app/Contents/MacOS/Chromium"],
        'firefox': '/Applications/Firefox.app/Contents/MacOS/firefox',
        'edge': '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
        'edge_release': 'https://go.microsoft.com/fwlink/?linkid=2069148&platform=Mac&Consent=1&channel=Stable' if not is_arm else
                        'https://go.microsoft.com/fwlink/?linkid=2093504&platform=Mac&Consent=1&channel=Stable',
        'opera': '/Applications/Opera.app/Contents/MacOS/Opera',
    },
    'Windows': {
        'chrome': ['reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
                   r'reg query "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome" /v version'],
        'firefox': ['reg query "HKEY_CURRENT_USER\Software\Mozilla\Mozilla Firefox" /v CurrentVersion',
                    'reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Mozilla\Mozilla Firefox" /v CurrentVersion',
                    r"Powershell (Get-Item (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe').'(Default)').VersionInfo.ProductVersion"],
        'edge': 'reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Edge\BLBeacon" /v version',
        'opera': r'reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall" /f Opera',
    },
    'Linux': {
        'chrome': 'google-chrome-stable',
        'firefox': 'firefox',
        'opera': 'opera',
    }
}

chrome_browser_path = browser_paths[os_name].get('chrome', '')
firefox_browser_path = browser_paths[os_name].get('firefox', '')
edge_browser_path = browser_paths[os_name].get('edge', '')
edge_browser_release = browser_paths[os_name].get('edge_release', '')
opera_browser_path = browser_paths[os_name].get('opera', '')

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
        self.assertEqual(len(self.setting), 14)

    #@unittest.skip('Temporary not needed')
    def test02_check_count_params(self):
        self.assertEqual(len(self.setting["Program"]), 5)
        self.assertEqual(len(self.setting["ChromeDriver"]), 5)
        self.assertEqual(len(self.setting["GeckoDriver"]), 2)
        self.assertEqual(len(self.setting["OperaDriver"]), 2)
        self.assertEqual(len(self.setting["EdgeDriver"]), 5)
        self.assertEqual(len(self.setting["PhantomJS"]), 3)
        self.assertEqual(len(self.setting["SafariDriver"]), 2)

        self.assertEqual(len(self.setting["ChromeBrowser"]), 3)
        self.assertEqual(len(self.setting["FirefoxBrowser"]), 3)
        self.assertEqual(len(self.setting["EdgeBrowser"]), 3)
        self.assertEqual(len(self.setting["OperaBrowser"]), 2)

        self.assertEqual(len(self.setting["JsonSchema"]), 3)
        self.assertEqual(len(self.setting["Github"]), 3)
        self.assertEqual(len(self.setting["PyPi"]), 1)

    #@unittest.skip('Temporary not needed')
    def test03_check_values_params(self):

        self.assertEqual(self.setting["Program"]["version"], info.version)
        self.assertEqual(self.setting["Program"]["wedriverVersionPattern"], r'([0-9.]*\.[0-9]+)')
        self.assertEqual(self.setting["Program"]["driversPath"], base_dir + 'test' + os.path.sep + 'drivers' + os.path.sep)
        self.assertEqual(self.setting["Program"]["DriversFileFormat"], ".exe" if platform.system() == 'Windows' else '')
        self.assertEqual(self.setting["Program"]["OSBitness"], os_bit)

        self.assertEqual(self.setting["ChromeDriver"]["LinkLastRelease"], "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json")
        self.assertEqual(self.setting["ChromeDriver"]["LinkLastReleaseFile"], chromedriver_latest_release)
        self.assertEqual(self.setting["ChromeDriver"]["LastReleasePlatform"], 'chromedriver')
        self.assertEqual(self.setting["ChromeDriver"]["LinkLatestReleaseSpecificVersion"], "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{}")
        self.assertEqual(self.setting["ChromeDriver"]["LinkCheckVersionIsValid"], "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json")

        self.assertEqual(self.setting["GeckoDriver"]["LinkLastReleasePlatform"], geckodriver_platform_release)
        self.assertEqual(self.setting["GeckoDriver"]["LastReleasePlatform"], 'geckodriver')

        self.assertEqual(self.setting["OperaDriver"]["LinkLastReleasePlatform"], operadriver_latest_release)
        self.assertEqual(self.setting["OperaDriver"]["LastReleasePlatform"], 'operadriver')  

        self.assertEqual(self.setting["EdgeDriver"]["LinkLastRelease"], 'https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver/LATEST_STABLE')
        self.assertEqual(self.setting["EdgeDriver"]["LinkLastReleaseFile"], edgedriver_latest_release)
        self.assertEqual(self.setting["EdgeDriver"]["LastReleasePlatform"], 'msedgedriver')
        self.assertEqual(self.setting["EdgeDriver"]["LinkCheckVersionIsValid"], "https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver?prefix={}%2F&delimiter=%2F&maxresults=100&restype=container&comp=list&_=1622714933676&timeout=60000")
        self.assertEqual(self.setting["EdgeDriver"]["LinkLatestReleaseSpecificVersion"], "https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver/LATEST_RELEASE_{}_{}")

        self.assertEqual(self.setting["PhantomJS"]["LinkLastReleaseFile"], phantomjs_latest_release)
        self.assertEqual(self.setting["PhantomJS"]["LastReleasePlatform"], 'phantomjs')
        self.assertEqual(self.setting["PhantomJS"]["LinkAllReleases"], url_release_phantomjs)

        self.assertEqual(self.setting["SafariDriver"]["LinkLastRelease"], 'https://support.apple.com/en-us/HT201222')
        self.assertEqual(self.setting["SafariDriver"]["LastReleasePlatform"], 'safaridriver')

        self.assertEqual(self.setting["ChromeBrowser"]["Path"], chrome_browser_path)
        self.assertEqual(self.setting["ChromeBrowser"]["LinkAllLatestRelease"], 'https://chromereleases.googleblog.com/search/label/Stable%20updates')
        self.assertEqual(self.setting["ChromeBrowser"]["LinkAllLatestReleaseFile"], 'https://dl.google.com/chrome/mac/universal/stable/GGRO/googlechrome.dmg')

        self.assertEqual(self.setting["FirefoxBrowser"]["Path"], firefox_browser_path)
        self.assertEqual(self.setting["FirefoxBrowser"]["LinkAllLatestReleases"], 'https://www.mozilla.org/en-US/firefox/releases/')
        self.assertEqual(self.setting["FirefoxBrowser"]["LinkAllLatestRelease"], 'https://download-installer.cdn.mozilla.net/pub/firefox/releases/{}/{}/{}/Firefox {}.{}')

        self.assertEqual(self.setting["EdgeBrowser"]["Path"], edge_browser_path)
        self.assertEqual(self.setting["EdgeBrowser"]["LinkAllLatestRelease"], 'https://docs.microsoft.com/en-us/deployedge/microsoft-edge-relnote-stable-channel')
        self.assertEqual(self.setting["EdgeBrowser"]["LinkAllLatestReleaseFile"], edge_browser_release)

        self.assertEqual(self.setting["OperaBrowser"]["Path"], opera_browser_path)
        self.assertEqual(self.setting["OperaBrowser"]["LinkAllLatestRelease"], 'https://get.geo.opera.com/pub/opera/desktop/')

        self.assertEqual(self.setting["JsonSchema"]["githubAssetSchema"], base_dir + 'schemas' + os.path.sep + 'github_asset_schema.json')
        self.assertEqual(self.setting["JsonSchema"]["githubReleaseSchema"], base_dir + 'schemas' + os.path.sep + 'github_release_schema.json')
        self.assertEqual(self.setting["JsonSchema"]["githubReleaseTagSchema"], base_dir + 'schemas' + os.path.sep + 'github_release_tag_schema.json')

        self.assertEqual(self.setting["Github"]["linkLatestReleaseBySpecificRepoName"], 'https://api.github.com/repos/{}/releases/latest')
        self.assertEqual(self.setting["Github"]["linkAllReleasesTags"], 'https://api.github.com/repos/{}/git/refs/tags')
        self.assertEqual(self.setting["Github"]["linkAllReleases"], 'https://api.github.com/repos/{}/releases')

        self.assertEqual(self.setting["PyPi"]["urlProjectJson"], 'https://pypi.python.org/pypi/selenium-driver-updater/json')

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)
    