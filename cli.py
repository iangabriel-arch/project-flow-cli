import argparse
from models.user import User
from models.project import Project
from models.task import Task
from utils.file_io import load_data, save_data
from utils.helpers import find_user, find_project, find_task

def main():
    parser = argparse.ArgumentParser(
        prog="ProjectFlow",
        description="A CLI Project Management Tool"
    )
    subparsers = parser.add_subparsers(dest="command")

    # add-user
    add_user = subparsers.add_parser("add-user", help="Add a new user")
    add_user.add_argument("--name", required=True, help="Name of the user")

    # list-users
    subparsers.add_parser("list-users", help="List all users")

    # add-project
    add_project = subparsers.add_parser("add-project", help="Add a project to a user")
    add_project.add_argument("--user", required=True, help="Name of the user")
    add_project.add_argument("--title", required=True, help="Title of the project")

    # list-projects
    list_projects = subparsers.add_parser("list-projects", help="List projects for a user")
    list_projects.add_argument("--user", required=True, help="Name of the user")

    # add-task
    add_task = subparsers.add_parser("add-task", help="Add a task to a project")
    add_task.add_argument("--project", required=True, help="Title of the project")
    add_task.add_argument("--title", required=True, help="Title of the task")

    # list-tasks
    list_tasks = subparsers.add_parser("list-tasks", help="List tasks for a project")
    list_tasks.add_argument("--project", required=True, help="Title of the project")

    # complete-task
    complete_task = subparsers.add_parser("complete-task", help="Mark a task as complete")
    complete_task.add_argument("--project", required=True, help="Title of the project")
    complete_task.add_argument("--title", required=True, help="Title of the task")

    args = parser.parse_args()
    users = load_data()

    if args.command == "add-user":
        if find_user(users, args.name):
            print(f"User '{args.name}' already exists.")
        else:
            users.append(User(args.name))
            save_data(users)
            print(f"✅ User '{args.name}' created successfully.")

    elif args.command == "list-users":
        if not users:
            print("No users found.")
        else:
            for user in users:
                print(user)

    elif args.command == "add-project":
        user = find_user(users, args.user)
        if not user:
            print(f"❌ User '{args.user}' not found.")
        else:
            user.add_project(Project(args.title, args.user))
            save_data(users)
            print(f"✅ Project '{args.title}' added to '{args.user}'.")

    elif args.command == "list-projects":
        user = find_user(users, args.user)
        if not user:
            print(f"❌ User '{args.user}' not found.")
        else:
            if not user.projects:
                print(f"No projects found for '{args.user}'.")
            else:
                for project in user.projects:
                    print(project)

    elif args.command == "add-task":
        project = find_project(users, args.project)
        if not project:
            print(f"❌ Project '{args.project}' not found.")
        else:
            project.add_task(Task(args.title))
            save_data(users)
            print(f"✅ Task '{args.title}' added to '{args.project}'.")

    elif args.command == "list-tasks":
        project = find_project(users, args.project)
        if not project:
            print(f"❌ Project '{args.project}' not found.")
        else:
            if not project.tasks:
                print(f"No tasks found for '{args.project}'.")
            else:
                for task in project.tasks:
                    print(task)

    elif args.command == "complete-task":
        project = find_project(users, args.project)
        if not project:
            print(f"❌ Project '{args.project}' not found.")
        else:
            task = find_task(project, args.title)
            if not task:
                print(f"❌ Task '{args.title}' not found.")
            else:
                task.mark_complete()
                save_data(users)
                print(f"✅ Task '{args.title}' marked as complete.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()