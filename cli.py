import argparse
import textwrap

from identifiers import MACAddress


def cli() -> None:
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        formatter_class=argparse.RawTextHelpFormatter,
        description='MAC address utility.',
        epilog=textwrap.dedent('''
        -------------------------------------
        https://github.com/das-dev/macaddress
        '''),
    )
    parser.add_argument(
        '-m',
        '--mac-address',
        nargs=1,
        type=MACAddress,
        help='Search vendor by MAC'
    )
    args = parser.parse_args()
    print(type(args.mac_address))
