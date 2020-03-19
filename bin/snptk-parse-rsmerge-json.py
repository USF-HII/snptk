#!/usr/bin/env python3

import os
import sys
import argparse
import gzip
import bz2
import json
from snptk.util import debug
from os.path import join, basename, dirname, abspath, splitext

sys.path.append('../snptk')

def process(fname, outfile):

    db = {}

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
    parser = argparse.ArgumentParser(description='Parses Rsmerge json bz2 file and converts to flat gzipped file')

    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('--input_file')
    parser.add_argument('--outfile')

    if len(argv) < 3:
        parser.print_help(sys.stderr)
        sys.exit()

    args = parser.parse_args(argv)

    process(args.input_file, args.outfile)

if __name__ == '__main__':
    main(sys.argv[1:])

