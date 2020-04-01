#!/usr/bin/env python3

import gzip
import sys
import os

from concurrent.futures import ProcessPoolExecutor

from snptk.util import debug

def execute_load(load_func, fname, *args, merge_method='update'):
    """
    Accepts a load_* function pointer, fname, and arguments and executes using a ProcessPoolExecutor()
    if the fname is a directory, otherwise call the function_pointer directly.

    The result will be either a dictionary with strings as keys or a list.
    The code performs a simple merge of strings but uses extend to merge lists.
    """

    if merge_method == 'set':
        result = set()
    else:
        result = {}

    if os.path.isdir(fname):
        jobs = []
        fnames = [os.path.join(fname, f) for f in os.listdir(fname)]

        with ProcessPoolExecutor(len(fnames)) as p:
            for fname in fnames:
                if args:
                    jobs.append(p.submit(load_func, fname, *args))
                else:
                    jobs.append(p.submit(load_func, fname))

            for job in jobs:
                if merge_method == 'update' or merge_method == 'set':
                    result.update(job.result())

                elif merge_method == 'extend':
                    for k, v in job.result().items():
                        result.setdefault(k, []).extend(v)
                else:
                    raise ValueError(f'Unknown merge method "{merge_method}"')

    else:
        if args:
            result = load_func(fname, *args)
        else:
            result = load_func(fname)

    return result


def update_snp_id(snp_id, rs_merge):
    """
    Pass SNP Id and using RsMerge return the merged SNP Id or the same if unchanged  if the SNP has been removed by NCBI.

    Old RSMerge logic from UM example script: https://genome.sph.umich.edu/wiki/LiftRsNumber.py
    """

    if snp_id.startswith('rs'):
        snp_id = snp_id[2:]

    if not snp_id.isdigit():
        return snp_id

    # snp has no merge history
    if snp_id not in rs_merge:
        return 'rs' + snp_id

    while snp_id in rs_merge:
        snp_id = rs_merge[snp_id]

    return 'rs' + snp_id

def load_rs_merge(fname):

    rs_merge = {}

    debug(f"Loading rs merge file '{fname}'...")

    with gzip.open(fname, 'rt', encoding='utf-8') as f:
        for line in f:
            fields = line.strip().split()
            rsid, merged_rsid = fields[0], fields[1]
            rs_merge[rsid] = merged_rsid

    debug(f"Complete loading rs merge file '{fname}'...")

    return rs_merge

def load_bim(fname, offset=0):
    """
    Read in file with Plink BIM format (https://www.cog-genomics.org/plink2/formats#bim) and return labeled entries as a list.
    """

    entries = []

    with open(fname) as f:
        for line in f:
            fields = line.strip().split()

            if len(fields) != 6:
                print(f'Invalid BIM format - len(fields)={len(fields)} but expected 6 fields={fields}', file=sys.stderr)
                sys.exit(1)

            entries.append({
                'chromosome': fields[0],
                'snp_id': fields[1],
                'distance': fields[2],
                'position': str(int(fields[3]) + offset),
                'allele_1': fields[4],
                'allele_2': fields[5]})

    return entries

def load_dbsnp_by_snp_id(fname, snp_ids, offset=0):
    """
    Read in NCBI dbSNP and return subset of entries keyed by SNP Id. E.g.:

        db = {'rs123': '1:1900500',
              'rs456': '2:3434343'}'
    """

    db = {}

    plink_map = {str(n):str(n) for n in range(1, 23)}
    plink_map.update({'X': '23', 'Y': '24', 'PAR': '25', 'M': '26', 'MT': '26'})

    debug(f"Loading dbSNP file '{fname}'...")

    with gzip.open(fname, 'rt', encoding='utf-8') as f:
        for line in f:
            fields = line.strip().split()

            fields_len = len(fields)

            # do we need this? YES
            if fields_len < 3 or fields[2] == '':
                continue

            snp_id = 'rs' + fields[0]

            # add back in Alt Only if statement
            if snp_id in snp_ids:
                chromosome = plink_map[fields[1]]
                position = str(int(fields[2]) + offset)
                db[snp_id] = chromosome + ':' + position

    debug(f"Completed loading dbSNP file '{fname}'...")

    return db

def load_dbsnp_by_coordinate(fname, coordinates, offset=0):
    """
    Read in NCBI dbSNP and return subset of entries keyed by coordinate. E.g.:

        db = {'1:1900500': ['rs123'],
              '3:2900500': ['rs456', 'rs789'], ...}
    """

    db = {}

    plink_map = {str(n):str(n) for n in range(1, 23)}
    plink_map.update({'X': '23', 'Y': '24', 'PAR': '25', 'M': '26', 'MT': '26'})

    debug(f"Loading dbSNP file '{fname}'...")

    with gzip.open(fname, 'rt', encoding='utf-8') as f:
        for line in f:
            fields = line.strip().split()

            fields_len = len(fields)

            if fields_len < 3 or fields[2] == '':
                continue

            snp_id = 'rs' + fields[0]
            chromosome = plink_map[fields[1]]
            position = str(int(fields[2]) + offset)

            k = chromosome + ':' + position

            if k in coordinates:
                if fields_len >= 4:
                    db.setdefault(k, []).append(snp_id)
                else:
                    if fields[1] == 'AltOnly':
                        db[k] = ['AltOnly']
                    else:
                        debug('len(fields) < 4 and not AltOnly: ' + str(fields))

    return db

