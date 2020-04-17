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

    debug(f'Began parsing GRCh38')

    db ={}

    with gzip.open(fname, 'rt') as f:
        for line in f:
            fields = line.strip().split()
            rsid, chromosome, strand = fields[0], fields[1], fields[3]

            db[rsid] = (chromosome, strand)

    debug(f'Finishing parsing GRCh38')

    return db

def map_chromosomes(grch37, grch38_db):

    debug(f'Began mapping GRCh37 chromosomes')

    db = {}
    multi_entries = set()

    with gzip.open(grch37, 'rt') as f:
        for line in f:
            fields = line.strip().split()
            rsid, chromosome, position = fields[:]

            if not chromosome.startswith("NC"):
                continue

            rsid = rsid[2:]

            if rsid in db:
                multi_entries.add(rsid)
                continue

            if rsid in grch38_db:
                chromosome = grch38_db[rsid][0]
                strand = grch38_db[rsid][1]
            else:
                debug(f'{rsid} was not found in GRCh38, therefore no change in chromosome', level=2)
                continue

            db[rsid] = chromosome + " " + position + " " + strand

    # remove any multi snps
    for rsid in multi_entries:
        del db[rsid]

    debug(f'Finished mapping GRCh37 chromosomes')

    return db, multi_entries

def output(db, multi_entries, outfile):

    with gzip.open(outfile + '_multi_entries.gz', 'wt') as out:
        for rsid in multi_entries:
            print(rsid, file=out)

    with gzip.open(outfile + '.gz', 'wt') as out:
        for rsid, value in db.items():
            print(rsid + " " + value, file=out)

def main(argv):

    parser = argparse.ArgumentParser(description='Maps GRCh37 chromosomes to GRCh38 to set correct chromosome')

    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('--grch38_dbsnp')
    parser.add_argument('--grch37_dbsnp')
    parser.add_argument('--outfile')

    args = parser.parse_args(argv)

    grch38_db = parse_grch38_dbsnp(args.grch38_dbsnp)

    grch37_db, multi_entries = map_chromosomes(args.grch37_dbsnp, grch38_db)

    output(grch37_db, multi_entries, args.outfile)

if __name__ == '__main__':
    main(sys.argv[1:])


