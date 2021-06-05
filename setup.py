from setuptools import setup

with open('README.md') as f:
    long_description = f.read()
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3',
  'Programming Language :: Python',
]

keywords = ['chromedriver', 'operadriver', 
            'edgedriver', 'safaridriver', 
            'selenium', 'seleniumdriver', 
            'chromedriver-binary', 'selenium-binary', 
            'selenium-python', 'selenium-driver',
            'geckodriver', 'geckodriver-binary',
            'operadriver-binary', 'edgedriver-binary',
            'safaridriver-binary', 'chromebrowser', 'chrome-browser', 'firefox',
            'firefox-browser', 'selenium-update', 'selenium-updater', 'updater']
 
setup(
  name='selenium_driver_updater',
  version='3.9.0',
  description='Download or update your Selenium driver binaries and their browsers automatically with this package',
  long_description=long_description,
  long_description_content_type='text/markdown', 
  url='https://github.com/Svinokur/selenium_driver_updater',  
  author='Stanislav Vinokur',
  author_email='stasvinokur@yahoo.com',
  license='MIT', 
  classifiers=classifiers,
  keywords=keywords,
  packages=['selenium_driver_updater', 'selenium_driver_updater/util', 'selenium_driver_updater/browsers'],
  install_requires=['wget', 'requests', 'selenium', 'beautifulsoup4'] 
)