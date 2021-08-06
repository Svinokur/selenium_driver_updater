#Standart library imports
import unittest
import time
import jsonschema
import json
from pathlib import Path
from typing import Any
import logging

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))

# Local imports
from selenium_driver_updater.util.github_viewer import GithubViewer

from selenium_driver_updater._setting import setting

logging.basicConfig(level=logging.INFO)

from selenium_driver_updater.util.exceptions import StatusCodeNotEqualException

# pylint: disable=missing-function-docstring
class testGithubViewer(unittest.TestCase): 
    """Class for unit-testing GithubViewer class

    Attributes:
        github_viewer               : Initialize class GithubViewer
        repo_name (str)             : Repository name of geckodriver
        specific_version (str)      : Specific version of geckodriver to test
        specific_asset_name (str)   : Specific asset name of geckodriver to test
        startTime (float)           : Time of starting unit-tests
    """

    @classmethod
    def setUpClass(cls):
        cls.setting : Any = setting
        cls.github_viewer = GithubViewer

    def setUp(self):
        self.repo_name : str = 'mozilla/geckodriver'
        self.specific_version : str = '0.29.0'
        self.specific_asset_name : str = 'win64'

        self.start_time : float = time.time()

    def tearDown(self):
        end_time = time.time() - self.start_time
        print("%.3f" % end_time)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_all_releases_data_by_repo_name_failure(self):
        try:
            releases = self.github_viewer.get_all_releases_data_by_repo_name(repo_name = 'mazilla/geckadruver')
            self.assertGreaterEqual(len(releases),0, (len(releases)))
        except Exception as error:
            self.assertTrue(error.__class__ == StatusCodeNotEqualException, error.__class__)

    #@unittest.skip('Temporary not needed')
    def test02_check_get_latest_release_tag_by_repo_name_failure(self):
        try:
            tag = self.github_viewer.get_latest_release_tag_by_repo_name(repo_name = 'mazilla/geckadruver')
            self.assertGreaterEqual(len(tag), 0, len(tag))
        except Exception as error:
            self.assertTrue(error.__class__ == StatusCodeNotEqualException, error.__class__)

    #@unittest.skip('Temporary not needed')
    def test03_check_get_release_version_by_repo_name_failure(self):
        try:
            version = self.github_viewer.get_release_version_by_repo_name(repo_name = 'mazilla/geckadruver')
            self.assertGreaterEqual(len(version), 0, len(version))
        except Exception as error:
            self.assertTrue(error.__class__ == StatusCodeNotEqualException, error.__class__)

    #@unittest.skip('Temporary not needed')
    def test04_check_get_all_releases_data_by_repo_name_and_validate_json_schema(self):
        releases = self.github_viewer.get_all_releases_data_by_repo_name(repo_name = self.repo_name)
        self.assertIsNotNone(releases,releases)
        self.assertGreater(len(releases), 0, len(releases))

        schema = json.loads(Path(self.setting["JsonSchema"]["githubReleaseSchema"]).read_text(encoding='utf-8'))

        for release in releases:
            self.assertIsNone(jsonschema.validate(instance=release, schema=schema))

    #@unittest.skip('Temporary not needed')
    def test05_check_get_latest_release_tag_by_repo_name(self):
        tag_api = self.github_viewer.get_latest_release_tag_by_repo_name(repo_name = 'ariya/phantomjs')
        self.assertIsNotNone(tag_api,tag_api)
        self.assertGreater(len(tag_api), 0, len(tag_api))

        tag_site = self.github_viewer.get_release_version_by_repo_name_via_site(repo_name = 'ariya/phantomjs')
        self.assertIsNotNone(tag_site,tag_site)
        self.assertGreater(len(tag_site), 0, len(tag_site))

        self.assertEqual(tag_api, tag_site, f'tag_api: {tag_api} is not equal to tag_api: {tag_api}')

    #@unittest.skip('Temporary not needed')
    def test06_check_get_release_version_by_repo_name(self):
        version_api = self.github_viewer.get_release_version_by_repo_name(repo_name = self.repo_name)
        self.assertGreaterEqual(len(version_api), 0, len(version_api))

        version_site = self.github_viewer.get_release_version_by_repo_name_via_site(repo_name = self.repo_name)
        self.assertGreaterEqual(len(version_site), 0, len(version_site))

        self.assertEqual(version_api, version_site, f'version_api: {version_api} is not equal to version_site: {version_site}')

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)
    