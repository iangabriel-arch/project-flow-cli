import pytest
from models.user import User
from models.project import Project
from models.task import Task

# ---- User Tests ----
def test_create_user():
    user = User("Alex")
    assert user.name == "Alex"
    assert user.projects == []

def test_add_project_to_user():
    user = User("Alex")
    project = Project("CLI Tool", "Alex")
    user.add_project(project)
    assert len(user.projects) == 1
    assert user.projects[0].title == "CLI Tool"

def test_user_to_dict():
    user = User("Alex")
    d = user.to_dict()
    assert d["name"] == "Alex"
    assert d["projects"] == []

def test_user_from_dict():
    data = {"name": "Alex", "projects": []}
    user = User.from_dict(data)
    assert user.name == "Alex"

# ---- Project Tests ----
def test_create_project():
    project = Project("CLI Tool", "Alex")
    assert project.title == "CLI Tool"
    assert project.tasks == []

def test_add_task_to_project():
    project = Project("CLI Tool", "Alex")
    task = Task("Implement add-task")
    project.add_task(task)
    assert len(project.tasks) == 1
    assert project.tasks[0].title == "Implement add-task"

def test_project_to_dict():
    project = Project("CLI Tool", "Alex")
    d = project.to_dict()
    assert d["title"] == "CLI Tool"
    assert d["tasks"] == []

# ---- Task Tests ----
def test_create_task():
    task = Task("Implement add-task")
    assert task.title == "Implement add-task"
    assert task.completed == False

def test_mark_task_complete():
    task = Task("Implement add-task")
    task.mark_complete()
    assert task.completed == True

def test_task_to_dict():
    task = Task("Implement add-task")
    d = task.to_dict()
    assert d["title"] == "Implement add-task"
    assert d["completed"] == False