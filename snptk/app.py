import os
import sys

from concurrent.futures import ProcessPoolExecutor

import snptk.core
import snptk.util

# [ (snpid, update_snpid),
#   (snpid, update_snpid),
# ]

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

    update_look_up = {}
    deleted_snp_ids = []
    updated_snp_ids = set(snp_ids)
    for snp_id in snp_ids:
        updated_snp_id = snptk.core.update_snp_id(snp_id, snp_history, rs_merge)

        if updated_snp_id == 'deleted':
            updated_snp_ids.remove(snp_id)
            snptk.util.debug(f'SNP id deleted {snp_id}')
            deleted_snp_ids.append(snp_id)
        elif updated_snp_id == 'unchanged':
            continue
        else:
            snptk.util.debug(f'SNP id was {snp_id}, Now is {updated_snp_id}')
            update_look_up[snp_id] = updated_snp_id
            updated_snp_ids.add(updated_snp_id)

    db = snptk.core.execute_load(snptk.core.load_dbsnp_by_snp_id, dbsnp_fname, updated_snp_ids, merge_method='update')

    counter = 0
    deleted_count = 0
    update_id = 0
    #update snp id and position
    updated_bim_entries = []
    for entry in bim_entries:
        snp_id = entry['snp_id']
        chromosome = entry['chromosome']
        position = entry['position']

        if snp_id in deleted_snp_ids:
            #updated_bim_entries.remove(entry)
            deleted_count +=1
            continue

        if snp_id in update_look_up:
            snp_id = update_look_up[snp_id]
            entry['snp_id'] = snp_id
            update_id +=1

        if snp_id in db:
            k = chromosome + ':' + position
            counter += 1
            if db[snp_id] != k:
                temp = k.split(':')
                entry['chromosome'] = temp[0]
                entry['position'] = temp [1]
            else:
                print('unchanged?!?!?')
        else:
            #AA_DQB1_-21_32742328_x
            #SNP_DQB1_32742328_T
            #SNP_DQB1_32742328_C
            pass

        updated_bim_entries.append(entry)

    print ('')
    print ('Deleted snps: ' + str(deleted_count))
    print ('Updated snps: ' + str(update_id))
    print ('Number of snps found in hg19 db: ' + str(counter))
    print ('Orignial Bim file size: ' + str(len(bim_entries)))
    print ('Updated Bim file size: ' + str(len(updated_bim_entries)))
    print ('')

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
