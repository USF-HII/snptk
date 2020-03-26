#!/usr/bin/env python3

import sys
import argparse
import re
import os
import gzip
import bz2
import json
from os.path import join, basename, dirname, abspath, splitext
from multiprocessing import Pool
from snptk.util import debug

sys.path.append('../snptk')


def process_dbsnp(fnames, outfile):

    with gzip.open(outfile + '.gz', 'at') as out:
        for fname in fnames:

            chromosome = re.search('chr(.*).json', fname).group(1)

            debug(f'Began parsing chr{chromosome} dbsnp file')
            with bz2.open(fname, "rb") as f2:
                for line in f2:
                    d = json.loads(line.decode('utf-8'))
                    snpid = d['refsnp_id']
                    orientation = '-'

                    if d['present_obs_movements']:
                        position = str(d['present_obs_movements'][0]['allele_in_cur_release']['position'])
                    else:
                        debug(f'rs{snpid} on chr{chromosome} does not have a position available')
                        continue

                    if len(d['primary_snapshot_data']['allele_annotations'][0]['assembly_annotation']) > 0:
                        if len(d['primary_snapshot_data']['allele_annotations'][0]['assembly_annotation'][0]['genes']) > 0:
                            orientation = d['primary_snapshot_data']['allele_annotations'][0]['assembly_annotation'][0]['genes'][0]['orientation']
                            if orientation == 'plus':
                                orientation = '0'
                            elif orientation == 'minus':
                                orientation = '1'
                            else:
                                orientation = '-'
                    else:
                        debug(f'rs{snpid} on chr{chromosome} does not have a orientation information', level=2)

                    print(snpid + " " + chromosome + " " + position + " " + orientation, file=out)

                debug(f'Finished parsing chr{chromosome} dbsnp file')

def process_rsmerge(fname, outfile):

    with gzip.open(outfile + '.gz', 'at') as out:

        debug(f'Began parsing Rsmerge file')
        with bz2.open(fname, "rb") as f2:
            for line in f2:
                d = json.loads(line.decode('utf-8'))
                if len(d['merged_snapshot_data']['merged_into']) > 0:
                    snpid = d['refsnp_id']
                    merged_snpid = d['merged_snapshot_data']['merged_into'][0]
                    print(snpid + " " + merged_snpid, file=out)
                else:
                    snpid = d['refsnp_id']
                    debug(f'rs{snpid} has no merge info!')

        debug(f'Finished parsing Rsmerge file')

def main(argv):

    parser = argparse.ArgumentParser(description='Parses GRCh38 json bz2 files and converts to flat gzipped file')

    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('--method')
    parser.add_argument('--outfile')
    parser.add_argument('filenames', nargs='*')

    args = parser.parse_args(argv)

    if args.method == 'dbsnp':
        process_dbsnp(args.filenames, args.outfile)
    elif args.method == 'rsmerge':
        process_rsmerge(args.filenames[0], args.outfile)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[1:])

