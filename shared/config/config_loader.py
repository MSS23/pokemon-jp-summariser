# utils/config_loader.py

import yaml

DEFAULT_PATH = ".streamlit/credentials.yaml"

def load_config(path=DEFAULT_PATH):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def save_config(config, path=DEFAULT_PATH):
    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
