import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import yaml


def select_dict_key_by_probability(items: Dict) -> Any:
    items_list = list(items.keys())
    prob_list = list(items.values())
    selected_item = random.choices(items_list, prob_list)[0]
    return selected_item


def get_p(array, epsilon=0.0001, divideby1=True):
    """Get the probability distribution from an array of values.
    Args:
        array (list): Array of values.
        epsilon (float): Epsilon value to prevent division by zero.
        divideby1 (bool): Whether to divide by 1.
    Returns:
        list: Probability distribution.
    """
    array = np.asarray(array, dtype=np.float64).ravel()
    k = 0
    agfd = np.min(array)
    array -= np.min((0, agfd))
    array = array / np.sum(array)  # speedier
    while np.abs(np.sum(array) - 1) > epsilon:
        array -= np.min((0, np.min(array)))
        array = array / np.sum(array)
        k += 1
    return array


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


def user_choice(
    list_options=None,
    info_text="please select:",
    fn_choice_save=None,
    suggestion=None,
    sort=True,
):
    # cmdline choices
    assert (
        list_options is not None
    ), 'please supply a list_options, e.g. ["good","bad","ugly"]'
    if sort:
        list_options.sort()

    if suggestion is not None and suggestion in list_options:
        idx_suggestion = list_options.index(suggestion)
        info_text = info_text + " (hit enter for: \033[93m%s\033[0m): " % suggestion
    else:
        idx_suggestion = -1

    for i, f in enumerate(list_options):
        if i == idx_suggestion:
            print("\033[93m(%i) %s \033[0m" % (i, f))
        else:
            print("(%i) %s" % (i, f))

    sel = input("{} ".format(info_text))
    if len(sel) == 0 and suggestion is not None:
        choice = suggestion  # list_options[int(suggestion)]
    else:
        assert sel.isdigit(), "unclear choice (type a number). you typed <{}>".format(
            sel
        )
        sel = int(sel)
        choice = list_options[sel]

    return choice
