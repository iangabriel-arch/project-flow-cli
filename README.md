# ProjectFlow CLI

A Python-based Command-Line Interface (CLI) tool for managing users, projects,
and tasks. Built as a Module 4 final project at Moringa School.

## Features

- Create, view, and update users (with name and email validation)
- Add projects to specific users, with descriptions and due dates
- Add tasks to projects, with status tracking and assignment
- Mark tasks as pending, in-progress, or done
- One-line polymorphic `summary` for any user, project, or task
- Data persistence using JSON, with safe handling of missing/corrupt files
- Pretty, colorized output using the `rich` library
- Advanced object-oriented design:
  - `Person` base class shared by `User`
  - `Identifiable` abstract base class giving every entity (`User`,
    `Project`, `Task`) its own auto-incrementing ID counter, plus
    equality, hashing, and ordering by ID
  - `Serializable` abstract mixin defining the `to_dict`/`from_dict`
    contract and a polymorphic `summary()` template method
  - Reusable **descriptor classes** (`NonEmptyString`, `EmailAddress`,
    `ChoiceAttribute`, `OptionalDateString`) providing validated,
    encapsulated attributes across multiple models
  - `User` uses multiple inheritance (`Person`, `Identifiable`, `Serializable`)

## Tech Stack

- Python 3.10+
- `argparse` (CLI)
- `rich` (pretty output)
- `pytest` (testing)
- JSON (data persistence)

## Project Structure

```
project-flow-cli/
├── main.py            # Entry point
├── cli.py             # CLI command definitions and handlers
├── models/
│   ├── base.py          # Identifiable & Serializable abstract base classes
│   ├── descriptors.py    # Reusable validated-attribute descriptors
│   ├── person.py         # Base Person class (name, email validation)
│   ├── user.py           # User (Person + Identifiable + Serializable), owns Projects
│   ├── project.py        # Project (Identifiable + Serializable), owns Tasks
│   └── task.py           # Task (Identifiable + Serializable)
├── utils/
│   ├── file_io.py       # JSON load/save with error handling
│   └── helpers.py       # find_user, find_project, find_task
├── data/
│   └── data.json        # Persisted data (created automatically)
└── tests/                # pytest test suite
```

## Installation

1. Clone the repository:

        git clone https://github.com/iangabriel-arch/project-flow-cli.git
        cd project-flow-cli

2. Install dependencies (using pip):

        pip install -r requirements.txt

   Or using Pipenv:

        pipenv install --dev

## Usage

### Users

Add a user (name and email required, email is validated):

    python3 main.py add-user --name "Alex" --email "alex@example.com"

List all users:

    python3 main.py list-users

Update a user's name and/or email:

    python3 main.py update-user --name "Alex" --new-name "Alexander" --new-email "alexander@example.com"

### Projects

Add a project to a user (description and due date are optional; due date
must be in `YYYY-MM-DD` format):

    python3 main.py add-project --user "Alex" --title "CLI Tool" --description "A terminal project manager" --due-date "2026-12-31"

List projects for a user:

    python3 main.py list-projects --user "Alex"

Update a project's title, description, and/or due date:

    python3 main.py update-project --title "CLI Tool" --description "Updated description" --due-date "2027-01-15"

### Tasks

Add a task to a project (status defaults to `pending`; valid statuses are
`pending`, `in-progress`, `done`):

    python3 main.py add-task --project "CLI Tool" --title "Implement add-task" --assigned-to "Alex" --status "in-progress"

List tasks for a project:

    python3 main.py list-tasks --project "CLI Tool"

Update a task's title, status, and/or assignee:

    python3 main.py update-task --project "CLI Tool" --title "Implement add-task" --status "done" --assigned-to "Bob"

Mark a task as complete (shortcut for setting status to `done`):

    python3 main.py complete-task --project "CLI Tool" --title "Implement add-task"

### Summary

Print a one-line summary for a user, project, or task. This single command
works polymorphically across all three entity types:

    python3 main.py summary --user "Alex"
    python3 main.py summary --project "CLI Tool"
    python3 main.py summary --project "CLI Tool" --task "Implement add-task"

## Data Model

- **User**: `id`, `name`, `email`, `projects` (one-to-many)
- **Project**: `id`, `title`, `description`, `due_date`, `owner`, `tasks` (one-to-many)
- **Task**: `id`, `title`, `status` (`pending` / `in-progress` / `done`), `assigned_to`

All attributes are validated through reusable descriptor classes
(`models/descriptors.py`) -- e.g. invalid emails, empty titles, malformed
dates, or invalid statuses raise a `ValueError` and are reported to the user
without crashing the program.

Every entity (`User`, `Project`, `Task`) inherits from two shared abstract
base classes (`models/base.py`):

- `Identifiable` -- gives each entity type its own independent
  auto-incrementing `id`, plus `==`, `hash()`, and ordering by id.
- `Serializable` -- defines the `to_dict`/`from_dict` contract and a
  polymorphic `summary()` method, where each class supplies its own
  `_summary_fields()`.

## Running Tests

    pytest tests/ -v

The test suite covers:

- Model creation, validation, inheritance, and JSON serialization
- Helper functions (`find_user`, `find_project`, `find_task`)
- File I/O, including missing, empty, and malformed data files
- End-to-end CLI command behavior (success and error cases)

## Known Issues / Limitations

- User, project, and task lookups by name/title are case-insensitive but
  require an exact (trimmed) match — no fuzzy search.
- Data files older than this version (without `id`, `email`, or `status`
  fields) are loaded with sensible defaults (`unknown@example.com`,
  auto-assigned IDs, and `status` derived from the legacy `completed` flag),
  but it's recommended to update those records via `update-user` /
  `update-project` / `update-task` once loaded.
- There is currently no `delete-*` command for users, projects, or tasks.

## Author

Ian Gabriel - Moringa School SDF-FT17
