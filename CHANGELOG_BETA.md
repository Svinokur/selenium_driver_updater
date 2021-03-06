## [5.1.0b6] - 31/08/2021
This version was written and tested on Python 3.9.6

### Improvements

- Returned parameter "old_return" with improved back-compatibility

### Other

- Setted default value "False" for parameter "old_return"

## [5.1.0b5] - 27/08/2021
This version was written and tested on Python 3.9.6

### Added
- Added support for edgedriver ARM version on Windows

### Improvements

- Speeded up getting latest version of safaridriver

## [5.1.0b4] - 17/08/2021
This version was written and tested on Python 3.9.6

### Added

- Added killing of browser if its getting updated
- Added full updating of opera browser on Windows (full installation instead of browser update command)

### Fixes

- Fixed an issue with incorrect default path detecting if library was ran in console mode

## [5.1.0b3] - 16/08/2021
This version was written and tested on Python 3.9.6

### Added

- Added full updating of edge browser on MacOS (full installation instead of browser update command)

## [5.1.0b2] - 14/08/2021
This version was written and tested on Python 3.9.6

### Added

- Added full updating of firefox and chrome browser on MacOS (full installation instead of browser update command)

### Fixes

- Partial fixed of getting latest version of edge browser

### Other

- Removed parameter "old_return" for returning old variables like "result and message"

## [5.1.0b1] - 12/08/2021
This version was written and tested on Python 3.9.6

### Added

- Added full updating of opera browser on MacOS (full installation instead of browser update command)

## [5.0.0b5] - 06/08/2021
This version was written and tested on Python 3.9.6

### Added

- Added alternative usage in command line (now supports selenium-driver-updater reference)

### Improvements

- Improved updating command of chrome browser

### Other

- Removed unused imports
- Removed unnecessary return after except statement

## [5.0.0b4] - 03/08/2021
This version was written and tested on Python 3.9.6

### Added

- Added base class for all driver classes
- Added support for safaridriver (not updating or downloading)
- Added properly exiting driver with context managers instead of driver.quit()

### Improvements

- Improved getting current version of chrome browser on MacOS (added additional path)

### Fixes

- Fixed an issue with incorrect getting current version of opera browser

## [5.0.0b3] - 29/07/2021
This version was written and tested on Python 3.9.6

### Added

- Added command line control
- Added alternative method of getting needed data via github if github api limit is restricted (not all methods, but many necessary)

### Fixes

- Fixed an issue if multiply identical drivers and different OS's names were given and later was incorrect filename extension checking

## [5.0.0b2] - 26/07/2021
This version was written and tested on Python 3.9.6

### Added

- Added firsts custom user-defined exceptions
- Added parameter "old_return" for returning old variables like "result and message"

### Improvements

- Improved driver version validating if specific version was given

### Fixes

- Fixed an issue with incorrect operadriver downloading

### Other

- Removed error handling pattern everywhere

## [5.0.0b1] - 25/07/2021
This version was written and tested on Python 3.9.6

### Added

- Added custom logger (No need to override root logger now)

### Improvements

- Simplified driver classes initialization
- Simplified checking for correct driver_name