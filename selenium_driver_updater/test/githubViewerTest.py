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

# Local imports
from util.github_viewer import GithubViewer

from _setting import setting

logging.basicConfig(level=logging.INFO)

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
    def test01_check_get_latest_release_data_by_repo_name_failure(self):
        result, message, json_data = self.github_viewer.get_latest_release_data_by_repo_name(repo_name = 'mazilla/geckadruver')
        self.assertFalse(result, json_data)
        self.assertGreater(len(message), 0, len(message))
        self.assertGreaterEqual(len(json_data),0, (len(json_data)))

    #@unittest.skip('Temporary not needed')
    def test02_check_get_latest_release_data_by_repo_name_failure(self):
        result, message, json_data = self.github_viewer.get_latest_release_data_by_repo_name(repo_name = 'mazilla/geckadruver')
        self.assertFalse(result, json_data)
        self.assertGreater(len(message), 0, len(message))
        self.assertGreaterEqual(len(json_data),0, (len(json_data)))

    #@unittest.skip('Temporary not needed')
    def test03_check_get_all_releases_data_by_repo_name_failure(self):
        result, message, releases = self.github_viewer.get_all_releases_data_by_repo_name(repo_name = 'mazilla/geckadruver')
        self.assertFalse(result, releases)
        self.assertGreater(len(message), 0, len(message))
        self.assertGreaterEqual(len(releases),0, (len(releases)))

    #@unittest.skip('Temporary not needed')
    def test04_check_get_latest_release_data_by_repo_name_and_validate_json_schema(self):
        result, message, json_data = self.github_viewer.get_latest_release_data_by_repo_name(repo_name = self.repo_name)
        self.assertTrue(result, message)
        self.assertIsNotNone(json_data,json_data)
        self.assertGreater(len(json_data), 0, len(json_data))

        schema_asset = json.loads(Path(self.setting["JsonSchema"]["githubAssetSchema"]).read_text(encoding='utf-8'))

        for asset in json_data.get('assets'):
            self.assertIsNone(jsonschema.validate(instance=asset, schema=schema_asset))

        del json_data['assets']

        self.assertIsNone(json_data.get('assets'), json_data)

        schema_release = json.loads(Path(self.setting["JsonSchema"]["githubReleaseSchema"]).read_text(encoding='utf-8'))

        self.assertIsNone(jsonschema.validate(instance=json_data, schema=schema_release))

    #@unittest.skip('Temporary not needed')
    def test05_check_get_latest_release_tag_by_repo_name(self):
        result, message, json_data = self.github_viewer.get_latest_release_tag_by_repo_name(repo_name = self.repo_name)
        self.assertTrue(result, message)
        self.assertIsNotNone(json_data,json_data)
        self.assertGreater(len(json_data), 0, len(json_data))

        schema = json.loads(Path(self.setting["JsonSchema"]["githubReleaseTagSchema"]).read_text(encoding='utf-8'))

        self.assertIsNone(jsonschema.validate(instance=json_data, schema=schema))

    #@unittest.skip('Temporary not needed')
    def test06_check_get_all_releases_data_by_repo_name_and_validate_json_schema(self):
        result, message, releases = self.github_viewer.get_all_releases_data_by_repo_name(repo_name = self.repo_name)
        self.assertTrue(result, message)
        self.assertIsNotNone(releases,releases)
        self.assertGreater(len(releases), 0, len(releases))

        schema = json.loads(Path(self.setting["JsonSchema"]["githubReleaseSchema"]).read_text(encoding='utf-8'))

        for release in releases:
            self.assertIsNone(jsonschema.validate(instance=release, schema=schema))

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)
    