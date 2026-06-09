import argparse
from rich.console import Console
from rich.table import Table
from models.user import User
from models.project import Project
from models.task import Task
from utils.file_io import load_data, save_data
from utils.helpers import find_user, find_project, find_task

console = Console()

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
            console.print(f"[yellow]⚠️ User '{args.name}' already exists.[/yellow]")
        else:
            users.append(User(args.name))
            save_data(users)
            console.print(f"[green]✅ User '{args.name}' created successfully.[/green]")

    elif args.command == "list-users":
        if not users:
            console.print("[yellow]No users found.[/yellow]")
        else:
            table = Table(title="Users")
            table.add_column("Name", style="cyan")
            table.add_column("Projects", style="magenta")
            for user in users:
                table.add_row(user.name, str(len(user.projects)))
            console.print(table)

    elif args.command == "add-project":
        user = find_user(users, args.user)
        if not user:
            console.print(f"[red]❌ User '{args.user}' not found.[/red]")
        else:
            user.add_project(Project(args.title, args.user))
            save_data(users)
            console.print(f"[green]✅ Project '{args.title}' added to '{args.user}'.[/green]")

    elif args.command == "list-projects":
        user = find_user(users, args.user)
        if not user:
            console.print(f"[red]❌ User '{args.user}' not found.[/red]")
        else:
            if not user.projects:
                console.print(f"[yellow]No projects found for '{args.user}'.[/yellow]")
            else:
                table = Table(title=f"{args.user}'s Projects")
                table.add_column("Title", style="cyan")
                table.add_column("Tasks", style="magenta")
                table.add_column("Completed", style="green")
                for project in user.projects:
                    completed = sum(1 for t in project.tasks if t.completed)
                    table.add_row(project.title, str(len(project.tasks)), str(completed))
                console.print(table)

    elif args.command == "add-task":
        project = find_project(users, args.project)
        if not project:
            console.print(f"[red]❌ Project '{args.project}' not found.[/red]")
        else:
            project.add_task(Task(args.title))
            save_data(users)
            console.print(f"[green]✅ Task '{args.title}' added to '{args.project}'.[/green]")

    elif args.command == "list-tasks":
        project = find_project(users, args.project)
        if not project:
            console.print(f"[red]❌ Project '{args.project}' not found.[/red]")
        else:
            if not project.tasks:
                console.print(f"[yellow]No tasks found for '{args.project}'.[/yellow]")
            else:
                table = Table(title=f"Tasks for '{args.project}'")
                table.add_column("Task", style="cyan")
                table.add_column("Status", style="magenta")
                for task in project.tasks:
                    status = "[green]✅ Complete[/green]" if task.completed else "[red]❌ Pending[/red]"
                    table.add_row(task.title, status)
                console.print(table)

    elif args.command == "complete-task":
        project = find_project(users, args.project)
        if not project:
            console.print(f"[red]❌ Project '{args.project}' not found.[/red]")
        else:
            task = find_task(project, args.title)
            if not task:
                console.print(f"[red]❌ Task '{args.title}' not found.[/red]")
            else:
                task.mark_complete()
                save_data(users)
                console.print(f"[green]✅ Task '{args.title}' marked as complete.[/green]")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()