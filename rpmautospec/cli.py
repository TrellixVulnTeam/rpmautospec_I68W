import argparse
import sys

from . import changelog, release


subcmd_modules_by_name = {}


def get_cli_args(args):
    global subcmd_modules_by_name

    parser = argparse.ArgumentParser(prog="rpmautospec")

    # global arguments

    parser.add_argument(
        "--koji-url",
        help="The base URL of the Koji hub",
        default="https://koji.fedoraproject.org/kojihub",
    )

    # parsers for sub-commands

    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    for subcmd_module in (changelog, release):
        subcmd_name = subcmd_module.register_subcommand(subparsers)

        if subcmd_name in subcmd_modules_by_name:
            raise RuntimeError(f"Sub-command specified more than once: {subcmd_name}.")

        subcmd_modules_by_name[subcmd_name] = subcmd_module

    return parser.parse_args(args)


def main():
    args = get_cli_args(sys.argv[1:])

    if args.subcommand:
        subcmd_module = subcmd_modules_by_name[args.subcommand]
        subcmd_module.main(args)
