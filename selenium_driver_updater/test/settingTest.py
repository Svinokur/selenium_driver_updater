import unittest
import sys
import time
import platform
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from _setting import setting

os_bit = platform.architecture()[0][:-3]

latest_release = 'https://chromedriver.storage.googleapis.com/{}/'

chromedriver_latest_release =   latest_release + "chromedriver_win32.zip" if platform.system() == 'Windows' else\
                                latest_release + "chromedriver_linux64.zip" if platform.system() == "Linux" else\
                                latest_release + "chromedriver_mac64_m1.zip" if 'ARM' in str(os.uname()) and platform.system() == 'Darwin' else\
                                latest_release + "chromedriver_mac64.zip"

chromedriver_platform_release = "chromedriver.exe" if platform.system() == 'Windows' else\
                                "chromedriver"

latest_release_geckodriver = 'https://api.github.com/repos/mozilla/geckodriver/releases/latest'

geckodriver_platform_release = f"win{os_bit}" if platform.system() == 'Windows' else\
                    f"linux{os_bit}" if platform.system() == "Linux" else\
                    "macos-aarch64" if 'ARM64' in str(os.uname()) else\
                    "macos"

geckodriver_platform_last_release = "geckodriver.exe" if platform.system() == 'Windows' else\
                                "geckodriver"

latest_release_operadriver = 'https://api.github.com/repos/operasoftware/operachromiumdriver/releases/latest'

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

chrome_browser_updater = fr'"C:\Program Files (x86)\Google\Update\GoogleUpdate.exe"' if platform.system() == 'Windows' else ''

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
        self.assertEqual(len(self.setting), 5)

    #@unittest.skip('Temporary not needed')
    def test02_checkCountParams(self):
        self.assertEqual(len(self.setting["ChromeDriver"]), 3)
        self.assertEqual(len(self.setting["GeckoDriver"]), 4)
        self.assertEqual(len(self.setting["OperaDriver"]), 4)
        self.assertEqual(len(self.setting["EdgeDriver"]), 3)
        self.assertEqual(len(self.setting["ChromeBrowser"]), 2)
    
    #@unittest.skip('Temporary not needed')
    def test03_checkValuesParams(self):

        self.assertEqual(self.setting["ChromeDriver"]["LinkLastRelease"], "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
        self.assertEqual(self.setting["ChromeDriver"]["LinkLastReleaseFile"], chromedriver_latest_release)
        self.assertEqual(self.setting["ChromeDriver"]["LastReleasePlatform"], chromedriver_platform_release)

        self.assertEqual(self.setting["GeckoDriver"]["LinkLastRelease"], latest_release_geckodriver)
        self.assertEqual(self.setting["GeckoDriver"]["LinkLastReleasePlatform"], geckodriver_platform_release)
        self.assertEqual(self.setting["GeckoDriver"]["LastReleasePlatform"], geckodriver_platform_last_release)
        self.assertEqual(self.setting["GeckoDriver"]["LinkAllReleases"], 'https://api.github.com/repos/mozilla/geckodriver/releases')

        self.assertEqual(self.setting["OperaDriver"]["LinkLastRelease"], latest_release_operadriver)
        self.assertEqual(self.setting["OperaDriver"]["LinkLastReleasePlatform"], operadriver_latest_release)
        self.assertEqual(self.setting["OperaDriver"]["LastReleasePlatform"], operadriver_platform_release)
        self.assertEqual(self.setting["OperaDriver"]["LinkAllReleases"], 'https://api.github.com/repos/operasoftware/operachromiumdriver/releases')

        self.assertEqual(self.setting["EdgeDriver"]["LinkLastRelease"], 'https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/')
        self.assertEqual(self.setting["EdgeDriver"]["LinkLastReleaseFile"], edgedriver_latest_release)
        self.assertEqual(self.setting["EdgeDriver"]["LastReleasePlatform"], edgedriver_platform_release)

        self.assertEqual(self.setting["ChromeBrowser"]["LinkAllLatestRelease"], 'https://chromereleases.googleblog.com')
        self.assertEqual(self.setting["ChromeBrowser"]["ChromeBrowserUpdater"], chrome_browser_updater)

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)