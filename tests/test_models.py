import pytest
from models.person import Person
from models.user import User
from models.project import Project
from models.task import Task


# ---- Person / inheritance tests ----
def test_user_is_a_person():
    user = User("Alex", "alex@example.com")
    assert isinstance(user, Person)


def test_person_invalid_email_raises():
    with pytest.raises(ValueError):
        Person("Alex", "not-an-email")


def test_person_empty_name_raises():
    with pytest.raises(ValueError):
        Person("", "alex@example.com")


# ---- User tests ----
def test_create_user():
    user = User("Alex", "alex@example.com")
    assert user.name == "Alex"
    assert user.email == "alex@example.com"
    assert user.projects == []
    assert isinstance(user.id, int)


def test_user_invalid_email_raises():
    with pytest.raises(ValueError):
        User("Alex", "bad-email")


def test_user_ids_increment():
    user1 = User("Alex", "alex@example.com")
    user2 = User("Sam", "sam@example.com")
    assert user2.id == user1.id + 1


def test_user_id_is_read_only():
    user = User("Alex", "alex@example.com")
    with pytest.raises(AttributeError):
        user.id = 999


def test_add_project_to_user():
    user = User("Alex", "alex@example.com")
    project = Project("CLI Tool")
    user.add_project(project)
    assert len(user.projects) == 1
    assert user.projects[0].title == "CLI Tool"
    assert user.projects[0].owner == "Alex"


def test_add_project_rejects_non_project():
    user = User("Alex", "alex@example.com")
    with pytest.raises(TypeError):
        user.add_project("not a project")


def test_user_find_project():
    user = User("Alex", "alex@example.com")
    project = Project("CLI Tool")
    user.add_project(project)
    assert user.find_project("cli tool") is project
    assert user.find_project("missing") is None


def test_user_to_dict_and_from_dict_roundtrip():
    user = User("Alex", "alex@example.com")
    user.add_project(Project("CLI Tool", description="desc", due_date="2026-01-01"))
    data = user.to_dict()
    restored = User.from_dict(data)
    assert restored.name == "Alex"
    assert restored.email == "alex@example.com"
    assert len(restored.projects) == 1
    assert restored.projects[0].title == "CLI Tool"
    assert restored.projects[0].owner == "Alex"


def test_user_str_and_repr():
    user = User("Alex", "alex@example.com")
    assert "Alex" in str(user)
    assert "User(" in repr(user)


# ---- Project tests ----
def test_create_project_defaults():
    project = Project("CLI Tool")
    assert project.title == "CLI Tool"
    assert project.description == ""
    assert project.due_date is None
    assert project.tasks == []


def test_project_empty_title_raises():
    with pytest.raises(ValueError):
        Project("")


def test_project_invalid_due_date_raises():
    with pytest.raises(ValueError):
        Project("CLI Tool", due_date="not-a-date")


def test_project_valid_due_date():
    project = Project("CLI Tool", due_date="2026-12-31")
    assert project.due_date == "2026-12-31"


def test_project_ids_increment():
    p1 = Project("Project A")
    p2 = Project("Project B")
    assert p2.id == p1.id + 1


def test_add_task_to_project():
    project = Project("CLI Tool")
    task = Task("Implement add-task")
    project.add_task(task)
    assert len(project.tasks) == 1
    assert project.tasks[0].title == "Implement add-task"


def test_add_task_rejects_non_task():
    project = Project("CLI Tool")
    with pytest.raises(TypeError):
        project.add_task("not a task")


def test_project_find_task():
    project = Project("CLI Tool")
    task = Task("Implement add-task")
    project.add_task(task)
    assert project.find_task("implement add-task") is task
    assert project.find_task("missing") is None


def test_project_completed_count():
    project = Project("CLI Tool")
    t1 = Task("Task 1", status="done")
    t2 = Task("Task 2", status="pending")
    project.add_task(t1)
    project.add_task(t2)
    assert project.completed_count == 1


def test_project_to_dict_and_from_dict_roundtrip():
    project = Project("CLI Tool", owner="Alex", description="desc", due_date="2026-05-01")
    project.add_task(Task("Implement add-task", status="in-progress", assigned_to="Alex"))
    data = project.to_dict()
    restored = Project.from_dict(data)
    assert restored.title == "CLI Tool"
    assert restored.owner == "Alex"
    assert restored.description == "desc"
    assert restored.due_date == "2026-05-01"
    assert len(restored.tasks) == 1
    assert restored.tasks[0].status == "in-progress"


def test_project_str():
    project = Project("CLI Tool", owner="Alex")
    assert "CLI Tool" in str(project)
    assert "Alex" in str(project)


# ---- Task tests ----
def test_create_task_defaults():
    task = Task("Implement add-task")
    assert task.title == "Implement add-task"
    assert task.status == "pending"
    assert task.assigned_to is None
    assert task.completed is False


def test_task_empty_title_raises():
    with pytest.raises(ValueError):
        Task("")


def test_task_invalid_status_raises():
    with pytest.raises(ValueError):
        Task("Implement add-task", status="invalid-status")


def test_task_ids_increment():
    t1 = Task("Task 1")
    t2 = Task("Task 2")
    assert t2.id == t1.id + 1


def test_mark_task_complete():
    task = Task("Implement add-task")
    task.mark_complete()
    assert task.status == "done"
    assert task.completed is True


def test_mark_task_in_progress_and_pending():
    task = Task("Implement add-task")
    task.mark_in_progress()
    assert task.status == "in-progress"
    task.mark_pending()
    assert task.status == "pending"


def test_task_to_dict():
    task = Task("Implement add-task", status="done", assigned_to="Alex")
    d = task.to_dict()
    assert d["title"] == "Implement add-task"
    assert d["status"] == "done"
    assert d["assigned_to"] == "Alex"


def test_task_from_dict_legacy_completed_field():
    """Older data files used a boolean `completed` field instead of `status`."""
    data = {"title": "Old Task", "completed": True}
    task = Task.from_dict(data)
    assert task.status == "done"

    data2 = {"title": "Old Task 2", "completed": False}
    task2 = Task.from_dict(data2)
    assert task2.status == "pending"


def test_task_str():
    task = Task("Implement add-task", assigned_to="Alex")
    assert "Implement add-task" in str(task)
    assert "Alex" in str(task)
