from argparse import ArgumentParser, Namespace

from cpn_cli import __version__

parser: ArgumentParser = ArgumentParser(
    prog="cpn-cli",
    description="Check phạt nguội CLI",
)

parser.add_argument(
    "-c",
    "--config",
    type=str,
    default=None,
    help="Path to the configuration file",
)
parser.add_argument(
    "-v",
    "--version",
    action="version",
    version=f"%(prog)s {__version__}",
)

args: Namespace = parser.parse_args()
