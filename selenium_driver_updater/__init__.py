import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from .driverUpdater import DriverUpdater # pylint: disable=wrong-import-position
