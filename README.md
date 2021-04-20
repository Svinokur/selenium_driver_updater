# selenium_driver_updater
It is a fast and convenience package that can automatically download or update Selenium webdriver binaries for different OS.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install selenium_driver_updater.

```
pip install selenium-driver-updater
```

## Usage
This example shows how you can use this library to download chromedriver binary.
```python
from selenium_driver_updater import DriverUpdater as DU
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
du = DU(path=base_dir, driver_name=DU.chromedriver)
file_name = du.install(upgrade=True)
print(file_name)

```

# Supported Selenium Binaries

## Chromedriver (DriverUpdater.chromedriver)

- Windows
- Linux
- MacOS
- MacOS with M1

## License
[MIT](https://choosealicense.com/licenses/mit/)