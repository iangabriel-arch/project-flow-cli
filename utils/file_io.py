import json
import os
from models.user import User

DATA_FILE = os.path.join("data", "data.json")


def load_data():
    """Load all users (with their nested projects and tasks) from DATA_FILE.

    Returns an empty list if the file does not exist, is empty, or contains
    malformed JSON. This ensures the CLI can always start from a clean slate
    rather than crashing on a missing or corrupted data file.

    Returns:
        list[User]: the users loaded from disk, or an empty list.
    """
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as f:
            raw = f.read().strip()
            if not raw:
                return []
            data = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        return []

    users = []
    for entry in data:
        try:
            users.append(User.from_dict(entry))
        except (KeyError, ValueError):
            # Skip individual malformed user records rather than failing entirely.
            continue
    return users


def save_data(users):
    """Persist the given list of User objects to DATA_FILE as JSON.

    Creates the containing `data/` directory if it does not already exist.

    Args:
        users (list[User]): the users to serialize and save.

    Raises:
        OSError: if the data directory cannot be created or the file
            cannot be written.
    """
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    try:
        with open(DATA_FILE, "w") as f:
            json.dump([u.to_dict() for u in users], f, indent=4)
    except OSError as e:
        raise OSError(f"Failed to save data to {DATA_FILE}: {e}")
