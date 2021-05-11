import os
import platform

base_dir = os.path.dirname(os.path.abspath(__file__)) + os.path.sep

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



setting = dict(
    {
        "Program":
        {
            'version'   : '2.10.1',
        },
        "ChromeDriver":
        {   
            "LinkLastRelease"                   : "https://chromedriver.storage.googleapis.com/LATEST_RELEASE",
            "LinkLastReleaseFile"               : chromedriver_latest_release,
            "LastReleasePlatform"               : chromedriver_platform_release,
            "LinkLatestReleaseSpecificVersion"  : "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{}",
        },
        "GeckoDriver":
        {
            "LinkLastRelease"           : 'https://api.github.com/repos/mozilla/geckodriver/releases/latest',
            "LinkLastReleasePlatform"   : geckodriver_platform_release,
            "LastReleasePlatform"       : geckodriver_platform_last_release,
            "LinkAllReleases"           : 'https://api.github.com/repos/mozilla/geckodriver/releases',
        },
        "OperaDriver":
        {
            "LinkLastRelease"           : 'https://api.github.com/repos/operasoftware/operachromiumdriver/releases/latest',
            "LinkLastReleasePlatform"   : operadriver_latest_release, 
            "LastReleasePlatform"       : operadriver_platform_release, 
            "LinkAllReleases"           : 'https://api.github.com/repos/operasoftware/operachromiumdriver/releases',
            "NamePlatformRelease"       : operadriver_name_platform_release,
        },
        "EdgeDriver":
        {
            "LinkLastRelease"           : 'https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/',
            "LinkLastReleaseFile"       : edgedriver_latest_release, 
            "LastReleasePlatform"       : edgedriver_platform_release,
        },
        "ChromeBrowser":
        {
            "LinkAllLatestRelease"      : 'https://chromereleases.googleblog.com',
            'ChromeBrowserUpdater'      : chrome_browser_updater,
            'ChromeBrowserUpdaterPath'  : chrome_browser_updater_path,
        },
        "FirefoxBrowser":
        {
            "LinkAllLatestReleases"     : 'https://www.mozilla.org/en-US/firefox/releases/',
            'FirefoxBrowserUpdater'      : firefox_browser_updater,
            'FirefoxBrowserUpdaterPath'  : firefox_browser_updater_path,
        },
        "EdgeBrowser":
        {
            "LinkAllLatestRelease"          : 'https://docs.microsoft.com/en-us/deployedge/microsoft-edge-relnote-stable-channel',
            'EdgeBrowserUpdater'            : edge_browser_updater,
            'EdgeBrowserUpdaterPath'        : edge_browser_updater_path,
        },
        "OperaBrowser":
        {
            'LinkAllReleases'               : 'https://blogs.opera.com/desktop/?s=changelog',
            "LinkSpecificReleaseChangelog"  : 'https://blogs.opera.com/desktop/changelog-for-{}/',
            "OperaBrowserUpdater"           : opera_browser_updater,
            'OperaBrowserUpdaterPath'       : opera_browser_updater_path,
        },
        "JsonSchema":
        {
            "githubAssetSchema"     : base_dir + 'schemas' + os.path.sep + 'github_asset_schema.json',
            "githubReleaseSchema"   : base_dir + 'schemas' + os.path.sep + 'github_release_schema.json',
        },
        "Github":
        {
            "linkLatestReleaseBySpecificRepoName"   : 'https://api.github.com/repos/{}/releases/latest',
            "linkAllReleasesBySpecificRepoName"     : 'https://api.github.com/repos/{}/releases',
        },
        "PyPi":
        {
            'urlProjectJson'    : 'https://pypi.python.org/pypi/selenium-driver-updater/json',
        },
    }
)