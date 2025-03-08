import json


def read_config(path: str = "config.json"):
    with open(path, "r") as f:
        conf = json.loads(f.read())

    return conf

conf = read_config()