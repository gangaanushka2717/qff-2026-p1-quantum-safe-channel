
import json
from pathlib import Path


def load_processor(path):
    """Load a processor configuration from a JSON file."""
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)
