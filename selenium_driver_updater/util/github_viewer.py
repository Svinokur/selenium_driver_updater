#Standart library imports
from typing import Any

# Local imports
from selenium_driver_updater._setting import setting
from selenium_driver_updater.util.requests_getter import RequestsGetter

class GithubViewer():
    """Class for working with github repositories"""

    @staticmethod
    def get_latest_release_data_by_repo_name(repo_name: str) -> Any:
        """Gets latest release asset by github repository name

        Args:
            repo_name (str): Repository path on github.

        Returns:
            Any

            json_data         : All latest release data.
        """

        url: str = str(setting["Github"]["linkLatestReleaseBySpecificRepoName"]).format(repo_name)

        json_data = RequestsGetter.get_result_by_request(url=url, is_json=True)

        return json_data

    @staticmethod
    def get_latest_release_tag_by_repo_name(repo_name: str) -> Any:
        """Gets latest release tag by github repository name

        Args:
            repo_name (str): Repository path on github.

        Returns:
            Any

            json_data         : Latest release tag.
        """

        url: str = str(setting["Github"]["linkAllReleasesTags"]).format(repo_name)

        json_data = RequestsGetter.get_result_by_request(url=url, is_json=True)

        json_data = json_data[len(json_data)-1]

        return json_data

    @staticmethod
    def get_all_releases_data_by_repo_name(repo_name: str) -> Any:
        """Gets all releases data by github repository name

        Args:
            repo_name (str): Repository path on github.

        Returns:
            Any

            json_data         : All releases data.
        """

        url: str = str(setting["Github"]["linkAllReleases"]).format(repo_name)

        json_data = RequestsGetter.get_result_by_request(url=url, is_json=True)

        return json_data
