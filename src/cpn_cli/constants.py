from typing import LiteralString

CONFIG_PATHS: tuple[LiteralString, ...] = (
    "config.json",
    "cpn-cli.config.json",
    "~/cpn-cli.config.json",
)
SIMPLE_LOG_MESSAGE: LiteralString = "[%(levelname)s]: %(message)s"
DETAIL_LOG_MESSAGE: LiteralString = (
    "%(asctime)s [%(levelname)s] - %(message)s (%(filename)s:%(lineno)d - %(pathname)s)"
)
