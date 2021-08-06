# selenium_driver_updater

[![PyPI version](https://badge.fury.io/py/selenium-driver-updater.svg)](https://badge.fury.io/py/selenium-driver-updater)
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/Svinokur/selenium_driver_updater/master/LICENSE)
[![Downloads](https://pepy.tech/badge/selenium-driver-updater)](https://pepy.tech/project/selenium-driver-updater)
[![Downloads](https://pepy.tech/badge/selenium-driver-updater/month)](https://pepy.tech/project/selenium-driver-updater)
[![Downloads](https://pepy.tech/badge/selenium-driver-updater/week)](https://pepy.tech/project/selenium-driver-updater)
[![Donate with Bitcoin](https://en.cryptobadges.io/badge/micro/32GJnnDrPkSKVzrRho84KwD5RsMW4ywMiW)](https://en.cryptobadges.io/donate/32GJnnDrPkSKVzrRho84KwD5RsMW4ywMiW)
[![Donate with Ethereum](https://en.cryptobadges.io/badge/micro/0xf2691CC12a70B4589edf081E059fD4A1c457417D)](https://en.cryptobadges.io/donate/0xf2691CC12a70B4589edf081E059fD4A1c457417D)

[![Windows](https://github.com/Svinokur/selenium_driver_updater/actions/workflows/windows-tests.yml/badge.svg)](https://github.com/Svinokur/selenium_driver_updater/actions/workflows/windows-tests.yml)
[![macOS](https://github.com/Svinokur/selenium_driver_updater/actions/workflows/macOS-tests.yml/badge.svg)](https://github.com/Svinokur/selenium_driver_updater/actions/workflows/macOS-tests.yml)
[![Ubuntu](https://github.com/Svinokur/selenium_driver_updater/actions/workflows/ubuntu-tests.yml/badge.svg)](https://github.com/Svinokur/selenium_driver_updater/actions/workflows/ubuntu-tests.yml)

[![Open in Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://open.vscode.dev/Svinokur/selenium_driver_updater)

It is a fast and convenience package that can automatically download or update Selenium webdriver binaries and their browsers for different OS.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install selenium_driver_updater.

```
pip install selenium-driver-updater
```

## Usage in code
This example shows how you can use this library to download chromedriver binary.
```python
from selenium_driver_updater import DriverUpdater
import os
base_dir = os.path.dirname(os.path.abspath(__file__))

filename = DriverUpdater.install(path=base_dir, driver_name=DriverUpdater.chromedriver, upgrade=True, check_driver_is_up_to_date=True)
print(filename)

```

Or you can use library to download and update chromedriver and geckodriver binaries at the same time.
```python
from selenium_driver_updater import DriverUpdater
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
list_drivers = [DriverUpdater.chromedriver, DriverUpdater.geckodriver]

filename = DriverUpdater.install(path=base_dir, driver_name=list_drivers, upgrade=True, check_driver_is_up_to_date=True)
print(filename)

```

## Usage with help of command line
Use 
```bash
selenium-driver-updater --help
```
To see all available arguments and commands

# Supported Selenium Binaries

### ``Chromedriver`` 
#### ``DriverUpdater.chromedriver``

For installing or updating [chromedriver binary](https://chromedriver.chromium.org)

All supported OS for this driver are:

- Windows
- Linux
- MacOS
- MacOS with M1

### ``Chromium ChromeDriver`` 
#### ``DriverUpdater.chromium_chromedriver``

For installing or updating [chromium_chromedriver binary](https://chromedriver.chromium.org)

All supported OS's for this driver are:

- Linux

### ``Geckodriver`` 
#### ``DriverUpdater.geckodriver``

For installing or updating [geckodriver binary](https://github.com/mozilla/geckodriver/releases)

All supported OS's for this driver are:

- Windows
- Linux
- MacOS
- MacOS with M1

### ``Operadriver`` 
#### ``DriverUpdater.operadriver``

For installing or updating [operadriver binary](https://github.com/operasoftware/operachromiumdriver)

All supported OS's for this driver are:

- Windows
- Linux
- MacOS

### ``Edgedriver`` 
#### ``DriverUpdater.edgedriver``

For installing or updating [edgedriver binary](https://developer.microsoft.com/ru-ru/microsoft-edge/tools/webdriver/)

All supported OS's for this driver are:

- Windows
- MacOS
- Linux
- ARM

### ``PhantomJS`` 
#### ``DriverUpdater.phantomjs``

For installing or updating [phantomjs binary](https://phantomjs.org/)

All supported OS's for this driver are:

- Windows
- MacOS
- Linux

# Supported browsers for updates

### ``Chrome Browser``

For updating [chrome browser](https://www.google.com/chrome/)

All supported OS's for this browser are:

- Windows
- MacOS
- Linux (Tested on Ubuntu 20.04)

### ``Chromium Browser``

For updating [chromium browser](https://www.chromium.org/getting-involved/download-chromium)

All supported OS's for this browser are:

- Linux (Tested on Ubuntu 20.04)

### ``Firefox Browser``

For updating [firefox browser](https://www.mozilla.org/en-US/firefox/)

All supported OS's for this browser are:

- Windows
- MacOS
- Linux (Tested on Ubuntu 20.04)

### ``Opera Browser``

For updating [opera browser](https://www.opera.com)

All supported OS's for this browser are:

- Windows
- MacOS
- Linux (Tested on Ubuntu 20.04)

### ``Edge Browser``

For updating [edge browser](https://www.microsoft.com/en-us/edge)

All supported OS's for this browser are:

- Windows
- MacOS
