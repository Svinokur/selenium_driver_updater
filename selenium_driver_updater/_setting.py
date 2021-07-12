import os
import platform

#pylint: disable=invalid-name
base_dir = os.path.dirname(os.path.abspath(__file__)) + os.path.sep

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
operadriver_latest_release += latest_release_operadriver + operadriver_latest_release

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
'reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Mozilla\Mozilla Firefox" /v CurrentVersion'] if platform.system() == 'Windows' else\
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

from dataclasses import dataclass

@dataclass
class info:
    version = "4.1.2"

setting = dict(
    {
        "Program":
        {
            'version'                   : info.version,
            'wedriverVersionPattern'    : r'([0-9.]*\.[0-9]+)',
            'driversPath'               : base_dir + 'test' + os.path.sep + 'drivers' + os.path.sep,
            'DriversFileFormat'         : ".exe" if platform.system() == 'Windows' else '',
        },
        "ChromeDriver":
        {
            "LinkLastRelease"                   : "https://chromedriver.storage.googleapis.com/LATEST_RELEASE",
            "LinkLastReleaseFile"               : chromedriver_latest_release,
            "LastReleasePlatform"               : 'chromedriver',
            "LinkLatestReleaseSpecificVersion"  : "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{}",
            "LinkCheckVersionIsValid"           : "https://chromedriver.storage.googleapis.com/?delimiter=/&prefix={}/",
        },
        "GeckoDriver":
        {
            "LinkLastRelease"           : 'https://api.github.com/repos/mozilla/geckodriver/releases/latest',
            "LinkLastReleasePlatform"   : geckodriver_platform_release,
            "LastReleasePlatform"       : 'geckodriver',
        },
        "OperaDriver":
        {
            "LinkLastRelease"           : 'https://api.github.com/repos/operasoftware/operachromiumdriver/releases/latest',
            "LinkLastReleasePlatform"   : operadriver_latest_release,
            "LastReleasePlatform"       : 'operadriver',
        },
        "EdgeDriver":
        {
            "LinkLastRelease"                   : 'https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver/LATEST_STABLE',
            "LinkLastReleaseFile"               : edgedriver_latest_release,
            "LastReleasePlatform"               : 'msedgedriver',
            "LinkCheckVersionIsValid"           : "https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver?prefix={}%2F&delimiter=%2F&maxresults=100&restype=container&comp=list&_=1622714933676&timeout=60000",
            "LinkLatestReleaseSpecificVersion"  : "https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver/LATEST_RELEASE_{}",
        },
        "ChromiumChromeDriver":
        {
            'ChromiumChromeDriverUpdater'    : chromiumchromedriver_updater,
        },
        "PhantomJS":
        {
            "LinkLastReleaseFile"   : phantomjs_latest_release,
            "LastReleasePlatform"   : 'phantomjs',
            "LinkAllReleases"       : url_release_phantomjs,
        },
        "ChromeBrowser":
        {
            "Path"                      : chrome_browser_path,
            "LinkAllLatestRelease"      : 'https://chromereleases.googleblog.com/search/label/Stable%20updates',
            'ChromeBrowserUpdater'      : chrome_browser_updater,
            'ChromeBrowserUpdaterPath'  : chrome_browser_updater_path,
        },
        "FirefoxBrowser":
        {
            "Path"                          : firefox_browser_path,
            "LinkAllLatestReleases"         : 'https://www.mozilla.org/en-US/firefox/releases/',
            'FirefoxBrowserUpdater'         : firefox_browser_updater,
            'FirefoxBrowserUpdaterPath'     : firefox_browser_updater_path,
        },
        "EdgeBrowser":
        {
            "Path"                          : edge_browser_path,
            "LinkAllLatestRelease"          : 'https://docs.microsoft.com/en-us/deployedge/microsoft-edge-relnote-stable-channel',
            'EdgeBrowserUpdater'            : edge_browser_updater,
            'EdgeBrowserUpdaterPath'        : edge_browser_updater_path,
        },
        "OperaBrowser":
        {
            "Path"                          : opera_browser_path,
            'LinkAllReleases'               : 'https://blogs.opera.com/desktop/?s=Stable+update',
            "LinkSpecificReleaseChangelog"  : 'https://blogs.opera.com/desktop/changelog-for-{}/',
            "OperaBrowserUpdater"           : opera_browser_updater,
            'OperaBrowserUpdaterPath'       : opera_browser_updater_path,
        },
        "ChromiumBrowser":
        {
            "Path"                      : chromiumbrowser_path,
            'ChromiumBrowserUpdater'    : chromiumbrowser_updater,
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
