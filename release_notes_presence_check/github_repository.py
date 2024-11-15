#
# Copyright 2024 ABSA Group Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
This module contains the GitHubRepository class that is used to interact with the GitHub API.
"""

import logging
import sys
import requests

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class GitHubRepository:
    """
    A class that represents a GitHub repository and provides methods to interact
    """

    def __init__(self, owner: str, repo: str, token: str) -> None:
        """
        Initialize the GitHubRepository with the owner, repo and token.

        @param owner: The owner of the repository
        @param repo: The name of the repository
        @param token: The GitHub API token
        @return: None
        """
        self.owner = owner
        self.repo = repo
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github.v3+json"}

    def get_pr_info(self, pr_number) -> dict:
        """
        Get Pull Request information for the repository.

        @return: A Pull Request object representing the PR.
        """
        pr_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{pr_number}"
        response = requests.get(pr_url, headers=self.headers, timeout=5)
        if response.status_code != 200:
            logger.error("Error fetching PR details. Status code: %s", response.status_code)
            sys.exit(1)

        return response.json()
