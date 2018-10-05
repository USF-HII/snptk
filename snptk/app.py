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

    snp_history = snptk.core.execute_load(snptk.core.load_snp_history, snp_history_fname, merge_method='set')
    rs_merge = snptk.core.execute_load(snptk.core.load_rs_merge, rs_merge_fname, merge_method='update')

    #-----------------------------------------------------------------------------------
    # Build a list of tuples with the original snp_id and updated_snp_id
    #-----------------------------------------------------------------------------------
    snp_map = []

    for entry in snptk.core.load_bim(bim_fname):
        snp_id_new = snptk.core.update_snp_id(snp_id, snp_history, rs_merge)
        snp_map.add((snp_id, snp_id_new))

    #-----------------------------------------------------------------------------------
    # Load dbsnp by snp_id
    #-----------------------------------------------------------------------------------
    dbsnp = snptk.core.execute_load(
            snptk.core.load_dbsnp_by_snp_id,
            dbsnp_fname,
            set([snp for pair in snp_map for snp in pair]),
            merge_method='update')

    #-----------------------------------------------------------------------------------
    # Generate edit instructions
    #-----------------------------------------------------------------------------------
    coords_to_update = []
    snps_to_delete = []
    snps_to_update = []

    for snp_id, snp_id_new in snp_map:
        if snp_id_new:
            if snp_id_new != snp_id:

                if snp_id_new in [snp[0] for snp_map]:
                    snps_to_delete.add(snp_id)
                else:
                    snps_to_update.add((snp_id, snp_id_new))
                    coords_to_update.add((snp_id_new, dbsnp[snp_id_new]))
            else:
                if snp_id not in dbsnp:
                    coords_to_update.add((snp_id, dbsnp[snp_id]))

        else:
           snps_to_delete.add(snp_id)

    # last thoughts
    #   handle snp_id that are not in dbsnp (ignore)


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
