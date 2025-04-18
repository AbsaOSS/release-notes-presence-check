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
This module contains the main script for the Version Tag Check GH Action.
"""

import logging
import sys

from release_notes_presence_check.release_notes_presence_check_action import ReleaseNotesPresenceCheckAction
from release_notes_presence_check.utils.gh_action import set_action_failed
from release_notes_presence_check.utils.logging_config import setup_logging

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting Release Notes Presence Check.")

    action = ReleaseNotesPresenceCheckAction()
    status, message = action.run()

    if status:
        logger.info(message)
        sys.exit(0)
    else:
        logger.error(message)
        set_action_failed(message)
