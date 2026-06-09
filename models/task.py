class Task:
    def __init__(self, title, completed=False):
        self.title = title
        self.completed = completed

    def mark_complete(self):
        self.completed = True

    def to_dict(self):
        return {
            "title": self.title,
            "completed": self.completed
        }

    @staticmethod
    def from_dict(data):
        return Task(data["title"], data.get("completed", False))

    def __str__(self):
        status = "✅" if self.completed else "❌"
        return f"{status} Task: {self.title}"