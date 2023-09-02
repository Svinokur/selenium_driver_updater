#pylint: disable=invalid-name
#Standart library imports
import os
import platform

base_dir = os.path.dirname(os.path.abspath(__file__)) + os.path.sep

os_bit = platform.architecture()[0][:-3]

latest_release = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{}/"

chromedriver_latest_release =   f"win{os_bit}/" + f"chromedriver-win{os_bit}.zip" if platform.system() == 'Windows' else\
                                "linux64/" + "chromedriver-linux64.zip" if platform.system() == "Linux" else\
                                "mac-arm64/" + "chromedriver-mac-arm64.zip" if 'arm' in str(os.uname().machine)\
                                and platform.system() == 'Darwin' else\
                                "mac-x64/" + "chromedriver-mac-x64.zip"
chromedriver_latest_release = latest_release + chromedriver_latest_release


latest_release_geckodriver = 'https://github.com/mozilla/geckodriver/releases/download/v{}/'
geckodriver_platform_release =  "geckodriver-v{}-" + f"win{os_bit}.zip" if platform.system() == 'Windows' and not 'arm' in platform.processor().lower() else\
                                "geckodriver-v{}-" + "win-aarch64.zip" if platform.system() == 'Windows' and 'arm' in platform.processor().lower() else\
                                "geckodriver-v{}-" + f"linux{os_bit}.tar.gz" if platform.system() == "Linux" and not 'arm' in platform.processor().lower() else\
                                "geckodriver-v{}-" + f"linux-aarch64.tar.gz" if platform.system() == "Linux" and 'arm' in platform.processor().lower() else\
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
edgedriver_latest_release =     f"edgedriver_win{os_bit}.zip" if platform.system() == 'Windows' and not 'arm' in platform.processor().lower() else\
                                "edgedriver_mac64.zip" if platform.system() == 'Darwin' and not 'arm' in str(os.uname().machine) else\
                                "edgedriver_mac64_m1.zip" if platform.system() == 'Darwin' and 'arm' in str(os.uname().machine) else\
                                "edgedriver_linux64.zip" if platform.system() == 'Linux' else\
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

chrome_browser_path = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
"/Applications/Chromium.app/Contents/MacOS/Chromium"] if platform.system() == 'Darwin' else \
['reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
r'reg query "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome" /v version'] if platform.system() == 'Windows' else \
"google-chrome-stable" if platform.system() == 'Linux' else ''


firefox_browser_path = '/Applications/Firefox.app/Contents/MacOS/firefox' if platform.system() == 'Darwin' else \
['reg query "HKEY_CURRENT_USER\Software\Mozilla\Mozilla Firefox" /v CurrentVersion',
'reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Mozilla\Mozilla Firefox" /v CurrentVersion',
r"Powershell (Get-Item (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe').'(Default)').VersionInfo.ProductVersion"] if platform.system() == 'Windows' else\
"firefox" if platform.system() == 'Linux' else ''



edge_browser_path = '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge' if platform.system() == 'Darwin' else\
'reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Edge\BLBeacon" /v version' if platform.system() == 'Windows' else ''

edge_browser_release = 'https://go.microsoft.com/fwlink/?linkid=2069148&platform=Mac&Consent=1&channel=Stable' if platform.system() == 'Darwin' and not 'arm' in str(os.uname().machine) else \
                        'https://go.microsoft.com/fwlink/?linkid=2093504&platform=Mac&Consent=1&channel=Stable' if platform.system() == 'Darwin' and 'arm' in str(os.uname().machine) else ''  


opera_browser_path = r'reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall" /f Opera' if platform.system() == 'Windows' else \
'/Applications/Opera.app/Contents/MacOS/Opera' if platform.system() == 'Darwin' else\
"opera" if platform.system() == 'Linux' else ''

from dataclasses import dataclass

@dataclass
class info:
    version = "6.0.0"

setting = dict(
    {
        "Program":
        {
            'version'                   : info.version,
            'wedriverVersionPattern'    : r'([0-9.]*\.[0-9]+)',
            'driversPath'               : base_dir + 'test' + os.path.sep + 'drivers' + os.path.sep,
            'DriversFileFormat'         : ".exe" if platform.system() == 'Windows' else '',
            'OSBitness'                 : os_bit,
        },
        "ChromeDriver":
        {
            "LinkLastRelease"                   : "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json",
            "LinkLastReleaseFile"               : chromedriver_latest_release,
            "LastReleasePlatform"               : 'chromedriver',
            "LinkLatestReleaseSpecificVersion"  : "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{}",
            "LinkCheckVersionIsValid"           : "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json",
        },
        "GeckoDriver":
        {
            "LinkLastReleasePlatform"   : geckodriver_platform_release,
            "LastReleasePlatform"       : 'geckodriver',
        },
        "OperaDriver":
        {
            "LinkLastReleasePlatform"   : operadriver_latest_release,
            "LastReleasePlatform"       : 'operadriver',
        },
        "EdgeDriver":
        {
            "LinkLastRelease"                   : 'https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver/LATEST_STABLE',
            "LinkLastReleaseFile"               : edgedriver_latest_release,
            "LastReleasePlatform"               : 'msedgedriver',
            "LinkCheckVersionIsValid"           : "https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver?prefix={}%2F&delimiter=%2F&maxresults=100&restype=container&comp=list&_=1622714933676&timeout=60000",
            "LinkLatestReleaseSpecificVersion"  : "https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver/LATEST_RELEASE_{}_{}",
        },
        "PhantomJS":
        {
            "LinkLastReleaseFile"   : phantomjs_latest_release,
            "LastReleasePlatform"   : 'phantomjs',
            "LinkAllReleases"       : url_release_phantomjs,
        },
        "SafariDriver":
        {   
            "LinkLastRelease"       : 'https://support.apple.com/en-us/HT201222',
            "LastReleasePlatform"   : 'safaridriver',
        },
        "ChromeBrowser":
        {
            "Path"                      : chrome_browser_path,
            "LinkAllLatestRelease"      : 'https://chromereleases.googleblog.com/search/label/Stable%20updates',
            "LinkAllLatestReleaseFile"  : 'https://dl.google.com/chrome/mac/universal/stable/GGRO/googlechrome.dmg',
        },
        "FirefoxBrowser":
        {
            "Path"                          : firefox_browser_path,
            "LinkAllLatestReleases"         : 'https://www.mozilla.org/en-US/firefox/releases/',
            "LinkAllLatestRelease"          : 'https://download-installer.cdn.mozilla.net/pub/firefox/releases/{}/{}/{}/Firefox {}.{}',
        },
        "EdgeBrowser":
        {
            "Path"                          : edge_browser_path,
            "LinkAllLatestRelease"          : 'https://docs.microsoft.com/en-us/deployedge/microsoft-edge-relnote-stable-channel',
            "LinkAllLatestReleaseFile"      : edge_browser_release,
        },
        "OperaBrowser":
        {
            "Path"                          : opera_browser_path,
            "LinkAllLatestRelease"          : 'https://get.geo.opera.com/pub/opera/desktop/',
        },
        "JsonSchema":
        {
            "githubAssetSchema"         : base_dir + 'schemas' + os.path.sep + 'github_asset_schema.json',
            "githubReleaseSchema"       : base_dir + 'schemas' + os.path.sep + 'github_release_schema.json',
            "githubReleaseTagSchema"    : base_dir + 'schemas' + os.path.sep + 'github_release_tag_schema.json',
        },
        "Github":
        {
            "linkLatestReleaseBySpecificRepoName"   : 'https://api.github.com/repos/{}/releases/latest',
            "linkAllReleasesTags"                   : 'https://api.github.com/repos/{}/git/refs/tags',
            "linkAllReleases"                       : 'https://api.github.com/repos/{}/releases',
        },
        "PyPi":
        {
            'urlProjectJson'    : 'https://pypi.python.org/pypi/selenium-driver-updater/json',
        },
    }
)
