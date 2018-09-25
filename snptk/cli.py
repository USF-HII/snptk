import argparse
import sys

import snptk.app
import snptk.release

def main():
    parser = argparse.ArgumentParser(prog='snptk', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-v', '--version', action='version', version=snptk.release.__version__)

    subparsers = parser.add_subparsers(help='sub-command help')

    #-----------------------------------------------------------------------------------------------------
    # snpid-from-coord
    #-----------------------------------------------------------------------------------------------------

    parser_snpid_from_coord = subparsers.add_parser('snpid-from-coord',
                                                    help='Fill in missing rs ids using chromosome coordinates')

    parser_snpid_from_coord.set_defaults(func=snptk.app.snpid_from_coord)

    parser_snpid_from_coord.add_argument('bim')

    parser_snpid_from_coord.add_argument('-d', '--dbsnp')

    #-----------------------------------------------------------------------------------------------------
    # update-snpids
    #-----------------------------------------------------------------------------------------------------

    # parser_update_snpids = subparsers.add_parser('update-snpids', help='Update snpids')

    #-----------------------------------------------------------------------------------------------------
    # parse
    #-----------------------------------------------------------------------------------------------------

    if len(sys.argv) > 1:
        args = parser.parse_args(sys.argv[1:])
        args.func(vars(args))
    else:
        parser.print_help()
        sys.exit(1)
