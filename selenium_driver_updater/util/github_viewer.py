from typing import Any, Tuple
import requests
import traceback
import logging
import json

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from _setting import setting

class GithubViewer():

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/35.0.1916.47 Safari/537.36'

    _headers = {'User-Agent': user_agent}

    @staticmethod
    def get_latest_release_data_by_repo_name(repo_name : str) -> Tuple[bool, str, Any]:
        """Gets latest release asset by github repository name

        Args:
            repo_name (str): Repository name on github. Something like operasoftware/operachromiumdriver

        Returns:
            Tuple of bool, str and Any

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            json_data               : All latest release data.
        """

        result_run : bool = False
        message_run : str = '' 
        url : str = setting["Github"]["linkLatestReleaseBySpecificRepoName"].format(repo_name)
        json_data : Any = ''

        try:

            request = requests.get(url, headers=GithubViewer._headers)
            request_text = request.text
            status_code = request.status_code

            if status_code != 200:
                message = f'status_code not equal 200 status_code : {status_code} request_text: {request_text}'
                return result_run, message, json_data

            json_data = json.loads(str(request_text))

            result_run = True

        except:

            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, json_data
    
    @staticmethod
    def get_specific_asset_by_repo_name(asset_name : str, repo_name : str):
        """Gets specific asset by asset name and repository name

        Args:
            asset_name (str)    : Specific name of asset.
            repo_name (str)     : Repository name on github. Something like operasoftware/operachromiumdriver

        Returns:
            Tuple of bool, str and Any

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            json_data               : All gathered data.
        """

        result_run : bool = False
        message_run : str = '' 
        url : str = setting["Github"]["linkLatestReleaseBySpecificRepoName"].format(repo_name)
        data = []
        asset = ''
        is_found : bool = False
        specific_asset = []

        try:

            request = requests.get(url, headers=GithubViewer._headers)
            request_text = request.text
            status_code = request.status_code

            if status_code != 200:
                message = f'status_code not equal 200 status_code : {status_code} request_text: {request_text}'
                return result_run, message, data
                
            json_data = json.loads(str(request_text))

            version = json_data.get('name')

            for asset in json_data.get('assets'):
                asset_name_package = asset.get('name').replace('.tar', '').replace('.gz', '').replace('.zip', '').replace('.asc', '')

                if asset_name_package.endswith(asset_name):
                    is_found = True
                    specific_asset = asset
                    break

            if not is_found:
                message = f"Specific binary was not found, maybe unknown OS. asset_name: {asset_name} repo_name: {repo_name}"
                logging.error(message)
                return result_run, message, data

            data.append(dict(version=version, asset=specific_asset))

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, data

    @staticmethod
    def get_specific_asset_by_specific_version_by_repo_name(version : str, asset_name : str, repo_name : str):
        """Gets specific asset by specific release by repository name

        Args:
            version (str)       : Specific release version of asset.
            asset_name (str)    : Specific name of asset.
            repo_name (str)     : Repository name on github. Something like operasoftware/operachromiumdriver

        Returns:
            Tuple of bool, str and Any

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            json_data               : All gathered data.
        """

        result_run : bool = False
        message_run : str = '' 
        url : str = setting["Github"]["linkAllReleasesBySpecificRepoName"].format(repo_name)
        data = []
        asset = ''
        is_found : bool = False
        specific_asset = []

        try:

            request = requests.get(url=url, headers=GithubViewer._headers)
            request_text = request.text
            status_code = request.status_code

            if status_code != 200:
                message = f'status_code not equal 200 status_code : {status_code} request_text: {request_text}'
                return result_run, message, data
                
            json_data = json.loads(str(request_text))

            for release in json_data:
                if version == release.get('name') or version in release.get('tag_name'):
                    for asset in release.get('assets'):
                        asset_name_package = asset.get('name').replace('.tar', '').replace('.gz', '').replace('.zip', '').replace('.asc', '')

                        if asset_name_package.endswith(asset_name):
                            is_found = True
                            specific_asset = asset
                            break
                    break

            if not is_found:
                message = (f"Specific binary by specific release was not found, maybe unknown OS."
                            f"version: {version} asset_name: {asset_name} repo_name: {repo_name}")
                logging.error(message)
                return result_run, message, data

            data.append(dict(version=version, asset=specific_asset))

            result_run = True

        except:
            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, data