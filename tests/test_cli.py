import json
import os
import subprocess
import sys
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_cli(args, cwd):
    """Run main.py with the given CLI args inside `cwd` and return the result.

    Args:
        args (list[str]): CLI arguments, e.g. ["add-user", "--name", "Alex", "--email", "a@a.com"].
        cwd (str): working directory in which to run the command (so data/data.json
            is created in an isolated temp location).

    Returns:
        subprocess.CompletedProcess: the completed process, with stdout/stderr captured.
    """
    return subprocess.run(
        [sys.executable, os.path.join(REPO_ROOT, "main.py")] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def isolated_cwd(tmp_path):
    """Provide a temp working directory with its own data/ folder."""
    (tmp_path / "data").mkdir()
    return str(tmp_path)


def test_add_user_success(isolated_cwd):
    result = run_cli(["add-user", "--name", "Alex", "--email", "alex@example.com"], isolated_cwd)
    assert result.returncode == 0
    assert "created successfully" in result.stdout


def test_add_user_invalid_email(isolated_cwd):
    result = run_cli(["add-user", "--name", "Alex", "--email", "not-an-email"], isolated_cwd)
    assert result.returncode == 0
    assert "Invalid email address" in result.stdout

    # Ensure nothing was persisted.
    data_file = os.path.join(isolated_cwd, "data", "data.json")
    if os.path.exists(data_file):
        with open(data_file) as f:
            content = f.read().strip()
        assert content in ("", "[]")


def test_add_user_duplicate(isolated_cwd):
    run_cli(["add-user", "--name", "Alex", "--email", "alex@example.com"], isolated_cwd)
    result = run_cli(["add-user", "--name", "Alex", "--email", "alex2@example.com"], isolated_cwd)
    assert "already exists" in result.stdout


def test_list_users_empty(isolated_cwd):
    result = run_cli(["list-users"], isolated_cwd)
    assert "No users found" in result.stdout


def test_full_workflow(isolated_cwd):
    """Exercise the full add-user -> add-project -> add-task -> complete-task flow."""
    run_cli(["add-user", "--name", "Alex", "--email", "alex@example.com"], isolated_cwd)
    run_cli([
        "add-project", "--user", "Alex", "--title", "CLI Tool",
        "--description", "A tool", "--due-date", "2026-12-31",
    ], isolated_cwd)
    run_cli([
        "add-task", "--project", "CLI Tool", "--title", "Implement add-task",
        "--assigned-to", "Alex", "--status", "pending",
    ], isolated_cwd)

    complete_result = run_cli(
        ["complete-task", "--project", "CLI Tool", "--title", "Implement add-task"],
        isolated_cwd,
    )
    assert "marked as complete" in complete_result.stdout

    # Verify persisted state.
    data_file = os.path.join(isolated_cwd, "data", "data.json")
    with open(data_file) as f:
        data = json.load(f)

    assert data[0]["name"] == "Alex"
    assert data[0]["projects"][0]["title"] == "CLI Tool"
    assert data[0]["projects"][0]["tasks"][0]["status"] == "done"


def test_add_project_missing_user(isolated_cwd):
    result = run_cli(["add-project", "--user", "Ghost", "--title", "Nope"], isolated_cwd)
    assert "not found" in result.stdout


def test_add_project_invalid_due_date(isolated_cwd):
    run_cli(["add-user", "--name", "Alex", "--email", "alex@example.com"], isolated_cwd)
    result = run_cli(
        ["add-project", "--user", "Alex", "--title", "CLI Tool", "--due-date", "31-12-2026"],
        isolated_cwd,
    )
    assert "Invalid date" in result.stdout


def test_update_user(isolated_cwd):
    run_cli(["add-user", "--name", "Alex", "--email", "alex@example.com"], isolated_cwd)
    result = run_cli(
        ["update-user", "--name", "Alex", "--new-name", "Alexander", "--new-email", "alexander@example.com"],
        isolated_cwd,
    )
    assert "renamed" in result.stdout
    assert "Email updated" in result.stdout


def test_update_user_nothing_to_update(isolated_cwd):
    run_cli(["add-user", "--name", "Alex", "--email", "alex@example.com"], isolated_cwd)
    result = run_cli(["update-user", "--name", "Alex"], isolated_cwd)
    assert "Nothing to update" in result.stdout


def test_update_task_status_and_assignment(isolated_cwd):
    run_cli(["add-user", "--name", "Alex", "--email", "alex@example.com"], isolated_cwd)
    run_cli(["add-project", "--user", "Alex", "--title", "CLI Tool"], isolated_cwd)
    run_cli(["add-task", "--project", "CLI Tool", "--title", "Task A"], isolated_cwd)

    result = run_cli(
        ["update-task", "--project", "CLI Tool", "--title", "Task A",
         "--status", "in-progress", "--assigned-to", "Bob"],
        isolated_cwd,
    )
    assert "status updated to 'in-progress'" in result.stdout
    assert "assigned to 'Bob'" in result.stdout


def test_list_tasks_empty_project(isolated_cwd):
    run_cli(["add-user", "--name", "Alex", "--email", "alex@example.com"], isolated_cwd)
    run_cli(["add-project", "--user", "Alex", "--title", "CLI Tool"], isolated_cwd)
    result = run_cli(["list-tasks", "--project", "CLI Tool"], isolated_cwd)
    assert "No tasks found" in result.stdout


def test_complete_task_project_not_found(isolated_cwd):
    result = run_cli(["complete-task", "--project", "Ghost", "--title", "X"], isolated_cwd)
    assert "not found" in result.stdout


def test_no_command_prints_help(isolated_cwd):
    result = run_cli([], isolated_cwd)
    assert "usage" in result.stdout.lower()


def test_summary_user(isolated_cwd):
    run_cli(["add-user", "--name", "Alex", "--email", "alex@example.com"], isolated_cwd)
    result = run_cli(["summary", "--user", "Alex"], isolated_cwd)
    assert "User #" in result.stdout
    assert "Alex" in result.stdout


def test_summary_project(isolated_cwd):
    run_cli(["add-user", "--name", "Alex", "--email", "alex@example.com"], isolated_cwd)
    run_cli(["add-project", "--user", "Alex", "--title", "CLI Tool"], isolated_cwd)
    result = run_cli(["summary", "--project", "CLI Tool"], isolated_cwd)
    assert "Project #" in result.stdout
    assert "CLI Tool" in result.stdout


def test_summary_task(isolated_cwd):
    run_cli(["add-user", "--name", "Alex", "--email", "alex@example.com"], isolated_cwd)
    run_cli(["add-project", "--user", "Alex", "--title", "CLI Tool"], isolated_cwd)
    run_cli(["add-task", "--project", "CLI Tool", "--title", "Task A", "--status", "in-progress"], isolated_cwd)
    result = run_cli(["summary", "--project", "CLI Tool", "--task", "Task A"], isolated_cwd)
    assert "Task #" in result.stdout
    assert "in-progress" in result.stdout


def test_summary_task_requires_project(isolated_cwd):
    result = run_cli(["summary", "--task", "Task A"], isolated_cwd)
    assert "requires --project" in result.stdout


def test_summary_no_args(isolated_cwd):
    result = run_cli(["summary"], isolated_cwd)
    assert "Specify --user" in result.stdout


def test_summary_user_not_found(isolated_cwd):
    result = run_cli(["summary", "--user", "Ghost"], isolated_cwd)
    assert "not found" in result.stdout
