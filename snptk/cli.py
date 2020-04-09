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

    parser_snpid_from_coord.add_argument('--bim-offset', type=int, default=0)

    parser_snpid_from_coord.add_argument('-d', '--dbsnp')

    parser_snpid_from_coord.add_argument('--keep-multi-snp-mappings', action="store_true")

    parser_snpid_from_coord.add_argument('--keep-unmapped-rsids', action="store_true")

    parser_snpid_from_coord.add_argument('-o', '--output-prefix')

    #-----------------------------------------------------------------------------------------------------
    # update-snpid-and-position
    #-----------------------------------------------------------------------------------------------------

    parser_update_snpids = subparsers.add_parser('update-snpid-and-position', help='Update snpid and position')

    parser_update_snpids.set_defaults(func=snptk.app.update_snpid_and_position)

    parser_update_snpids.add_argument('bim')

    parser_update_snpids.add_argument('-d', '--dbsnp')

    parser_update_snpids.add_argument('-r', '--rs-merge')

    parser_update_snpids.add_argument('--bim-offset', type=int, default=0)

    parser_update_snpids.add_argument('-o', '--output-prefix')

    #-----------------------------------------------------------------------------------------------------
    # remove duplicates
    #-----------------------------------------------------------------------------------------------------

    parser_remove_duplicates = subparsers.add_parser('remove-duplicates', help='Remove duplicate snps in plink binary files')

    parser_remove_duplicates.set_defaults(func=snptk.app.remove_duplicates)

    parser_remove_duplicates.add_argument('--plink-prefix')

    parser_remove_duplicates.add_argument('-o', '--output-prefix')

    #-----------------------------------------------------------------------------------------------------
    # plink update snpid from coordniate
    #-----------------------------------------------------------------------------------------------------

    parser_snpid_from_coord_update = subparsers.add_parser('snpid-from-coord-update',
                                                    help='Plink update using output from snptk snpid_from_coord')

    parser_snpid_from_coord_update.set_defaults(func=snptk.app.snpid_from_coord_update)

    parser_snpid_from_coord_update.add_argument('--plink-prefix')

    parser_snpid_from_coord_update.add_argument('--update-file')

    parser_snpid_from_coord_update.add_argument('--delete-file')

    parser_snpid_from_coord_update.add_argument('--out-name')

    parser_snpid_from_coord_update.add_argument('-o', '--output-prefix')

    #-----------------------------------------------------------------------------------------------------
    # plink update snpid and position
    #-----------------------------------------------------------------------------------------------------

    parser_snpid_and_position_update = subparsers.add_parser('snpid-and-position-update',
                                                    help='Plink update using output from snptk snpid_and_position')

    parser_snpid_and_position_update.set_defaults(func=snptk.app.snpid_and_position_update)

    parser_snpid_and_position_update.add_argument('--plink-prefix')

    parser_snpid_and_position_update.add_argument('--delete-file')

    parser_snpid_and_position_update.add_argument('--update-file')

    parser_snpid_and_position_update.add_argument('--coord-file')

    parser_snpid_and_position_update.add_argument('--chr-file')

    parser_snpid_and_position_update.add_argument('--out-name')

    parser_snpid_and_position_update.add_argument('-o', '--output-prefix')

    #-----------------------------------------------------------------------------------------------------
    # parse
    #-----------------------------------------------------------------------------------------------------

    if len(sys.argv) > 1:
        args = parser.parse_args(sys.argv[1:])
        args.func(vars(args))
    else:
        parser.print_help()
        sys.exit(1)
