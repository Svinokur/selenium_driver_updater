#Standart library imports
from typing import Any, Tuple
import traceback
import logging

# Local imports
from _setting import setting
from util.requests_getter import RequestsGetter

class GithubViewer():
    """Class for working with github repositories"""

    @staticmethod
    def get_latest_release_data_by_repo_name(repo_name: str) -> Tuple[bool, str, Any]:
        """Gets latest release asset by github repository name

        Args:
            repo_name (str): Repository path on github.

        Returns:
            Tuple of bool, str and Any

            result_run (bool) : True if function passed correctly, False otherwise.
            message_run (str) : Returns an error message if an error occurs in the function.
            json_data         : All latest release data.
        """

        result_run: bool = False
        message_run: str = ''
        url: str = str(setting["Github"]["linkLatestReleaseBySpecificRepoName"]).format(repo_name)
        json_data: Any = ''

        try:

            result, message, status_code, json_data = RequestsGetter.get_result_by_request(url=url, is_json=True)
            if not result:
                logging.error(message)
                return result, message, json_data

            result_run = True

        except Exception:

            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, json_data

    @staticmethod
    def get_latest_release_tag_by_repo_name(repo_name: str) -> Tuple[bool, str, Any]:
        """Gets latest release tag by github repository name

        Args:
            repo_name (str): Repository path on github.

        Returns:
            Tuple of bool, str and Any

            result_run (bool) : True if function passed correctly, False otherwise.
            message_run (str) : Returns an error message if an error occurs in the function.
            json_data         : Latest release tag.
        """

        result_run : bool = False
        message_run : str = ''
        url : str = str(setting["Github"]["linkAllReleasesTags"]).format(repo_name)
        json_data : Any = ''

        try:

            result, message, status_code, json_data = RequestsGetter.get_result_by_request(url=url, is_json=True)
            if not result:
                logging.error(message)
                return result, message, json_data

            json_data = json_data[len(json_data)-1]

            result_run = True

        except Exception:

            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, json_data

    @staticmethod
    def get_all_releases_data_by_repo_name(repo_name: str) -> Tuple[bool, str, Any]:
        """Gets all releases data by github repository name

        Args:
            repo_name (str): Repository path on github.

        Returns:
            Tuple of bool, str and Any

            result_run (bool) : True if function passed correctly, False otherwise.
            message_run (str) : Returns an error message if an error occurs in the function.
            json_data         : All releases data.
        """

        result_run: bool = False
        message_run: str = ''
        url: str = str(setting["Github"]["linkAllReleases"]).format(repo_name)
        json_data: Any = ''

        try:

            result, message, status_code, json_data = RequestsGetter.get_result_by_request(url=url, is_json=True)
            if not result:
                logging.error(message)
                return result, message, json_data

            result_run = True

        except Exception:

            message_run = f'Unexcepted error: {str(traceback.format_exc())}'
            logging.error(message_run)

        return result_run, message_run, json_data
