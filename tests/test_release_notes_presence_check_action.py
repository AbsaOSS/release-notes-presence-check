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
import logging
import os
import pytest

from release_notes_presence_check.release_notes_presence_check_action import ReleaseNotesPresenceCheckAction


# input validation

def test_validate_inputs_valid(monkeypatch, caplog):
    # Set all required environment variables with valid values
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_PR_NUMBER": "109",
        "INPUT_LOCATION": "body",
        "INPUT_TITLE": "[Rr]elease [Nn]otes:",
        "INPUT_SKIP_LABELS": "",
        "INPUT_FAILS_ON_ERROR": "true",
    }
    os.environ.update(env_vars)

    # Capture logs
    caplog.set_level(logging.ERROR)

    # Instantiate the action; should not raise SystemExit if validation passes
    action = ReleaseNotesPresenceCheckAction()

    # There should be no errors or warnings
    assert "Failure" not in caplog.text

@pytest.mark.parametrize("env_name, env_value, error_message", [
    # GITHUB_TOKEN missing or empty
    ("INPUT_GITHUB_TOKEN", None, "Failure: GITHUB_TOKEN is not set correctly."),
    ("INPUT_GITHUB_TOKEN", "", "Failure: GITHUB_TOKEN is not set correctly."),

    # PR_NUMBER missing, empty, or invalid format
    ("INPUT_PR_NUMBER", None, "Failure: PR_NUMBER is not set correctly."),
    ("INPUT_PR_NUMBER", "", "Failure: PR_NUMBER is not set correctly."),
    ("INPUT_PR_NUMBER", "abc", "Failure: PR_NUMBER is not a valid number."),

    # GITHUB_REPOSITORY missing, empty, or invalid format
    ("INPUT_GITHUB_REPOSITORY", None, "Failure: GITHUB_REPOSITORY is not set correctly."),
    ("INPUT_GITHUB_REPOSITORY", "", "Failure: GITHUB_REPOSITORY is not set correctly."),
    ("INPUT_GITHUB_REPOSITORY", "ownerrepo", "Failure: GITHUB_REPOSITORY is not in the correct format."),
    ("INPUT_GITHUB_REPOSITORY", "owner//repo", "Failure: GITHUB_REPOSITORY is not in the correct format."),
    ("INPUT_GITHUB_REPOSITORY", "owner/", "Failure: GITHUB_REPOSITORY is not in the correct format."),
    ( "INPUT_GITHUB_REPOSITORY", "/repo", "Failure: GITHUB_REPOSITORY is not in the correct format."),

    # LOCATION missing, empty, or unsupported value
    ("INPUT_LOCATION", "", "Failure: LOCATION is not set correctly."),
    ("INPUT_LOCATION", "header", "Failure: LOCATION is not one of the supported values."),

    # TITLE missing or empty
    ("INPUT_TITLE", "", "Failure: TITLE is not set correctly."),
])
def test_validate_inputs_invalid(monkeypatch, caplog, env_name, env_value, error_message):
    # Set all required valid environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_PR_NUMBER": "109",
        "INPUT_LOCATION": "body",
        "INPUT_TITLE": "[Rr]elease [Nn]otes:",
        "INPUT_SKIP_LABELS": "",
    }

    # Update or remove the environment variable for the tested scenario
    if env_value is None:
        env_vars.pop(env_name, None)  # Remove the variable to simulate it missing
        if env_name in os.environ:
            os.environ.pop(env_name)
    else:
        env_vars[env_name] = env_value

    # Update environment variables for the test
    os.environ.update(env_vars)

    # Mock sys.exit to raise SystemExit exception
    with pytest.raises(SystemExit) as e:
        # Capture logs
        caplog.set_level(logging.ERROR)

        # Instantiate the action; should raise SystemExit if validation fails
        ReleaseNotesPresenceCheckAction()

    # Assert that sys.exit was called with exit code 1
    assert e.value.code == 1, f"Expected SystemExit with code 1 for {env_name}={env_value}"

    # Assert that the correct error message was logged
    assert error_message in caplog.text, f"Expected error message '{error_message}' for {env_name}={env_value}"


# run

def test_run_successful(mocker):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_PR_NUMBER": "109",
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_LOCATION": "body",
        "INPUT_TITLE": "[Rr]elease [Nn]otes:",
        "INPUT_SKIP_LABELS": "",
        "INPUT_FAILS_ON_ERROR": "true",
    }
    # Update os.environ with the test environment variables
    os.environ.update(env_vars)
    if os.path.exists("output.txt"):
        os.remove("output.txt")

    # Mock sys.exit to prevent the test from exiting
    mock_exit = mocker.patch("sys.exit")

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("release_notes_presence_check.release_notes_presence_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_pr_info.return_value = {
        "body": "Release Notes:\n- This update includes bug fixes and improvements.",
        "labels": [{"name": "bug"}, {"name": "enhancement"}]
    }

    # Run the action
    action = ReleaseNotesPresenceCheckAction()
    action.run()

    mock_exit.assert_called_once_with(0)


def test_run_skip_by_label(mocker):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_PR_NUMBER": "109",
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_LOCATION": "body",
        "INPUT_TITLE": "[Rr]elease [Nn]otes:",
        "INPUT_SKIP_LABELS": "skip-release-notes-check",
        "INPUT_FAILS_ON_ERROR": "true",
    }
    # Update os.environ with the test environment variables
    os.environ.update(env_vars)
    if os.path.exists("output.txt"):
        os.remove("output.txt")

    # Mock sys.exit to prevent the test from exiting
    mock_exit = mocker.patch("sys.exit", side_effect=SystemExit(0))

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("release_notes_presence_check.release_notes_presence_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_pr_info.return_value = {
        "body": "Release Notes:\n- This update includes bug fixes and improvements.",
        "labels": [{"name": "bug"}, {"name": "enhancement"}, {"name": "skip-release-notes-check"}]
    }

    # Run the action
    with pytest.raises(SystemExit) as exit_info:
        action = ReleaseNotesPresenceCheckAction()
        action.run()

    assert SystemExit == exit_info.type
    assert 0 == exit_info.value.code


def test_run_fail_no_body(mocker):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_PR_NUMBER": "109",
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_LOCATION": "body",
        "INPUT_TITLE": "[Rr]elease [Nn]otes:",
        "INPUT_SKIP_LABELS": "skip-release-notes-check",
        "INPUT_FAILS_ON_ERROR": "true",
    }
    # Update os.environ with the test environment variables
    os.environ.update(env_vars)
    if os.path.exists("output.txt"):
        os.remove("output.txt")

    # Mock sys.exit to prevent the test from exiting
    mock_exit = mocker.patch("sys.exit", side_effect=SystemExit(1))

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("release_notes_presence_check.release_notes_presence_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_pr_info.return_value = {
        "labels": [{"name": "bug"}, {"name": "enhancement"}]
    }

    # Run the action
    with pytest.raises(SystemExit) as exit_info:
        action = ReleaseNotesPresenceCheckAction()
        action.run()

    assert SystemExit == exit_info.type
    assert 1 == exit_info.value.code

def test_run_fail_empty_body(mocker):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_PR_NUMBER": "109",
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_LOCATION": "body",
        "INPUT_TITLE": "[Rr]elease [Nn]otes:",
        "INPUT_SKIP_LABELS": "skip-release-notes-check",
        "INPUT_FAILS_ON_ERROR": "true",
    }
    # Update os.environ with the test environment variables
    os.environ.update(env_vars)
    if os.path.exists("output.txt"):
        os.remove("output.txt")

    # Mock sys.exit to prevent the test from exiting
    mock_exit = mocker.patch("sys.exit", side_effect=SystemExit(1))

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("release_notes_presence_check.release_notes_presence_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_pr_info.return_value = {
        "body": "",
        "labels": [{"name": "bug"}, {"name": "enhancement"}]
    }

    # Run the action
    with pytest.raises(SystemExit) as exit_info:
        action = ReleaseNotesPresenceCheckAction()
        action.run()

    assert SystemExit == exit_info.type
    assert 1 == exit_info.value.code

def test_run_fail_title_not_found(mocker):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_PR_NUMBER": "109",
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_LOCATION": "body",
        "INPUT_TITLE": "Not present:",
        "INPUT_SKIP_LABELS": "skip-release-notes-check",
        "INPUT_FAILS_ON_ERROR": "true",
    }
    # Update os.environ with the test environment variables
    os.environ.update(env_vars)
    if os.path.exists("output.txt"):
        os.remove("output.txt")

    # Mock sys.exit to prevent the test from exiting
    mock_exit = mocker.patch("sys.exit", side_effect=SystemExit(1))

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("release_notes_presence_check.release_notes_presence_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_pr_info.return_value = {
        "body": "Release Notes:\n- This update includes bug fixes and improvements.",
        "labels": [{"name": "bug"}, {"name": "enhancement"}]
    }

    # Run the action
    with pytest.raises(SystemExit) as exit_info:
        action = ReleaseNotesPresenceCheckAction()
        action.run()

    assert SystemExit == exit_info.type
    assert 1 == exit_info.value.code

def test_run_fail_release_notes_lines_not_found(mocker):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_PR_NUMBER": "109",
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_LOCATION": "body",
        "INPUT_TITLE": "[Rr]elease [Nn]otes:",
        "INPUT_SKIP_LABELS": "skip-release-notes-check",
        "INPUT_FAILS_ON_ERROR": "true",
    }
    # Update os.environ with the test environment variables
    os.environ.update(env_vars)
    if os.path.exists("output.txt"):
        os.remove("output.txt")

    # Mock sys.exit to prevent the test from exiting
    mock_exit = mocker.patch("sys.exit", side_effect=SystemExit(1))

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("release_notes_presence_check.release_notes_presence_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_pr_info.return_value = {
        "body": "Release Notes:\nThis update includes bug fixes and improvements.",
        "labels": [{"name": "bug"}, {"name": "enhancement"}]
    }

    # Run the action
    with pytest.raises(SystemExit) as exit_info:
        action = ReleaseNotesPresenceCheckAction()
        action.run()

    assert SystemExit == exit_info.type
    assert 1 == exit_info.value.code

def test_run_fail_no_lines_after_title(mocker):
    # Set environment variables
    env_vars = {
        "INPUT_GITHUB_TOKEN": "fake_token",
        "INPUT_PR_NUMBER": "109",
        "INPUT_GITHUB_REPOSITORY": "owner/repo",
        "INPUT_LOCATION": "body",
        "INPUT_TITLE": "[Rr]elease [Nn]otes:",
        "INPUT_SKIP_LABELS": "skip-release-notes-check",
        "INPUT_FAILS_ON_ERROR": "true",
    }
    # Update os.environ with the test environment variables
    os.environ.update(env_vars)
    if os.path.exists("output.txt"):
        os.remove("output.txt")

    # Mock sys.exit to prevent the test from exiting
    mock_exit = mocker.patch("sys.exit", side_effect=SystemExit(1))

    # Mock the GitHubRepository class
    mock_repository_class = mocker.patch("release_notes_presence_check.release_notes_presence_check_action.GitHubRepository")
    mock_repository_instance = mock_repository_class.return_value
    mock_repository_instance.get_pr_info.return_value = {
        "body": "Release Notes:",
        "labels": [{"name": "bug"}, {"name": "enhancement"}]
    }

    # Run the action
    with pytest.raises(SystemExit) as exit_info:
        action = ReleaseNotesPresenceCheckAction()
        action.run()

    assert SystemExit == exit_info.type
    assert 1 == exit_info.value.code
