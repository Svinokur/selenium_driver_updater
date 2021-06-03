import unittest

import sys
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from util.github_viewer import GithubViewer
import time
import jsonschema
import json

from _setting import setting

import logging
logging.basicConfig(level=logging.INFO)

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
        cls.setting = setting
        cls.github_viewer = GithubViewer

    def setUp(self):
        self.repo_name : str = 'mozilla/geckodriver'
        self.specific_version : str = '0.29.0'
        self.specific_asset_name : str = 'win64'

        self.startTime : float = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

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
    def test03_check_get_all_releases_tags_by_repo_name_failure(self):
        result, message, tags = self.github_viewer.get_all_releases_tags_by_repo_name(repo_name = 'mazilla/geckadruver')
        self.assertFalse(result, tags)
        self.assertGreater(len(message), 0, len(message))
        self.assertGreaterEqual(len(tags),0, (len(tags)))

    #@unittest.skip('Temporary not needed')
    def test04_check_get_all_releases_data_by_repo_name_failure(self):
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

        with open(self.setting["JsonSchema"]["githubAssetSchema"], 'r', encoding='utf-8') as schema_file:
            schema_asset = json.loads(schema_file.read())

        for asset in json_data.get('assets'):
            self.assertIsNone(jsonschema.validate(instance=asset, schema=schema_asset))

        del json_data['assets']

        self.assertIsNone(json_data.get('assets'), json_data)

        with open(self.setting["JsonSchema"]["githubReleaseSchema"], 'r', encoding='utf-8') as schema_file:
            schema_release = json.loads(schema_file.read())
        
        self.assertIsNone(jsonschema.validate(instance=json_data, schema=schema_release))

    #@unittest.skip('Temporary not needed')
    def test05_check_get_latest_release_tag_by_repo_name(self):
        result, message, json_data = self.github_viewer.get_latest_release_tag_by_repo_name(repo_name = self.repo_name)
        self.assertTrue(result, message)
        self.assertIsNotNone(json_data,json_data)
        self.assertGreater(len(json_data), 0, len(json_data))

        with open(self.setting["JsonSchema"]["githubReleaseTagSchema"], 'r', encoding='utf-8') as schema_file:
            schema = json.loads(schema_file.read())
        
        self.assertIsNone(jsonschema.validate(instance=json_data, schema=schema))

    #@unittest.skip('Temporary not needed')
    def test06_check_get_all_releases_tags_by_repo_name_and_validate_json_schema(self):
        result, message, tags = self.github_viewer.get_all_releases_tags_by_repo_name(repo_name = self.repo_name)
        self.assertTrue(result, message)
        self.assertIsNotNone(tags,tags)
        self.assertGreater(len(tags), 0, len(tags))

        with open(self.setting["JsonSchema"]["githubReleaseTagSchema"], 'r', encoding='utf-8') as schema_file:
            schema = json.loads(schema_file.read())
        
        for tag in tags:
            self.assertIsNone(jsonschema.validate(instance=tag, schema=schema))

    #@unittest.skip('Temporary not needed')
    def test07_check_get_all_releases_data_by_repo_name_and_validate_json_schema(self):
        result, message, releases = self.github_viewer.get_all_releases_data_by_repo_name(repo_name = self.repo_name)
        self.assertTrue(result, message)
        self.assertIsNotNone(releases,releases)
        self.assertGreater(len(releases), 0, len(releases))

        with open(self.setting["JsonSchema"]["githubReleaseSchema"], 'r', encoding='utf-8') as schema_file:
            schema = json.loads(schema_file.read())
        
        for release in releases:
            self.assertIsNone(jsonschema.validate(instance=release, schema=schema))

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)