import argparse
from rich.console import Console
from rich.table import Table

from models.user import User
from models.project import Project
from models.task import Task
from utils.file_io import load_data, save_data
from utils.helpers import find_user, find_project, find_task

console = Console()


def build_parser():
    """Construct and return the top-level argparse parser for ProjectFlow."""
    parser = argparse.ArgumentParser(
        prog="ProjectFlow",
        description="A CLI Project Management Tool for managing users, projects, and tasks.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- User commands -----------------------------------------------
    add_user = subparsers.add_parser("add-user", help="Add a new user")
    add_user.add_argument("--name", required=True, help="Name of the user")
    add_user.add_argument("--email", required=True, help="Email address of the user")

    subparsers.add_parser("list-users", help="List all users")

    update_user = subparsers.add_parser("update-user", help="Update an existing user")
    update_user.add_argument("--name", required=True, help="Current name of the user")
    update_user.add_argument("--new-name", help="New name for the user")
    update_user.add_argument("--new-email", help="New email address for the user")

    # --- Project commands ----------------------------------------------
    add_project = subparsers.add_parser("add-project", help="Add a project to a user")
    add_project.add_argument("--user", required=True, help="Name of the user")
    add_project.add_argument("--title", required=True, help="Title of the project")
    add_project.add_argument("--description", default="", help="Description of the project")
    add_project.add_argument("--due-date", dest="due_date", default=None,
                              help="Due date in YYYY-MM-DD format")

    list_projects = subparsers.add_parser("list-projects", help="List projects for a user")
    list_projects.add_argument("--user", required=True, help="Name of the user")

    update_project = subparsers.add_parser("update-project", help="Update an existing project")
    update_project.add_argument("--title", required=True, help="Current title of the project")
    update_project.add_argument("--new-title", help="New title for the project")
    update_project.add_argument("--description", help="New description for the project")
    update_project.add_argument("--due-date", dest="due_date", help="New due date in YYYY-MM-DD format")

    # --- Task commands ----------------------------------------------------
    add_task = subparsers.add_parser("add-task", help="Add a task to a project")
    add_task.add_argument("--project", required=True, help="Title of the project")
    add_task.add_argument("--title", required=True, help="Title of the task")
    add_task.add_argument("--assigned-to", dest="assigned_to", default=None,
                           help="Name of the user this task is assigned to")
    add_task.add_argument("--status", default="pending", choices=Task.VALID_STATUSES,
                           help="Initial status of the task (default: pending)")

    list_tasks = subparsers.add_parser("list-tasks", help="List tasks for a project")
    list_tasks.add_argument("--project", required=True, help="Title of the project")

    update_task = subparsers.add_parser("update-task", help="Update an existing task")
    update_task.add_argument("--project", required=True, help="Title of the project the task belongs to")
    update_task.add_argument("--title", required=True, help="Current title of the task")
    update_task.add_argument("--new-title", help="New title for the task")
    update_task.add_argument("--status", choices=Task.VALID_STATUSES, help="New status for the task")
    update_task.add_argument("--assigned-to", dest="assigned_to", help="New assignee for the task")

    complete_task = subparsers.add_parser("complete-task", help="Mark a task as complete")
    complete_task.add_argument("--project", required=True, help="Title of the project")
    complete_task.add_argument("--title", required=True, help="Title of the task")

    # --- Summary command ---------------------------------------------------
    summary = subparsers.add_parser(
        "summary",
        help="Show a one-line summary for a user, project, or task",
    )
    summary.add_argument("--user", help="Name of the user to summarize")
    summary.add_argument("--project", help="Title of the project to summarize")
    summary.add_argument("--task", help="Title of the task to summarize (requires --project)")

    return parser


def handle_add_user(args, users):
    """Create a new user, unless one with the same name already exists."""
    if find_user(users, args.name):
        console.print(f"[yellow]⚠️ User '{args.name}' already exists.[/yellow]")
        return False

    user = User(args.name, args.email)
    users.append(user)
    console.print(f"[green]✅ User '{user.name}' created successfully (ID: {user.id}).[/green]")
    return True


def handle_list_users(args, users):
    """Display a table of all users and their project counts."""
    if not users:
        console.print("[yellow]No users found.[/yellow]")
        return False

    table = Table(title="Users")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Email", style="blue")
    table.add_column("Projects", style="magenta")
    for user in users:
        table.add_row(str(user.id), user.name, user.email, str(len(user.projects)))
    console.print(table)
    return False


def handle_update_user(args, users):
    """Update an existing user's name and/or email."""
    user = find_user(users, args.name)
    if not user:
        console.print(f"[red]❌ User '{args.name}' not found.[/red]")
        return False

    if not args.new_name and not args.new_email:
        console.print("[yellow]⚠️ Nothing to update. Provide --new-name and/or --new-email.[/yellow]")
        return False

    if args.new_name:
        old_name = user.name
        user.name = args.new_name
        for project in user.projects:
            project.owner = user.name
        console.print(f"[green]✅ User renamed from '{old_name}' to '{user.name}'.[/green]")

    if args.new_email:
        user.email = args.new_email
        console.print(f"[green]✅ Email updated to '{user.email}'.[/green]")

    return True


def handle_add_project(args, users):
    """Create a new project belonging to the given user."""
    user = find_user(users, args.user)
    if not user:
        console.print(f"[red]❌ User '{args.user}' not found.[/red]")
        return False

    project = Project(args.title, owner=user.name, description=args.description, due_date=args.due_date)
    user.add_project(project)
    console.print(f"[green]✅ Project '{project.title}' (ID: {project.id}) added to '{user.name}'.[/green]")
    return True


def handle_list_projects(args, users):
    """Display a table of all projects belonging to the given user."""
    user = find_user(users, args.user)
    if not user:
        console.print(f"[red]❌ User '{args.user}' not found.[/red]")
        return False

    if not user.projects:
        console.print(f"[yellow]No projects found for '{args.user}'.[/yellow]")
        return False

    table = Table(title=f"{user.name}'s Projects")
    table.add_column("ID", style="dim")
    table.add_column("Title", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Due Date", style="yellow")
    table.add_column("Tasks", style="magenta")
    table.add_column("Completed", style="green")
    for project in user.projects:
        table.add_row(
            str(project.id),
            project.title,
            project.description or "-",
            project.due_date or "-",
            str(len(project.tasks)),
            str(project.completed_count),
        )
    console.print(table)
    return False


def handle_update_project(args, users):
    """Update an existing project's title, description, and/or due date."""
    project = find_project(users, args.title)
    if not project:
        console.print(f"[red]❌ Project '{args.title}' not found.[/red]")
        return False

    if not any([args.new_title, args.description is not None, args.due_date is not None]):
        console.print("[yellow]⚠️ Nothing to update. Provide --new-title, --description, and/or --due-date.[/yellow]")
        return False

    if args.new_title:
        old_title = project.title
        project.title = args.new_title
        console.print(f"[green]✅ Project renamed from '{old_title}' to '{project.title}'.[/green]")

    if args.description is not None:
        project.description = args.description
        console.print("[green]✅ Description updated.[/green]")

    if args.due_date is not None:
        project.due_date = args.due_date
        console.print(f"[green]✅ Due date updated to '{project.due_date or 'N/A'}'.[/green]")

    return True


def handle_add_task(args, users):
    """Create a new task belonging to the given project."""
    project = find_project(users, args.project)
    if not project:
        console.print(f"[red]❌ Project '{args.project}' not found.[/red]")
        return False

    task = Task(args.title, status=args.status, assigned_to=args.assigned_to)
    project.add_task(task)
    console.print(f"[green]✅ Task '{task.title}' (ID: {task.id}) added to '{project.title}'.[/green]")
    return True


def handle_list_tasks(args, users):
    """Display a table of all tasks belonging to the given project."""
    project = find_project(users, args.project)
    if not project:
        console.print(f"[red]❌ Project '{args.project}' not found.[/red]")
        return False

    if not project.tasks:
        console.print(f"[yellow]No tasks found for '{args.project}'.[/yellow]")
        return False

    table = Table(title=f"Tasks for '{project.title}'")
    table.add_column("ID", style="dim")
    table.add_column("Task", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Assigned To", style="blue")
    for task in project.tasks:
        status_style = {
            "pending": "[red]⏳ Pending[/red]",
            "in-progress": "[yellow]🔧 In Progress[/yellow]",
            "done": "[green]✅ Done[/green]",
        }[task.status]
        table.add_row(str(task.id), task.title, status_style, task.assigned_to or "-")
    console.print(table)
    return False


def handle_update_task(args, users):
    """Update an existing task's title, status, and/or assignee."""
    project = find_project(users, args.project)
    if not project:
        console.print(f"[red]❌ Project '{args.project}' not found.[/red]")
        return False

    task = find_task(project, args.title)
    if not task:
        console.print(f"[red]❌ Task '{args.title}' not found in '{project.title}'.[/red]")
        return False

    if not any([args.new_title, args.status, args.assigned_to is not None]):
        console.print("[yellow]⚠️ Nothing to update. Provide --new-title, --status, and/or --assigned-to.[/yellow]")
        return False

    if args.new_title:
        old_title = task.title
        task.title = args.new_title
        console.print(f"[green]✅ Task renamed from '{old_title}' to '{task.title}'.[/green]")

    if args.status:
        task.status = args.status
        console.print(f"[green]✅ Task status updated to '{task.status}'.[/green]")

    if args.assigned_to is not None:
        task.assigned_to = args.assigned_to
        console.print(f"[green]✅ Task assigned to '{task.assigned_to}'.[/green]")

    return True


def handle_complete_task(args, users):
    """Mark the given task in the given project as complete."""
    project = find_project(users, args.project)
    if not project:
        console.print(f"[red]❌ Project '{args.project}' not found.[/red]")
        return False

    task = find_task(project, args.title)
    if not task:
        console.print(f"[red]❌ Task '{args.title}' not found.[/red]")
        return False

    task.mark_complete()
    console.print(f"[green]✅ Task '{args.title}' marked as complete.[/green]")
    return True


def handle_summary(args, users):
    """Print a one-line summary for a user, project, or task.

    This handler demonstrates polymorphism: it resolves the target entity
    (a User, Project, or Task -- three unrelated-looking but structurally
    similar classes) and calls `.summary()` on it without needing to know
    which concrete type it is. Each class's `_summary_fields()` override
    determines what actually gets printed.
    """
    if args.task is not None:
        if not args.project:
            console.print("[red]❌ --task requires --project to also be specified.[/red]")
            return False
        project = find_project(users, args.project)
        if not project:
            console.print(f"[red]❌ Project '{args.project}' not found.[/red]")
            return False
        task = find_task(project, args.task)
        if not task:
            console.print(f"[red]❌ Task '{args.task}' not found in '{project.title}'.[/red]")
            return False
        entity = task

    elif args.project is not None:
        project = find_project(users, args.project)
        if not project:
            console.print(f"[red]❌ Project '{args.project}' not found.[/red]")
            return False
        entity = project

    elif args.user is not None:
        user = find_user(users, args.user)
        if not user:
            console.print(f"[red]❌ User '{args.user}' not found.[/red]")
            return False
        entity = user

    else:
        console.print("[yellow]⚠️ Specify --user, --project, or --task (with --project).[/yellow]")
        return False

    console.print(f"[cyan]{entity.summary()}[/cyan]")
    return False


# Maps each CLI command name to the handler function that implements it.
COMMAND_HANDLERS = {
    "add-user": handle_add_user,
    "list-users": handle_list_users,
    "update-user": handle_update_user,
    "add-project": handle_add_project,
    "list-projects": handle_list_projects,
    "update-project": handle_update_project,
    "add-task": handle_add_task,
    "list-tasks": handle_list_tasks,
    "update-task": handle_update_task,
    "complete-task": handle_complete_task,
    "summary": handle_summary,
}


def main(argv=None):
    """Entry point for the ProjectFlow CLI.

    Parses command-line arguments, loads existing data, dispatches to the
    appropriate command handler, and (if the handler made changes) saves
    the updated data back to disk.

    Args:
        argv (list[str] | None): optional list of arguments to parse instead
            of sys.argv (useful for testing).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return

    handler = COMMAND_HANDLERS.get(args.command)
    if handler is None:
        parser.print_help()
        return

    users = load_data()

    try:
        changed = handler(args, users)
    except (ValueError, TypeError) as e:
        console.print(f"[red]❌ {e}[/red]")
        return

    if changed:
        save_data(users)


if __name__ == "__main__":
    main()
