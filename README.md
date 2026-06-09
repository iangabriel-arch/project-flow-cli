# ProjectFlow CLI

A Python-based Command-Line Interface (CLI) tool for managing users, projects, and tasks. Built as a Module 4 final project at Moringa School.

## Features

- Create and manage users
- Add projects to specific users
- Add tasks to projects
- Mark tasks as complete
- Data persistence using JSON
- Pretty output using the rich library

## Tech Stack

- Python 3.10+
- argparse (CLI)
- rich (pretty output)
- pytest (testing)
- JSON (data persistence)

## Installation

1. Clone the repository:

        git clone https://github.com/iangabriel-arch/project-flow-cli.git
        cd project-flow-cli

2. Install dependencies:

        pip install -r requirements.txt

## Usage

Add a user:

    python3 main.py add-user --name "Alex"

List all users:

    python3 main.py list-users

Add a project to a user:

    python3 main.py add-project --user "Alex" --title "CLI Tool"

List projects for a user:

    python3 main.py list-projects --user "Alex"

Add a task to a project:

    python3 main.py add-task --project "CLI Tool" --title "Implement add-task"

List tasks for a project:

    python3 main.py list-tasks --project "CLI Tool"

Mark a task as complete:

    python3 main.py complete-task --project "CLI Tool" --title "Implement add-task"

## Running Tests

    pytest tests/test_models.py -v

## Author

Ian Gabriel - Moringa School SDF-FT17