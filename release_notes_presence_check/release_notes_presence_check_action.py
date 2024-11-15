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

logger = logging.getLogger(__name__)


class ReleaseNotesPresenceCheckAction:
    """
    Class to handle the Release Notes Presence Check action.
    """

    def __init__(self) -> None:
        """
        Initialize the action with the required inputs.

        @return: None
        """
        self.github_token = os.environ.get("INPUT_GITHUB_TOKEN", default="")
        self.pr_number = os.environ.get("INPUT_PR_NUMBER", default="")
        self.location = os.environ.get("INPUT_LOCATION", default="body")
        self.title = os.environ.get("INPUT_TITLE", default="[Rr]elease [Nn]otes:")
        self.skip_labels = os.environ.get("INPUT_SKIP_LABELS", default="")
        self.fails_on_error = os.environ.get("INPUT_FAILS_ON_ERROR", "true").lower() == "true"

        self.__validate_inputs()

    def run(self) -> None:
        """
        Run the action.

        @return: None
        """

        # get PR information


        # check skip labels presence


        # check release notes presence in defined location





        validator = NewVersionValidator(new_version, existing_versions)

        if validator.is_valid_increment():
            self.write_output("true")
            logger.info("Release Notes detected.")
            sys.exit(0)
        else:
            logger.error("Release notes not detected.")
            self.handle_failure()

    def write_output(self, valid_value) -> None:
        """
        Write the output to the file specified by the GITHUB_OUTPUT environment variable.

        @param valid_value: The value to write to the output file.
        @return: None
        """
        output_file = os.environ.get("GITHUB_OUTPUT", default="output.txt")
        if output_file:
            with open(output_file, "a", encoding="utf-8") as fh:
                print(f"valid={valid_value}", file=fh)

    def handle_failure(self) -> None:
        """
        Handle the failure of the action.

        @return: None
        """
        self.write_output("false")
        if self.fails_on_error:
            sys.exit(1)
        else:
            sys.exit(0)

    def __validate_inputs(self) -> None:
        """
        Validate the required inputs. When the inputs are not valid, the action will fail.

        @return: None
        """
        if len(self.github_token) == 0:
            logger.error("Failure: GITHUB_TOKEN is not set correctly.")
            sys.exit(1)

        if len(self.pr_number) == 0:
            logger.error("Failure: PR_NUMBER is not set correctly.")
            sys.exit(1)

        if not self.pr_number.isdigit():
            logger.error("Failure: PR_NUMBER is not a valid number.")
            sys.exit(1)

        if len(self.location) == 0:
            logger.error("Failure: LOCATION is not set correctly.")
            sys.exit(1)

        if self.location not in ["body"]:
            logger.error("Failure: LOCATION is not one of the supported values.")
            sys.exit(1)

        if len(self.title) == 0:
            logger.error("Failure: TITLE is not set correctly.")
            sys.exit(1)
