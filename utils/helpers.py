from models.user import User
from models.project import Project
from models.task import Task

def find_user(users, name):
    for user in users:
        if user.name.lower() == name.lower():
            return user
    return None

def find_project(users, title):
    for user in users:
        for project in user.projects:
            if project.title.lower() == title.lower():
                return project
    return None

def find_task(project, title):
    for task in project.tasks:
        if task.title.lower() == title.lower():
            return task
    return None