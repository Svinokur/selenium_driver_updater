from typing import Any, Tuple
import traceback
import logging

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from _setting import setting
from util.requests_getter import RequestsGetter

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

            result, message, status_code, json_data = RequestsGetter.get_result_by_request(url=url, is_json=True)
            if not result:
                logging.error(message)
                return result, message, json_data

            result_run = True

        except:

            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, json_data

    @staticmethod
    def get_latest_release_tag_by_repo_name(repo_name : str) -> Tuple[bool, str, Any]:
        """Gets latest release tag by github repository name

        Args:
            repo_name (str): Repository name on github. Something like operasoftware/operachromiumdriver

        Returns:
            Tuple of bool, str and Any

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            json_data               : Latest release tag.
        """

        result_run : bool = False
        message_run : str = '' 
        url : str = setting["Github"]["linkAllReleasesTags"].format(repo_name)
        json_data : Any = ''

        try:

            result, message, status_code, json_data = RequestsGetter.get_result_by_request(url=url, is_json=True)
            if not result:
                logging.error(message)
                return result, message, json_data

            json_data = json_data[len(json_data)-1]

            result_run = True

        except:

            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, json_data
    
    @staticmethod
    def get_all_releases_tags_by_repo_name(repo_name : str) -> Tuple[bool, str, Any]:
        """Gets all releases tags by github repository name

        Args:
            repo_name (str): Repository name on github. Something like operasoftware/operachromiumdriver

        Returns:
            Tuple of bool, str and Any

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            json_data               : Latest release tag.
        """

        result_run : bool = False
        message_run : str = '' 
        url : str = setting["Github"]["linkAllReleasesTags"].format(repo_name)
        json_data : Any = ''

        try:

            result, message, status_code, json_data = RequestsGetter.get_result_by_request(url=url, is_json=True)
            if not result:
                logging.error(message)
                return result, message, json_data

            result_run = True

        except:

            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, json_data

    @staticmethod
    def get_all_releases_data_by_repo_name(repo_name : str) -> Tuple[bool, str, Any]:
        """Gets all releases data by github repository name

        Args:
            repo_name (str): Repository name on github. Something like operasoftware/operachromiumdriver

        Returns:
            Tuple of bool, str and Any

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            json_data               : All releases data.
        """

        result_run : bool = False
        message_run : str = '' 
        url : str = setting["Github"]["linkAllReleases"].format(repo_name)
        json_data : Any = ''

        try:

            result, message, status_code, json_data = RequestsGetter.get_result_by_request(url=url, is_json=True)
            if not result:
                logging.error(message)
                return result, message, json_data

            result_run = True

        except:

            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, json_data