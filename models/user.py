class User:
    def __init__(self, name):
        self.name = name
        self.projects = []

    def add_project(self, project):
        self.projects.append(project)

    def to_dict(self):
        return {
            "name": self.name,
            "projects": [p.to_dict() for p in self.projects]
        }

    @staticmethod
    def from_dict(data):
        from models.project import Project
        user = User(data["name"])
        user.projects = [Project.from_dict(p) for p in data["projects"]]
        return user

    def __str__(self):
        return f"User: {self.name} | Projects: {len(self.projects)}"