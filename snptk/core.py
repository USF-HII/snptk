#!/usr/bin/env python3

import gzip
import sys
import os

from concurrent.futures import ProcessPoolExecutor

import snptk.util

def update_snp_id(snp_id, snp_history, rs_merge):
    """
    Pass SNP Id and using RsMerge and SNPHistory return the merged SNP Id, the same if unchanged
    or None if the SNP has been removed by NCBI.
    RSMerge logic from UM example script: https://genome.sph.umich.edu/wiki/LiftRsNumber.py
    """

    if snp_id.startswith('rs'):
        snp_id = snp_id[2:]

    if snp_id not in rs_merge:
        if snp_id not in snp_history:
            return 'unchanged'
        else:
            return 'deleted'

    while True:
        if snp_id in rs_merge:
            rs_low, rs_current = rs_merge[snp_id]

            if rs_current not in snp_history:
                return 'rs' + rs_current
            else:
                snp_id = rs_low
        else:
            return 'deleted'

    return 0

def load_rs_merge(fname):

    rs_merge = {}

    if os.path.isdir(fname):
        jobs = []
        fnames = [os.path.join(fname, f) for f in os.listdir(fname)]

        with ProcessPoolExecutor(len(fnames)) as p:
            for fname in fnames:
                jobs.append(p.submit(load_rs_merge_exec, fname, rs_merge))

        for job in jobs:
            rs_merge.update(job.result())

    else:
        rs_merge = load_rs_merge_exec(fname, rs_merge)

    return rs_merge

def load_rs_merge_exec(fname, rs_merge):

    snptk.util.debug(f"Loading rs merge file '{fname}'...")

    with gzip.open(fname, 'rt', encoding='utf-8') as f:
        for line in f:
            fields = line.strip().split('\t')
            rs_high, rs_low, rs_current = fields[0], fields[1], fields[6]
            rs_merge[rs_high] = (rs_low, rs_current)

    return rs_merge

def load_snp_history(fname):

    snp_history = set()

    if os.path.isdir(fname):
        jobs = []
        fnames = [os.path.join(fname, f) for f in os.listdir(fname)]

        with ProcessPoolExecutor(len(fnames)) as p:
            for fname in fnames:
                jobs.append(p.submit(load_snp_history_exec, fname, snp_history))

        for job in jobs:
            snp_history.update(job.result())

    else:
        snp_history = load_snp_history_exec(fname, snp_history)

    return snp_history

def load_snp_history_exec(fname, snp_history):

    snptk.util.debug(f"Loading SNP history file '{fname}'...")

    with gzip.open(fname, 'rt', encoding='utf-8') as f:
        for line in f:
            if line.lower().find('re-activ') < 0:
                fields = line.strip().split('\t')
                snp_history.add(fields[0])

    return snp_history

def load_bim(fname):
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
                'position': fields[3],
                'allele_1': fields[4],
                'allele_2': fields[5]})

    return entries

def load_dbsnp_by_snp_id(fname, snp_ids):
    db = {}

    if os.path.isdir(fname):
        jobs = []
        fnames = [os.path.join(fname, f) for f in os.listdir(fname)]

        with ProcessPoolExecutor(len(fnames)) as p:
            for fname in fnames:
                jobs.append(p.submit(load_dbsnp_by_snp_id_exec, fname, snp_ids))

        for job in jobs:
            db.update(job.result())
    else:
        db = load_dbsnp_by_snp_id_exec(fname, snp_ids)

    return db

def load_dbsnp_by_snp_id_exec(fname, snp_ids, offset=1):
    """
    Read in NCBI dbSNP and return subset of entries keyed by SNP Id. E.g.:

        db = {'rs123': '1:1900500',
              'rs456': '2:3434343'}'
    """

    db = {}

    plink_map = {str(n):str(n) for n in range(1, 23)}
    plink_map.update({'X': '23', 'Y': '24', 'PAR': '25', 'M': '26', 'MT': '26'})

    snptk.util.debug(f"Loading dbSNP file '{fname}'...")

    with gzip.open(fname, 'rt', encoding='utf-8') as f:
        for line in f:
            fields = line.strip().split('\t')

            fields_len = len(fields)

            if fields_len < 3 or fields[2] == '':
                continue

            snp_id = 'rs' + fields[0]

            if snp_id in snp_ids:
                if fields[1] == 'AltOnly':
                    db[snp_id] = ['AltOnly']
                else:
                    chromosome = plink_map[fields[1]]
                    position = str(int(fields[2]) + offset)
                    db[snp_id] = chromosome + ':' + position

    return db

def load_dbsnp_by_coordinate(fname, coordinates, offset=1):
    """
    Read in NCBI dbSNP and return subset of entries keyed by coordinate. E.g.:

        db = {'1:1900500': ['rs123'],
              '3:2900500': ['rs456', 'rs789'], ...}
    """

    db = {}

    plink_map = {str(n):str(n) for n in range(1, 23)}
    plink_map.update({'X': '23', 'Y': '24', 'PAR': '25', 'M': '26', 'MT': '26'})

    snptk.util.debug(f"Loading dbSNP file '{fname}'...")

    with gzip.open(fname, 'rt', encoding='utf-8') as f:
        for line in f:
            fields = line.strip().split('\t')

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
                        snptk.util.debug('len(fields) < 4 and not AltOnly: ' + str(fields))

    return db
