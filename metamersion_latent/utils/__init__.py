from pathlib import Path

import yaml


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
