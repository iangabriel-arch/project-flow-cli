from models.base import Identifiable, Serializable
from models.descriptors import NonEmptyString, OptionalDateString


class Project(Identifiable, Serializable):
    """
    Represents a project, owned by a User, that contains zero or more Tasks.

    Inherits:
        - Identifiable: auto-incrementing `id`, comparison by id.
        - Serializable: to_dict/from_dict contract and polymorphic summary().

    Attributes:
        title (str): the project's title (validated, non-empty).
        description (str): a short description of the project.
        due_date (str | None): the project's due date, in YYYY-MM-DD format.
        owner (str): the name of the User who owns this project.
        tasks (list[Task]): the tasks belonging to this project.
    """

    title = NonEmptyString(field_label="Project title")
    due_date = OptionalDateString()

    def __init__(self, title, owner=None, description="", due_date=None,
                 project_id=None, tasks=None):
        Identifiable.__init__(self, entity_id=project_id)
        self.title = title
        self.description = description
        self.due_date = due_date
        self.owner = owner
        self.tasks = tasks if tasks is not None else []

    def add_task(self, task):
        """Attach a Task instance to this project.

        Args:
            task: a Task instance to add to this project's task list.

        Raises:
            TypeError: if `task` is not a Task instance.
        """
        from models.task import Task
        if not isinstance(task, Task):
            raise TypeError("add_task expects a Task instance.")
        self.tasks.append(task)

    def find_task(self, title):
        """Return the task in this project with the given title, or None."""
        for task in self.tasks:
            if task.title.lower() == title.lower():
                return task
        return None

    @property
    def completed_count(self):
        """Return the number of tasks in this project with status 'done'."""
        return sum(1 for t in self.tasks if t.status == "done")

    def _summary_fields(self):
        """Provide the fields used by Serializable.summary() for a Project."""
        return [
            ("Title", self.title),
            ("Owner", self.owner),
            ("Due", self.due_date or "N/A"),
            ("Tasks", f"{self.completed_count}/{len(self.tasks)} done"),
        ]

    def to_dict(self):
        """Serialize this project (and its tasks) to a JSON-friendly dict."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "owner": self.owner,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a Project (and its tasks) from a dict produced by to_dict()."""
        from models.task import Task
        project = cls(
            title=data["title"],
            owner=data.get("owner") or data.get("user"),
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            project_id=data.get("id"),
        )
        project.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return project

    def __str__(self):
        return (
            f"Project #{self.id}: {self.title} | Owner: {self.owner} | "
            f"Tasks: {len(self.tasks)} | Completed: {self.completed_count} | "
            f"Due: {self.due_date or 'N/A'}"
        )

    def __repr__(self):
        return f"Project(id={self.id}, title={self.title!r}, owner={self.owner!r})"
