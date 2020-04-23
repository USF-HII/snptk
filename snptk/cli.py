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

    map_using_coord = subparsers.add_parser('map-using-coord',
                                                    help='Generate edit maps using genetic coordindates of bim entry')

    map_using_coord.set_defaults(func=snptk.app.map_using_coord)

    map_using_coord.add_argument('--bim-offset', type=int, default=0)

    map_using_coord.add_argument('-d', '--dbsnp')

    map_using_coord.add_argument('--keep-multi-snp-mappings', action="store_true")

    map_using_coord.add_argument('--keep-unmapped-rsids', action="store_true")

    map_using_coord.add_argument('--skip-rs-ids', action="store_true")

    map_using_coord.add_argument('input_bim')

    map_using_coord.add_argument('output_map_dir')

    #-----------------------------------------------------------------------------------------------------
    # map-using-rs-id
    #-----------------------------------------------------------------------------------------------------

    map_using_rs_id = subparsers.add_parser('map-using-rs-id', help='Update snpid and position')

    map_using_rs_id.set_defaults(func=snptk.app.map_using_rs_id)

    map_using_rs_id.add_argument('-d', '--dbsnp')

    map_using_rs_id.add_argument('-r', '--rs-merge')

    map_using_rs_id.add_argument('--bim-offset', type=int, default=0)

    map_using_rs_id.add_argument('--include-file', default=None)

    map_using_rs_id.add_argument('input_bim')

    map_using_rs_id.add_argument('output_map_dir')

    #-----------------------------------------------------------------------------------------------------
    # remove duplicates
    #-----------------------------------------------------------------------------------------------------

    remove_duplicates = subparsers.add_parser('remove-duplicates', help='Remove duplicate snps in plink binary files')

    remove_duplicates.set_defaults(func=snptk.app.remove_duplicates)

    remove_duplicates.add_argument('--plink', default="plink", help="Path to plink; assumes exe is in path otherwise")

    remove_duplicates.add_argument('--bcftools', default="bcftools", help="Path to bcftools; assumes exe is in path otherwise")

    remove_duplicates.add_argument('--dry-run', '-n', action="store_true")

    remove_duplicates.add_argument('--plink-prefix')

    remove_duplicates.add_argument('-o', '--output-prefix')

    #-----------------------------------------------------------------------------------------------------
    # update-from-map
    #-----------------------------------------------------------------------------------------------------

    update_from_map = subparsers.add_parser("update-from-map")
    update_from_map.set_defaults(func=snptk.app.update_from_map)

    update_from_map.add_argument("--dry-run", "-n", action="store_true")
    update_from_map.add_argument("--plink", default="plink")
    update_from_map.add_argument("--map-dir", required=True)
    update_from_map.add_argument("input_prefix")
    update_from_map.add_argument("output_prefix")

    #-----------------------------------------------------------------------------------------------------
    # parse
    #-----------------------------------------------------------------------------------------------------

    if len(sys.argv) > 1:
        args = parser.parse_args(sys.argv[1:])
        args.func(vars(args))
    else:
        parser.print_help()
        sys.exit(1)
