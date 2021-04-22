from setuptools import setup

with open('README.md') as f:
    long_description = f.read()
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='selenium_driver_updater',
  version='1.4.0',
  description='Download or update your Selenium driver binaries automatically with this package',
  long_description=long_description,
  long_description_content_type='text/markdown', 
  url='https://github.com/Svinokur/selenium_driver_updater',  
  author='Stanislav Vinokur',
  author_email='stasvinokur@yahoo.com',
  license='MIT', 
  classifiers=classifiers,
  keywords=['chromedriver', 'operadriver', 'edgedriver', 'safaridriver', 'selenium', 'seleniumdriver', 'chromedriver-binary', 'selenium-binary', 'selenium-python'],
  packages=['selenium_driver_updater'],
  install_requires=['wget', 'requests', 'selenium', 'beautifulsoup4', 'lxml', 'msedge-selenium-tools'] 
)