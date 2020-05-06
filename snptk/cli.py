import argparse
import sys

import snptk.app
import snptk.release

def main():
    help_fmt = lambda prog: argparse.HelpFormatter(prog, max_help_position=42, width=132)

    parser = argparse.ArgumentParser(prog="snptk", formatter_class=help_fmt, add_help=False)
    parser.add_argument("--help", "-h", action="help", help="Show this help message and exit")
    parser.add_argument("--version", "-v", action="version", version=snptk.release.__version__, help="Show version number and exit")

    subparsers = parser.add_subparsers()

    #-----------------------------------------------------------------------------------------------------

    map_using_coord = subparsers.add_parser(
        "map-using-coord",
        help="Generate Plink update files by chromosome/coordinate of BIM entry",
        formatter_class=help_fmt,
        add_help=False)

    map_using_coord.set_defaults(func=snptk.app.map_using_coord)

    map_using_coord.add_argument("--help", "-h", action="help", help="Show this help message and exit")

    map_using_coord.add_argument("--bim-offset", type=int, default=0, help="Add BIM_OFFSET to each BIM entry coordinate")
    map_using_coord.add_argument("--keep-multi", action="store_true", help="If coordinate maps to multiple RS Ids, write out Chrom Coord RSId,RSId,... into multi.txt")
    map_using_coord.add_argument("--keep-unmapped-rs-ids", action="store_true", help="If entry starts with rs and is not in dbsnp, keep it anyways")
    map_using_coord.add_argument("--skip-rs-ids", action="store_true", help="Do not update/delete any entry which starts with rs")

    map_using_coord.add_argument("--dbsnp", "-d", required=True, help="NCBI dbSNP SNPChrPosOnRef file or directory with split-files")
    map_using_coord.add_argument("--dbsnp-offset", type=int, default=1, help="Add DBSNP_OFFSET to each DBSNP coordinate (default: 1)")

    map_using_coord.add_argument("input_bim")
    map_using_coord.add_argument("output_map_dir")

    #-----------------------------------------------------------------------------------------------------

    map_using_rs_id = subparsers.add_parser(
        "map-using-rs-id",
        help="Generate Plink update files by Reference SNP (RS) Id of BIM entry",
        formatter_class=help_fmt,
        add_help=False)

    map_using_rs_id.set_defaults(func=snptk.app.map_using_rs_id)

    map_using_rs_id.add_argument("--help", "-h", action="help", help="Show this help message and exit")

    map_using_rs_id.add_argument("--bim-offset", type=int, default=0, help="Add BIM_OFFSET to each BIM entry coordinate")
    map_using_rs_id.add_argument("--include-file", help="Do not remove variant ids listed in this file")

    map_using_rs_id.add_argument("--dbsnp", "-d", required=True,metavar="FILE|DIR",  help="NCBI dbSNP SNPChrPosOnRef file or directory w/ split-files")
    map_using_rs_id.add_argument("--dbsnp-offset", type=int, default=1, help="Add DBSNP_OFFSET to each DBSNP coordinate (default: 1)")
    map_using_rs_id.add_argument("--refsnp-merged", "-r", required=True, metavar="FILE|DIR", help="Tab-separated gzipped file (or directory w/ split-files) generated from NCBI refsnp-merged.json.bz2")

    map_using_rs_id.add_argument("input_bim")
    map_using_rs_id.add_argument("output_map_dir")

    #-----------------------------------------------------------------------------------------------------

    remove_duplicates = subparsers.add_parser(
        "remove-duplicates",
        help="Remove duplicate snps from Plink BIM,BED,FAM fileset",
        formatter_class=help_fmt,
        add_help=False)

    remove_duplicates.set_defaults(func=snptk.app.remove_duplicates)

    remove_duplicates.add_argument("--help", "-h", action="help", help="Show this help message and exit")

    remove_duplicates.add_argument("--plink", default="plink", help="Path to plink command")
    remove_duplicates.add_argument("--bcftools", default="bcftools", help="Path to bcftools command")
    remove_duplicates.add_argument("--dry-run", "-n", action="store_true", help="Print the commands that would be executed, but do not execute them")

    remove_duplicates.add_argument("input_prefix", help="Input path prefix shared by Plink BIM,BED,FAM files")
    remove_duplicates.add_argument("output_prefix", help="Output path prefix to write out Plink BIM,BED,FAM files")

    #-----------------------------------------------------------------------------------------------------

    update_from_map = subparsers.add_parser(
        "update-from-map",
        help="Update Plink BIM,BED,FAM fileset using output from map-using-coord or map-using-rs-id",
        formatter_class=help_fmt,
        add_help=False)

    update_from_map.set_defaults(func=snptk.app.update_from_map)

    update_from_map.add_argument("--help", "-h", action="help", help="Show this help message and exit")

    update_from_map.add_argument("--dry-run", "-n", action="store_true", help="Print the commands that would be executed, but do not execute them")
    update_from_map.add_argument("--plink", default="plink", help="Path to plink command")

    update_from_map.add_argument("map_dir", help="Directory containing update files from map-using-coord/map-using-rs-id")
    update_from_map.add_argument("input_prefix", help="Input path prefix shared by Plink BIM,BED,FAM files")
    update_from_map.add_argument("output_prefix", help="Output path prefix to write out Plink BIM,BED,FAM files")

    #-----------------------------------------------------------------------------------------------------

    if len(sys.argv) > 1:
        args = parser.parse_args(sys.argv[1:])
        args.func(vars(args))
    else:
        parser.print_help()
        sys.exit(1)
