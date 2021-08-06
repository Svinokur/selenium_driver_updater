#pylint: disable=wrong-import-position,wrong-import-order
import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import logging

import traceback

from selenium_driver_updater.test import settingTest
from selenium_driver_updater.test import driverUpdaterTest

from selenium_driver_updater.test import chromeDriverTest
from selenium_driver_updater.test import chromeBrowserTest

from selenium_driver_updater.test import geckoDriverTest
from selenium_driver_updater.test import firefoxBrowserTest

from selenium_driver_updater.test import operaDriverTest
from selenium_driver_updater.test import operaBrowserTest

from selenium_driver_updater.test import edgeDriverTest
from selenium_driver_updater.test import edgeBrowserTest

from selenium_driver_updater.test import githubViewerTest
from selenium_driver_updater.test import extractorTest
from selenium_driver_updater.test import requestsGetterTest

from selenium_driver_updater.test import chromiumChromeDriverTest
from selenium_driver_updater.test import chromiumChromeBrowserTest

from selenium_driver_updater.test import phantomJSTest

from selenium_driver_updater.test import exceptionsTest

from selenium_driver_updater.test import safariDriverTest

import platform

#refresh logger sometimes issue with writing log file
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

base_dir = os.path.dirname(os.path.abspath(__file__)) + os.path.sep

LEVEL=logging.INFO
FORMAT='%(asctime)s %(name)s %(levelname)s [%(module)s %(funcName)s %(lineno)d] %(message)s '

logging.basicConfig(level=LEVEL, format=FORMAT)

#define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)

# add the handler to the root logger
logging.getLogger('').addHandler(console)

try:

    testSuite = unittest.TestSuite()
    testSuite.addTest(unittest.makeSuite(settingTest.testSetting))
    testSuite.addTest(unittest.makeSuite(driverUpdaterTest.testDriverUpdater))

    testSuite.addTest(unittest.makeSuite(chromeDriverTest.testChromeDriver))
    testSuite.addTest(unittest.makeSuite(chromeBrowserTest.testChromeBrowser))

    testSuite.addTest(unittest.makeSuite(geckoDriverTest.testGeckoDriver))
    testSuite.addTest(unittest.makeSuite(firefoxBrowserTest.testFirefoxBrowser))

    if platform.system() == 'Darwin':
        testSuite.addTest(unittest.makeSuite(operaDriverTest.testOperaDriver))
        testSuite.addTest(unittest.makeSuite(operaBrowserTest.testOperaBrowser))

    if platform.system() != 'Linux':
        testSuite.addTest(unittest.makeSuite(edgeDriverTest.testEdgeDriver))
        testSuite.addTest(unittest.makeSuite(edgeBrowserTest.testEdgeBrowser))


    #testSuite.addTest(unittest.makeSuite(chromiumChromeDriverTest.testChromiumChromeDriver))
    #testSuite.addTest(unittest.makeSuite(chromiumChromeBrowserTest.testChromiumChromeBrowser))

    testSuite.addTest(unittest.makeSuite(phantomJSTest.testPhantomJS))

    if platform.system() == 'Darwin':
        testSuite.addTest(unittest.makeSuite(safariDriverTest.testSafariDriver))

    testSuite.addTest(unittest.makeSuite(githubViewerTest.testGithubViewer))
    testSuite.addTest(unittest.makeSuite(extractorTest.testExtractor))
    testSuite.addTest(unittest.makeSuite(requestsGetterTest.testRequestsGetter))

    testSuite.addTest(unittest.makeSuite(exceptionsTest.testExceptions))


    runner = unittest.TextTestRunner(verbosity=2, failfast=True)
    result = runner.run(testSuite)

    if result.wasSuccessful():

        logging.debug('OK')

    else:

        failures = ''
        errors = ''

        for failures in result.failures:
            failures = str(failures) + "\r\n"

        logging.error(failures)

        for errors in result.errors:
            errors = str(errors) + "\r\n"

        logging.error(errors)

        sys.exit(1)

except Exception:
    message_run = f'Unexcepted error: {traceback.format_exc()}'
    logging.error(message_run)

    sys.exit(1)
