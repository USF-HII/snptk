import os
import sys

from concurrent.futures import ProcessPoolExecutor

import snptk.core
import snptk.util

def update_snpid_and_position(args):
    bim_fname = args['bim']
    dbsnp_fname = args['dbsnp']
    snp_history_fname = args['snp_history']
    rs_merge_fname = args['rs_merge']

    snp_ids = set()

    bim_entries = snptk.core.load_bim(bim_fname)
    snp_history = snptk.core.execute_load(snptk.core.load_snp_history, snp_history_fname, merge_method='set')
    rs_merge = snptk.core.execute_load(snptk.core.load_rs_merge, rs_merge_fname, merge_method='update')

    for entry in bim_entries:
        snp_ids.add(entry['snp_id'])

    updated_snp_ids = set(snp_ids)
    for snp_id in snp_ids:
        updated_snp_id = snptk.core.update_snp_id(snp_id, snp_history, rs_merge)

        if updated_snp_id == 'deleted':
            updated_snp_ids.remove(snp_id)
        elif updated_snp_id == 'unchanged':
            continue
        else:
            updated_snp_ids.add(updated_snp_id)

    print ('SNP ids removed: ')
    print(updated_snp_ids.difference(snp_ids))

    db = snptk.core.execute_load(snptk.core.load_dbsnp_by_snp_id, dbsnp_fname, updated_snp_ids, merge_method='update')

    #update snp id and position



def snpid_from_coord(args):
    snptk.util.debug(f'snpid_from_coord: {args}', 1)

    bim_fname = args['bim']
    dbsnp_fname = args['dbsnp']

    coordinates = set()

    bim_entries = snptk.core.load_bim(bim_fname)

    for entry in bim_entries:
        coordinates.add(entry['chromosome'] + ':' + entry['position'])

    db = snptk.core.execute_load(snptk.core.load_dbsnp_by_coordinate, dbsnp_fname, coordinates, merge_method='extend')

    for entry in bim_entries:
        k = entry['chromosome'] + ':' + entry['position']

        if k in db:
            if len(db[k]) > 1:
                snptk.util.debug(f'Has more than one snp_id db[{k}] = {str(db[k])}')
            else:
                if db[k][0] != entry['snp_id']:
                    snptk.util.debug(f'Rewrote snp_id {entry["snp_id"]} to {db[k][0]} for position {k}')
                    entry['snp_id'] = db[k][0]

        else:
            snptk.util.debug('NO_MATCH: ' + '\t'.join(entry.values()))

        print('\t'.join(entry.values()))
