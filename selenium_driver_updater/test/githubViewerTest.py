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

class testGithubViewer(unittest.TestCase): 
    """Class for unit-testing GithubViewer class

    Attributes:
        github_viewer               : Initialize class GithubViewer
        repo_name (str)             : Repository name of geckodriver
        specific_version (str)      : Specific version of geckodriver to test
        specific_asset_name (str)   : Specific asset name of geckodriver to test
        startTime (float)           : Time of starting unit-tests
    """

    def setUp(self):
        self.github_viewer = GithubViewer
        self.repo_name : str = 'mozilla/geckodriver'
        self.specific_version : str = '0.29.0'
        self.specific_asset_name : str = 'win64'

        self.startTime : float = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_latest_release_data_by_repo_name(self):
        result, message, json_data = GithubViewer.get_latest_release_data_by_repo_name(repo_name = self.repo_name)
        self.assertTrue(result, message)
        self.assertIsNotNone(json_data,json_data)
        self.assertGreater(len(json_data), 0, len(json_data))
    
    #@unittest.skip('Temporary not needed')
    def test02_check_get_latest_release_data_by_repo_name_and_validate_json_schema(self):
        result, message, json_data = GithubViewer.get_specific_asset_by_repo_name(asset_name = self.specific_asset_name, 
        repo_name=self.repo_name)
        self.assertTrue(result, message)
        self.assertIsNotNone(json_data,json_data)
        self.assertGreater(len(json_data), 0, len(json_data))

        with open(setting["JsonSchema"]["githubAssetSchema"], 'r', encoding='utf-8') as schema_file:
            schema = json.loads(schema_file.read())
        
        self.assertIsNone(jsonschema.validate(instance=json_data[0].get('asset'), schema=schema))

    #@unittest.skip('Temporary not needed')
    def test03_check_get_specific_asset_by_specific_version_by_repo_name_and_validate_json_schema(self):
        result, message, json_data = GithubViewer.get_specific_asset_by_specific_version_by_repo_name(version = self.specific_version, 
        asset_name = self.specific_asset_name, repo_name=self.repo_name)
        self.assertTrue(result, message)
        self.assertIsNotNone(json_data,json_data)
        self.assertGreater(len(json_data), 0, len(json_data))
        self.assertEqual(json_data[0].get('version'), self.specific_version, json_data[0].get('version'))
        self.assertIn(self.specific_asset_name, json_data[0].get('asset').get('name'), json_data[0].get('asset').get('name'))

        with open(setting["JsonSchema"]["githubAssetSchema"], 'r', encoding='utf-8') as schema_file:
            schema = json.loads(schema_file.read())
        
        self.assertIsNone(jsonschema.validate(instance=json_data[0].get('asset'), schema=schema))

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)