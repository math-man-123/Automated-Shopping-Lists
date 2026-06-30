import json, os


def load_json(name: str) -> dict:
    """Load `name`.json in json folder."""
    with open(f"json/{name}.json", "r") as file: 
        return json.load(file)


def check_id(id: int) -> bool:
    """Check if `id.json` exist in json folder."""
    return os.path.exists(f"json/{id}.json")
