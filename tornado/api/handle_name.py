import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(script_dir, "id_name_mapping.json")

with open(json_file_path, "r") as f:
    id_name_mapping = json.load(f)


def handle_name(name: str, name_type: str):
    if name_type == "packet":
        name_dict = id_name_mapping.get("packet")
    elif name_type == "entry":
        name_dict = id_name_mapping.get("entry")
    else:
        return name

    if name in name_dict:
        return name_dict.get(name)
    for key, value in name_dict.items():
        if name == value:
            return key
    return name
