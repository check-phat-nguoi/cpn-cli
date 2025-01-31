from json import load
from json.decoder import JSONDecodeError
from os.path import exists as path_exists
from os.path import expanduser as expand_user_path
from sys import stderr
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
            print(f"Failed to read the config from {config_path}!", file=stderr)
            print(e, file=stderr)
            exit(1)
        except JSONDecodeError as e:
            print(f"Failed to read the config from {config_path}!", file=stderr)
            print(e, file=stderr)
            exit(1)
        else:
            print(f"Failed to read the config from {config_path}!", file=stderr)
            exit(1)

    if args.config:
        if path_exists(args.config):
            return read_config(args.config)
        else:
            print("Config not found with the given config path!")
            exit(1)

    for config_path in CONFIG_PATHS:
        config_path = expand_user_path(config_path)
        if path_exists(config_path):
            return read_config(config_path)

    print("No config was found!", file=stderr)
    exit(1)


config: Final[Config] = _config_reader()
