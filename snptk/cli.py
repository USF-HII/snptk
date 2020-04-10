import argparse
import sys

import snptk.app
import snptk.release

def main():
    parser = argparse.ArgumentParser(prog='snptk', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-v', '--version', action='version', version=snptk.release.__version__)

    subparsers = parser.add_subparsers(help='sub-command help')

    #-----------------------------------------------------------------------------------------------------
    # map-using-coord
    #-----------------------------------------------------------------------------------------------------

    parser_map_using_coord = subparsers.add_parser('map-using-coord',
                                                    help='Generate edit maps using genetic coordindates of bim entry')

    parser_map_using_coord.set_defaults(func=snptk.app.map_using_coord)

    parser_map_using_coord.add_argument('bim')

    parser_map_using_coord.add_argument('--bim-offset', type=int, default=0)

    parser_map_using_coord.add_argument('-d', '--dbsnp')

    parser_map_using_coord.add_argument('--keep-multi-snp-mappings', action="store_true")

    parser_map_using_coord.add_argument('--keep-unmapped-rsids', action="store_true")

    parser_map_using_coord.add_argument('-o', '--output-prefix')

    #-----------------------------------------------------------------------------------------------------
    # map-using-rs-id
    #-----------------------------------------------------------------------------------------------------

    map_using_rs_id = subparsers.add_parser('map-using-rs-id', help='Update snpid and position')

    map_using_rs_id.set_defaults(func=snptk.app.map_using_rs_id)

    map_using_rs_id.add_argument('bim')

    map_using_rs_id.add_argument('-d', '--dbsnp')

    map_using_rs_id.add_argument('-r', '--rs-merge')

    map_using_rs_id.add_argument('--bim-offset', type=int, default=0)

    map_using_rs_id.add_argument('-o', '--output-prefix')

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
