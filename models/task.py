from models.base import Identifiable, Serializable
from models.descriptors import NonEmptyString, ChoiceAttribute


class Task(Identifiable, Serializable):
    """
    Represents a single task that belongs to a Project.

    Inherits:
        - Identifiable: auto-incrementing `id`, comparison by id.
        - Serializable: to_dict/from_dict contract and polymorphic summary().

    Attributes:
        title (str): the task's title (validated, non-empty).
        status (str): one of 'pending', 'in-progress', or 'done'.
        assigned_to (str | None): the name of the user assigned to this task.
    """

    VALID_STATUSES = ("pending", "in-progress", "done")

    title = NonEmptyString(field_label="Task title")
    status = ChoiceAttribute(VALID_STATUSES, field_label="Status")

    def __init__(self, title, status="pending", assigned_to=None, task_id=None):
        Identifiable.__init__(self, entity_id=task_id)
        self.title = title
        self.status = status
        self.assigned_to = assigned_to

    @property
    def completed(self):
        """Backwards-compatible alias: True if status is 'done'."""
        return self.status == "done"

    def mark_complete(self):
        """Mark this task as done."""
        self.status = "done"

    def mark_in_progress(self):
        """Mark this task as in-progress."""
        self.status = "in-progress"

    def mark_pending(self):
        """Reset this task's status back to pending."""
        self.status = "pending"

    def _summary_fields(self):
        """Provide the fields used by Serializable.summary() for a Task."""
        return [
            ("Title", self.title),
            ("Status", self.status),
            ("Assigned to", self.assigned_to or "unassigned"),
        ]

    def to_dict(self):
        """Serialize this task to a JSON-friendly dict."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "assigned_to": self.assigned_to,
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a Task from a dict produced by to_dict().

        Supports loading legacy data that used a boolean `completed` field
        instead of `status`.
        """
        if "status" in data:
            status = data["status"]
        else:
            status = "done" if data.get("completed") else "pending"

        return cls(
            title=data["title"],
            status=status,
            assigned_to=data.get("assigned_to"),
            task_id=data.get("id"),
        )

    def __str__(self):
        icon = {"pending": "⏳", "in-progress": "🔧", "done": "✅"}[self.status]
        assignee = f" | Assigned to: {self.assigned_to}" if self.assigned_to else ""
        return f"{icon} Task #{self.id}: {self.title} | Status: {self.status}{assignee}"

    def __repr__(self):
        return f"Task(id={self.id}, title={self.title!r}, status={self.status!r})"
