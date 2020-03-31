#!/usr/bin/env python3

import sys
import argparse
import re
import os
import gzip
from os.path import join, basename, dirname, abspath, splitext
from snptk.util import debug

sys.path.append('../snptk')

def parse_grch38_dbsnp(fname):

    db ={}

    with gzip.open(fname, 'rt') as f:
        for line in f:
            fields = line.strip().split()
            rsid, chromosome, strand = fields[0], fields[1], fields[3]

            db[rsid] = (chromosome, strand)

    return db

def map_chromosomes(grch37, grch38_db, outfile):

    with gzip.open(outfile + '.gz', 'wt') as out:
        with gzip.open(grch37, 'rt') as f:
            for line in f:
                fields = line.strip().split()
                rsid, chromosome, position = fields[:]

                rsid = rsid[2:]

                if rsid in grch38_db:
                    chromosome = grch38_db[rsid][0]
                    strand = grch38_db[rsid][1]
                else:
                    debug(f'{rsid} was not found in GRCh38, therefore no change in chromosome')
                    continue

                print(rsid + " " + chromosome + " " + position + " " + strand, file=out)

def main(argv):

    parser = argparse.ArgumentParser(description='Parses GRCh38 json bz2 files and converts to flat gzipped file')

    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('--grch38_dbsnp')
    parser.add_argument('--grch37_dbsnp')
    parser.add_argument('--outfile')

    args = parser.parse_args(argv)

    grch38_db = parse_grch38_dbsnp(args.grch38_dbsnp)

    map_chromosomes(args.grch37_dbsnp, grch38_db, args.outfile)

if __name__ == '__main__':
    main(sys.argv[1:])


