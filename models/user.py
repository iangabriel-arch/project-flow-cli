from models.person import Person
from models.base import Identifiable, Serializable


class User(Person, Identifiable, Serializable):
    """
    Represents a user of the ProjectFlow system.

    User combines three base classes (multiple inheritance):
        - Person: gives it validated `name` and `email` attributes.
        - Identifiable: gives it an auto-incrementing `id` and comparison
          (__eq__, __lt__, __hash__) based on that id.
        - Serializable: requires to_dict/from_dict and provides the
          polymorphic `summary()` template method via `_summary_fields()`.

    A User can own zero or more Projects (one-to-many relationship).
    """

    def __init__(self, name, email, user_id=None, projects=None):
        Person.__init__(self, name, email)
        Identifiable.__init__(self, entity_id=user_id)
        self.projects = projects if projects is not None else []

    def add_project(self, project):
        """Attach a Project instance to this user.

        Args:
            project: a Project instance to add to this user's project list.

        Raises:
            TypeError: if `project` is not a Project instance.
        """
        from models.project import Project
        if not isinstance(project, Project):
            raise TypeError("add_project expects a Project instance.")
        project.owner = self.name
        self.projects.append(project)

    def find_project(self, title):
        """Return the project owned by this user with the given title, or None."""
        for project in self.projects:
            if project.title.lower() == title.lower():
                return project
        return None

    @property
    def total_tasks(self):
        """Return the total number of tasks across all of this user's projects."""
        return sum(len(p.tasks) for p in self.projects)

    @property
    def completed_tasks(self):
        """Return the total number of completed tasks across all projects."""
        return sum(p.completed_count for p in self.projects)

    def _summary_fields(self):
        """Provide the fields used by Serializable.summary() for a User."""
        return [
            ("Name", self.name),
            ("Email", self.email),
            ("Projects", len(self.projects)),
            ("Tasks done", f"{self.completed_tasks}/{self.total_tasks}"),
        ]

    def to_dict(self):
        """Serialize this user (and its projects) to a JSON-friendly dict."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "projects": [p.to_dict() for p in self.projects],
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a User (and its projects) from a dict produced by to_dict()."""
        from models.project import Project
        user = cls(
            name=data["name"],
            email=data.get("email", "unknown@example.com"),
            user_id=data.get("id"),
        )
        user.projects = [Project.from_dict(p) for p in data.get("projects", [])]
        for project in user.projects:
            project.owner = user.name
        return user

    def __str__(self):
        return f"User #{self.id}: {self.name} <{self.email}> | Projects: {len(self.projects)}"

    def __repr__(self):
        return f"User(id={self.id}, name={self.name!r}, email={self.email!r})"
