import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import logging

import traceback

from test import settingTest
from test import driverUpdaterTest

from test import chromeDriverTest
from test import chromeBrowserTest

from test import geckoDriverTest
from test import firefoxBrowserTest

from test import operaDriverTest
from test import operaBrowserTest

from test import edgeDriverTest
from test import edgeBrowserTest

from test import githubViewerTest
from test import extractorTest
from test import requestsGetterTest

from test import chromiumChromeDriverTest
from test import chromiumChromeBrowserTest

from test import phantomJSTest

import platform

#refresh logger sometimes issue with writing log file
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

base_dir = os.path.dirname(os.path.abspath(__file__)) + os.path.sep

level=logging.DEBUG
format='%(asctime)s %(name)s %(levelname)s [%(module)s %(funcName)s %(lineno)d] %(message)s '
filename=f'{base_dir}log_test.log' 
filemode='w'
encoding='utf-8'

logging.basicConfig(level=level, format=format, filename=filename, filemode=filemode, encoding=encoding)

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

    #testSuite.addTest(unittest.makeSuite(operaDriverTest.testOperaDriver)) #Temporary could not test it in Github Workflow
    #testSuite.addTest(unittest.makeSuite(operaBrowserTest.testOperaBrowser)) #Temporary could not test it in Github Workflow

    if platform.system() != 'Linux':
        testSuite.addTest(unittest.makeSuite(edgeDriverTest.testEdgeDriver))
        testSuite.addTest(unittest.makeSuite(edgeBrowserTest.testEdgeBrowser))


    #testSuite.addTest(unittest.makeSuite(chromiumChromeDriverTest.testChromiumChromeDriver)) Temporary could not test it in Github Workflow
    #testSuite.addTest(unittest.makeSuite(chromiumChromeBrowserTest.testChromiumChromeBrowser)) Temporary could not test it in Github Workflow

    testSuite.addTest(unittest.makeSuite(phantomJSTest.testPhantomJS))

    testSuite.addTest(unittest.makeSuite(githubViewerTest.testGithubViewer))
    testSuite.addTest(unittest.makeSuite(extractorTest.testExtractor))
    testSuite.addTest(unittest.makeSuite(requestsGetterTest.testRequestsGetter))


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
