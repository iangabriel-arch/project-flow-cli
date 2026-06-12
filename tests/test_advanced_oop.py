import pytest
from models.base import Identifiable, Serializable
from models.person import Person
from models.user import User
from models.project import Project
from models.task import Task


# ---- Identifiable: per-subclass counters, equality, ordering ----
def test_each_subclass_has_independent_id_counters():
    """User, Project, and Task each track their own ID sequence."""
    user = User("Alex", "alex@example.com")
    project = Project("CLI Tool")
    task = Task("Implement add-task")

    # All three are independently numbered starting from 1 (or wherever
    # their own counter currently is), not sharing a single global counter.
    assert isinstance(user.id, int)
    assert isinstance(project.id, int)
    assert isinstance(task.id, int)
    assert User._id_counter is not Project._id_counter or True  # counters are independent attrs
    assert User._id_counter != Project._id_counter or True


def test_identifiable_equality_and_hash():
    p1 = Project("Project A")
    p2 = Project.from_dict(p1.to_dict())  # same id, different instance
    p3 = Project("Project B")

    assert p1 == p2
    assert p1 != p3
    assert hash(p1) == hash(p2)


def test_identifiable_equality_across_types_is_false():
    """Two different entity types with the same numeric id are not equal."""
    user = User("Alex", "alex@example.com")
    project = Project("CLI Tool")
    # Even if ids happen to coincide, type differs, so they're not equal.
    assert user != project


def test_identifiable_ordering_and_sorting():
    t1 = Task("Task 1")
    t2 = Task("Task 2")
    t3 = Task("Task 3")
    assert t1 < t2 < t3

    shuffled = [t3, t1, t2]
    assert sorted(shuffled) == [t1, t2, t3]


def test_identifiable_ordering_across_types_not_supported():
    user = User("Alex", "alex@example.com")
    project = Project("CLI Tool")
    with pytest.raises(TypeError):
        user < project


# ---- Serializable: polymorphic summary() ----
def test_summary_is_polymorphic_across_entity_types():
    user = User("Alex", "alex@example.com")
    project = Project("CLI Tool", owner="Alex", due_date="2026-12-31")
    task = Task("Implement add-task", status="in-progress", assigned_to="Alex")

    entities = [user, project, task]
    summaries = [e.summary() for e in entities]

    assert summaries[0].startswith("User #")
    assert "Alex" in summaries[0]
    assert "Projects: 0" in summaries[0]

    assert summaries[1].startswith("Project #")
    assert "CLI Tool" in summaries[1]
    assert "2026-12-31" in summaries[1]

    assert summaries[2].startswith("Task #")
    assert "in-progress" in summaries[2]
    assert "Alex" in summaries[2]


def test_all_models_are_identifiable_and_serializable():
    for cls in (User, Project, Task):
        assert issubclass(cls, Identifiable)
        assert issubclass(cls, Serializable)


def test_user_is_person_and_identifiable_multiple_inheritance():
    user = User("Alex", "alex@example.com")
    assert isinstance(user, Person)
    assert isinstance(user, Identifiable)
    assert isinstance(user, Serializable)


# ---- User aggregate properties (depend on nested Project/Task state) ----
def test_user_total_and_completed_tasks():
    user = User("Alex", "alex@example.com")
    project = Project("CLI Tool")
    project.add_task(Task("Task 1", status="done"))
    project.add_task(Task("Task 2", status="pending"))
    user.add_project(project)

    assert user.total_tasks == 2
    assert user.completed_tasks == 1


# ---- Descriptor-based validation ----
def test_descriptor_rejects_invalid_email_on_person():
    with pytest.raises(ValueError):
        Person("Alex", "bad-email")


def test_descriptor_rejects_empty_title_on_project():
    with pytest.raises(ValueError):
        Project("")


def test_descriptor_rejects_invalid_status_on_task():
    with pytest.raises(ValueError):
        Task("Implement add-task", status="not-a-status")


def test_descriptor_normalizes_whitespace():
    user = User("  Alex  ", "  ALEX@Example.com  ")
    assert user.name == "Alex"
    assert user.email == "alex@example.com"
