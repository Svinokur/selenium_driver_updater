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
  version='1.0.2',
  description='Download or update your chromedriver automatically with this package',
  long_description=long_description,
  long_description_content_type='text/markdown', 
  url='https://github.com/Svinokur/selenium_driver_updater',  
  author='Stanislav Vinokur',
  author_email='stasvinokur@yahoo.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='chromedriver', 
  packages=['selenium_driver_updater'],
  install_requires=['wget', 'requests'] 
)