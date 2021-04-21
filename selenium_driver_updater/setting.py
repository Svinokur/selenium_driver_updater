import os
import platform

latest_release = 'https://chromedriver.storage.googleapis.com/{}/'

chromedriver_latest_release =   latest_release + "chromedriver_win32.zip" if platform.system() == 'Windows' else\
                                latest_release + "chromedriver_linux64.zip" if platform.system() == "Linux" else\
                                latest_release + "chromedriver_mac64_m1.zip" if 'ARM' in str(os.uname()) and platform.system() == 'Darwin' else\
                                latest_release + "chromedriver_mac64.zip"

latest_release_geckodriver = 'https://api.github.com/repos/mozilla/geckodriver/releases/latest'

geckodriver_platform_release = "win64" if platform.system() == 'Windows' else\
                    "linux64" if platform.system() == "Linux" else\
                    "macos-aarch64" if 'ARM64' in str(os.uname()) else\
                    "macos"

latest_release_operadriver = 'https://api.github.com/repos/operasoftware/operachromiumdriver/releases/latest'

operadriver_latest_release =    "operadriver_win32.zip" if platform.system() == 'Windows' else\
                                "operadriver_linux64.zip" if platform.system() == "Linux" else\
                                "operadriver_mac64.zip"


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
        }
    }
)