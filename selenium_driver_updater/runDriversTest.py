import unittest
import os
import sys

import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

import logging

import traceback

from test import settingTest
from test import chromeDriverTest
from test import geckoDriverTest
from test import operaDriverTest
from test import edgeDriverTest

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
    testSuite.addTest(unittest.makeSuite(chromeDriverTest.testChromeDriver))
    testSuite.addTest(unittest.makeSuite(geckoDriverTest.testGeckoDriver))
    testSuite.addTest(unittest.makeSuite(operaDriverTest.testOperaDriver))
    testSuite.addTest(unittest.makeSuite(edgeDriverTest.testEdgeDriver))
    
    
    runner = unittest.TextTestRunner(verbosity=2, failfast=True)
    result = runner.run(testSuite)

    if result.wasSuccessful():

        logging.debug('OK')
   
    else:

        for failures in result.failures:
            failures = str(failures) + "\n"
            logging.error(failures)

        for errors in result.errors:
            errors = str(errors) + "\n"
            logging.error(errors)

except:
    message_run = f'Unexcepted error: {str(traceback.format_exc())}'
    logging.error(message_run)