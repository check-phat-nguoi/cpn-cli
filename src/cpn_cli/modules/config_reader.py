from json import load
from os.path import exists as path_exists
from typing import Final

from pydantic import ValidationError

from cpn_cli.constants import CONFIG_PATHS
from cpn_cli.models.config import Config
from cpn_cli.modules.argparse import args


def _config_reader() -> Config:
    def read_config(config_path: str) -> Config:
        try:
            with open(config_path, encoding="utf8") as config_fp:
                data = load(config_fp)
                return Config(**data)
        except ValidationError as e:
            print(f"Failed to read the config from {config_path}!")
            print(e)
            exit(1)

    if args.config:
        if path_exists(args.config):
            return read_config(args.config)
        else:
            print("Config not found with the given config path!")
            exit(1)

    for config_path in CONFIG_PATHS:
        if path_exists(config_path):
            return read_config(config_path)

    print("No config was found!")
    exit(1)


config: Final[Config] = _config_reader()
