import os
import platform

os_bit = platform.machine()[-2:]

latest_release = 'https://chromedriver.storage.googleapis.com/{}/'

chromedriver_latest_release =   latest_release + "chromedriver_win32.zip" if platform.system() == 'Windows' else\
                                latest_release + "chromedriver_linux64.zip" if platform.system() == "Linux" else\
                                latest_release + "chromedriver_mac64_m1.zip" if 'ARM' in str(os.uname()) and platform.system() == 'Darwin' else\
                                latest_release + "chromedriver_mac64.zip"

latest_release_geckodriver = 'https://api.github.com/repos/mozilla/geckodriver/releases/latest'

geckodriver_platform_release = f"win{os_bit}" if platform.system() == 'Windows' else\
                    f"linux{os_bit}" if platform.system() == "Linux" else\
                    "macos-aarch64" if 'ARM64' in str(os.uname()) else\
                    "macos"

latest_release_operadriver = 'https://api.github.com/repos/operasoftware/operachromiumdriver/releases/latest'

operadriver_latest_release =    f"operadriver_win{os_bit}.zip" if platform.system() == 'Windows' else\
                                "operadriver_linux64.zip" if platform.system() == "Linux" else\
                                "operadriver_mac64.zip"

latest_release_edgedriver = 'https://msedgedriver.azureedge.net/{}/'
edgedriver_latest_release =     latest_release_edgedriver + f"edgedriver_win{os_bit}.zip" if platform.system() == 'Windows' else\
                                latest_release_edgedriver + "edgedriver_linux64.zip" if platform.system() == "Linux" else\
                                latest_release_edgedriver + "edgedriver_mac64.zip" if platform.system() == 'Darwin' else\
                                latest_release_edgedriver + "edgedriver_arm64.zip"



setting = dict(
    {
        "ChromeDriver":
        {   
            "LinkLastRelease"       : "https://chromedriver.storage.googleapis.com/LATEST_RELEASE",
            "LinkLastReleaseFile"   : chromedriver_latest_release,
        },
        "GeckoDriver":
        {
            "LinkLastRelease"           : latest_release_geckodriver,
            "LinkLastReleasePlatform"   : geckodriver_platform_release,
        },
        "OperaDriver":
        {
            "LinkLastRelease"           : latest_release_operadriver,
            "LinkLastReleasePlatform"   : operadriver_latest_release, 
        },
        "EdgeDriver":
        {
            "LinkLastRelease"           : 'https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/',
            "LinkLastReleaseFile"       : edgedriver_latest_release, 
        }
    }
)