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
This module contains the Release Notes Presence Check action.
"""

import logging
import os
import sys
import re

from release_notes_presence_check.github_repository import GitHubRepository
from release_notes_presence_check.utils.gh_action import set_action_failed, get_action_input

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class ReleaseNotesPresenceCheckAction:
    """
    Class to handle the Release Notes Presence Check action.
    """

    def __init__(self) -> None:
        """
        Initialize the action with the required inputs.

        @return: None
        """
        self.github_token: str = get_action_input("GITHUB_TOKEN", "")
        self.location: str = get_action_input("LOCATION", "body")
        self.title: str = get_action_input("TITLE", "[Rr]elease [Nn]otes:")
        self.skip_labels: list[str] = get_action_input("SKIP_LABELS", default="").split(",")

        self.__validate_inputs()

        self.pr_number: int = int(os.environ.get("INPUT_PR_NUMBER", default=""))
        self.owner, self.repo_name = os.environ.get("INPUT_GITHUB_REPOSITORY", default="").split("/")

    def run(self) -> None:
        """
        Run the action.

        @return: None
        """

        # get PR information
        repository: GitHubRepository = GitHubRepository(self.owner, self.repo_name, self.github_token)
        pr_data: dict = repository.get_pr_info(self.pr_number)

        # check skip labels presence
        labels: list[str] = [label.get("name", "") for label in pr_data.get("labels", [])]
        logger.debug(f"PR number: {self.pr_number}, labels: {labels}")
        for label in labels:
            if label in self.skip_labels:
                logger.info("Skipping release notes check because '%s' label is present.", label)
                sys.exit(0)  # Exiting with code 0 indicates success but the action is skipped.

        # check release notes presence in defined location
        pr_body = pr_data.get("body", "")
        if len(pr_body.strip()) == 0:
            message = "Error: Pull request description is empty."
            logger.error(message)
            set_action_failed(message)

        # Check if release notes tag is present
        if not re.search(self.title, pr_body):
            message = f"Error: Release notes title '{self.title}' not found in pull request body."
            logger.error(message)
            set_action_failed(message)

        # Get line index of the release notes tag
        lines = pr_body.split("\n")
        release_notes_start_index = None
        for i, line in enumerate(lines):
            if re.search(self.title, line):
                release_notes_start_index = i + 1  # text after the tag line
                break

        # Check if there is content after the release notes tag
        if release_notes_start_index is None or release_notes_start_index >= len(lines):
            message = "Error: No content found after the release notes tag."
            logger.error(message)
            set_action_failed(message)

        # Check if there is a bullet list directly under the release notes tag
        text_below_release_notes = lines[release_notes_start_index:]
        if not text_below_release_notes or not text_below_release_notes[0].strip().startswith(("-", "+", "*")):
            message = "Error: No bullet list found directly under release notes tag."
            logger.error(message)
            set_action_failed(message)

        logger.info("Release Notes detected.")
        sys.exit(0)

    def __validate_inputs(self) -> None:
        """
        Validate the required inputs. When the inputs are not valid, the action will fail.

        @return: None
        """
        error_detected = False

        if len(self.github_token) == 0:
            logger.error("Failure: GITHUB_TOKEN is not set correctly.")
            error_detected = True

        value = os.environ.get("INPUT_PR_NUMBER", default="")
        if len(value) == 0:
            logger.error("Failure: PR_NUMBER is not set correctly.")
            error_detected = True

        if not value.isdigit():
            logger.error("Failure: PR_NUMBER is not a valid number.")
            error_detected = True

        value = os.environ.get("INPUT_GITHUB_REPOSITORY", default="")
        if len(value) == 0:
            logger.error("Failure: GITHUB_REPOSITORY is not set correctly.")
            error_detected = True

        if value.count("/") != 1:
            logger.error("Failure: GITHUB_REPOSITORY is not in the correct format.")
            error_detected = True
        else:
            if len(value.split("/")[0]) == 0 or len(value.split("/")[1]) == 0:
                logger.error("Failure: GITHUB_REPOSITORY is not in the correct format.")
                error_detected = True

        if len(self.location) == 0:
            logger.error("Failure: LOCATION is not set correctly.")
            error_detected = True

        if self.location not in ["body"]:
            logger.error("Failure: LOCATION is not one of the supported values.")
            error_detected = True

        if len(self.title) == 0:
            logger.error("Failure: TITLE is not set correctly.")
            error_detected = True

        logger.debug(f"Input - `location`: {self.location}")
        logger.debug(f"Input - `title`: {self.title}")
        logger.debug(f"Input - `skip_labels`: {self.skip_labels}")

        if error_detected:
            sys.exit(1)
