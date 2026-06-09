class Project:
    def __init__(self, title, user=None):
        self.title = title
        self.user = user
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def to_dict(self):
        return {
            "title": self.title,
            "user": self.user,
            "tasks": [t.to_dict() for t in self.tasks]
        }

    @staticmethod
    def from_dict(data):
        from models.task import Task
        project = Project(data["title"], data.get("user"))
        project.tasks = [Task.from_dict(t) for t in data["tasks"]]
        return project

    def __str__(self):
        completed = sum(1 for t in self.tasks if t.completed)
        return f"Project: {self.title} | Tasks: {len(self.tasks)} | Completed: {completed}"