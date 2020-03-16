#!/usr/bin/env python3

import json
import sys
import argparse
import re
import os
import gzip
from os.path import join, basename, dirname, abspath, splitext
from concurrent.futures import ProcessPoolExecutor
from pprint import pprint

sys.path.append('../snptk')

import snptk.util
from snptk.util import debug

def process(fname, outfile):

    base = basename(fname)
    file_number = splitext(base)[0]

    db = {}

    debug(f'Began parsing Rsmerge-{file_number} file')
    with gzip.open(fname, "rb") as f2:
        for line in f2:
            d = json.loads(line.decode('utf-8'))
            if len(d['merged_snapshot_data']['merged_into']) > 0:
                snpid = d['refsnp_id']
                merged_snpid = d['merged_snapshot_data']['merged_into'][0]
                db[snpid] = merged_snpid
            else:
                snpid = d['refsnp_id']
                debug(f'rs{snpid} in file {file_number} has no merge info!')

    debug(f'Finished parsing Rsmerge-{file_number} file')

    return db

def parse(input_dir, fnames, outfile):

    result = {}
    jobs = []

    # truncates file or creates it if it doesn't exist
    open(outfile+'.gz', 'w').close()

    with ProcessPoolExecutor(len(fnames)) as p:
        for fname in fnames:
            fname = join(input_dir, fname)
            jobs.append(p.submit(process, fname, outfile))
        for job in jobs:
            result.update(job.result())

    with gzip.open(outfile + '.gz', 'at') as out:
        for snpid, merged_snpid in result.items():
            print(snpid + " " + merged_snpid, file=out)

def main(argv):
    parser = argparse.ArgumentParser(description='Parses Rsmerge json bz2 file and converts to flat file')

    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('--input_dir')
    parser.add_argument('--output_file')

    if len(argv) < 3:
        parser.print_help(sys.stderr)
        sys.exit()

    args = parser.parse_args(argv)

    files = [i for i in os.listdir(args.input_dir)]
    parse(args.input_dir, files, args.output_file)

if __name__ == '__main__':
    main(sys.argv[1:])

