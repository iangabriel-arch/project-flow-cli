import json
import pytest
from models.user import User
from models.project import Project
from models.task import Task
from utils.helpers import find_user, find_project, find_task
from utils import file_io


# ---- find_user / find_project / find_task ----
@pytest.fixture
def sample_users():
    user = User("Alex", "alex@example.com")
    project = Project("CLI Tool", owner="Alex")
    task = Task("Implement add-task")
    project.add_task(task)
    user.add_project(project)
    return [user]


def test_find_user_found(sample_users):
    assert find_user(sample_users, "alex") is sample_users[0]


def test_find_user_not_found(sample_users):
    assert find_user(sample_users, "Nobody") is None


def test_find_project_found(sample_users):
    project = find_project(sample_users, "cli tool")
    assert project is not None
    assert project.title == "CLI Tool"


def test_find_project_not_found(sample_users):
    assert find_project(sample_users, "Nonexistent") is None


def test_find_task_found(sample_users):
    project = find_project(sample_users, "CLI Tool")
    task = find_task(project, "implement add-task")
    assert task is not None
    assert task.title == "Implement add-task"


def test_find_task_not_found(sample_users):
    project = find_project(sample_users, "CLI Tool")
    assert find_task(project, "Nonexistent") is None


# ---- file_io ----
def test_load_data_missing_file(tmp_path, monkeypatch):
    missing_path = tmp_path / "does_not_exist.json"
    monkeypatch.setattr(file_io, "DATA_FILE", str(missing_path))
    assert file_io.load_data() == []


def test_load_data_empty_file(tmp_path, monkeypatch):
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("")
    monkeypatch.setattr(file_io, "DATA_FILE", str(empty_file))
    assert file_io.load_data() == []


def test_load_data_malformed_json(tmp_path, monkeypatch):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json")
    monkeypatch.setattr(file_io, "DATA_FILE", str(bad_file))
    assert file_io.load_data() == []


def test_save_and_load_roundtrip(tmp_path, monkeypatch):
    target = tmp_path / "data" / "data.json"
    monkeypatch.setattr(file_io, "DATA_FILE", str(target))

    user = User("Alex", "alex@example.com")
    project = Project("CLI Tool", owner="Alex", description="desc", due_date="2026-01-01")
    project.add_task(Task("Implement add-task", status="in-progress", assigned_to="Alex"))
    user.add_project(project)

    file_io.save_data([user])
    assert target.exists()

    loaded = file_io.load_data()
    assert len(loaded) == 1
    assert loaded[0].name == "Alex"
    assert loaded[0].projects[0].title == "CLI Tool"
    assert loaded[0].projects[0].tasks[0].status == "in-progress"


def test_load_data_skips_malformed_user_entries(tmp_path, monkeypatch):
    target = tmp_path / "data.json"
    # One valid user, one malformed (missing required 'name' key).
    target.write_text(json.dumps([
        {"name": "Alex", "email": "alex@example.com", "projects": []},
        {"email": "bad@example.com", "projects": []},
    ]))
    monkeypatch.setattr(file_io, "DATA_FILE", str(target))

    loaded = file_io.load_data()
    assert len(loaded) == 1
    assert loaded[0].name == "Alex"
