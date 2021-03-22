import sys
import argparse
import textwrap

from macaddress.identifiers import MACAddress, OUIList


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent('''
            MAC address utility.
            ====================
        '''),
        epilog=' '
    )
    commands = parser.add_subparsers(title='Commands')
    update_command = commands.add_parser('update')
    update_command.add_argument(
        '-i',
        '--from-ieee',
        action='store_const',
        default=True,
        const=True
    )
    lookup_command = commands.add_parser('lookup')
    lookup_command.add_argument(
        '-m',
        '--mac-address',
        action='append',
        type=MACAddress,
        help='Search vendor by MAC'
    )
    return parser


def cli() -> None:
    parser = make_parser()
    args = vars(parser.parse_args())
    if args.get('from_ieee'):
        OUIList().update()
    for mac in args.get('mac_address') or []:
        if vendor := OUIList().lookup_by_mac(str(mac)):
            sys.stdout.write(f'{mac} => {vendor}\n')
        else:
            sys.stderr.write(f'Sorry, not found vendor for {mac}\n')
