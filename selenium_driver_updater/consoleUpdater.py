#Standart library imports
import argparse

#Local imports
from selenium_driver_updater._setting import setting
from selenium_driver_updater.driverUpdater import DriverUpdater

#pylint: disable=protected-access
class ConsoleUpdater():
    """Class for working with command line of selenium driver updater library"""

    @staticmethod
    def parse_command_line():
        "Function for parsing arguments that were specified in command line"
        parser = argparse.ArgumentParser(
            description=f'Download or update your Selenium driver binaries and their browsers automatically with this package. Current version is {str(setting["Program"]["version"])}',
        )
        parser.add_argument(
        "--driver_name",
        "-d",
        action="store",
        dest="driver_name",
        metavar="F",
        help="Specified driver name/names which will be downloaded or updated",
        default='',
        required=True,
        )
        parser.add_argument(
        "--path",
        "-p",
        action="store",
        dest="path",
        metavar="F",
        help="Specified path which will used for downloading or updating Selenium driver binary. Must be folder path",
        default='',
        )
        parser.add_argument(
        "--upgrade",
        "-upg",
        action="store",
        dest="upgrade",
        metavar="F",
        help="If true, it will overwrite existing driver in the folder",
        default=False,
        )
        parser.add_argument(
        "--chmod",
        "-ch",
        action="store",
        dest="chmod",
        metavar="F",
        help="If true, it will make driver binary executable",
        default=True,
        )
        parser.add_argument(
        "--check_driver_is_up_to_date",
        "-cdr",
        action="store",
        dest="check_driver_is_up_to_date",
        metavar="F",
        help="If true, it will check driver version before and after upgrade",
        default=True,
        )
        parser.add_argument(
        "--info_messages",
        "-im",
        action="store",
        dest="info_messages",
        metavar="F",
        help="If false, it will disable all info messages",
        default=True,
        )
        parser.add_argument(
        "--filename",
        action="store",
        dest="filename",
        metavar="F",
        help="Specific name for driver. If given, it will replace name for driver",
        default='',
        )
        parser.add_argument(
        "--check_browser_is_up_to_date",
        "-cb",
        action="store",
        dest="check_browser_is_up_to_date",
        metavar="F",
        help="If true, it will check browser version before specific driver update or upgrade",
        default=False,
        )
        parser.add_argument(
        "--system_name",
        action="store",
        dest="system_name",
        metavar="F",
        help="Specific OS for driver",
        default='',
        )
        parser.add_argument("--version", action="version", version=str(setting["Program"]["version"]))
        return parser.parse_args()

    @staticmethod
    def install():
        "Main function that initializes all variables and pass it to main module (driver Updater)"

        #Initialize all variables

        args = ConsoleUpdater.parse_command_line()
        kwargs = vars(args)

        DriverUpdater.install(**kwargs)
