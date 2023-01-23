from datetime import datetime
from pathlib import Path

import yaml


def create_output_directory_with_identifier(
    output_dir_parent="data/WHATISTHIS", identifier="sample"
) -> None:
    # Format the datetime as a string
    now = datetime.now()
    date = now.strftime("%Y%m%d_%H%M")
    # remove any special characters from the username
    identifier = "".join(e for e in identifier if e.isalnum())
    token = f"{date}_{identifier}"
    output_dir = Path(output_dir_parent) / token
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    return output_dir


def load_yaml(filepath):
    with open(filepath, "r") as f:
        items = yaml.safe_load(f)
    return items


def save_to_yaml(items, token, output_dir="data/yaml"):
    # Create directory if it does not exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filepath = Path(output_dir) / f"{token}.yaml"
    with open(filepath, "w") as f:
        yaml.dump(items, f)
    return filepath
