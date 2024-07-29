import json

with open("id_name_mapping.json", "r") as f:
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
    return name
