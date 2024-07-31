import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(script_dir, "id_name_mapping.json")

with open(json_file_path, "r") as f:

    id_name_mapping_raw = json.load(f)

id_name_mapping = {}
for key, value in id_name_mapping_raw.items():
    id_name_mapping[key.lower()] = {}
    for key, value in value.items():
        id_name_mapping[key.lower()][key] = value.lower()


def handle_name(name: str, name_type: str):
    if name_type in id_name_mapping:
        name_dict = id_name_mapping.get(name_type)
    else:
        return name

    if name in name_dict:
        return name_dict.get(name)
    else:
        for key, value in name_dict.items():
            if name == value:
                return key
    return name
