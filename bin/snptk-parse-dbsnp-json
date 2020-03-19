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


def process_pool(fname):

    db = {}

    chromosome = re.search('chr(.*).json', fname).group(1)

    debug(f'Began parsing chr{chromosome} dbsnp file')
    with bz2.open(fname, "rb") as f2:
        for line in f2:
            d = json.loads(line.decode('utf-8'))
            snpid = d['refsnp_id']

            if d['present_obs_movements']:
                position = str(d['present_obs_movements'][0]['allele_in_cur_release']['position'])
            else:
                debug(f'rs{snpid} on chr{chromosome} does not have a position available')
                continue

            db[snpid] = chromosome + " " + position

        debug(f'Finished parsing chr{chromosome} dbsnp file')

    return db

def pool_parse(fnames, outfile):

    with Pool(len(fnames)) as pool:
        with gzip.open(outfile + '.gz', 'at') as out:
            for result in pool.map(process_pool, fnames):
                for snpid, chr_position in result.items():
                    print(snpid + " " + chr_position, file=out)

def main(argv):

    parser = argparse.ArgumentParser(description='Parses GRCh38 json bz2 files and converts to flat gzipped file')

    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('--outfile')
    parser.add_argument('filenames', nargs='*')

    args = parser.parse_args(argv)

    pool_parse(args.filenames, args.outfile)

if __name__ == '__main__':
    main(sys.argv[1:])

