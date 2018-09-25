import os

from concurrent.futures import ProcessPoolExecutor

import snptk.core
import snptk.util

def snpid_from_coord(args):
    snptk.util.debug(f'snpid_from_coord: {args}', 1)

    bim_fname = args['bim']
    dbsnp_fname = args['dbsnp']

    coordinates = set()

    bim_entries = snptk.core.load_bim(bim_fname)

    for entry in bim_entries:
        coordinates.add(entry['chromosome'] + ':' + entry['position'])

    db = {}

    if os.path.isdir(dbsnp_fname):
        jobs = []
        dbsnp_fnames = [os.path.join(dbsnp_fname, f) for f in os.listdir(dbsnp_fname)]

        with ProcessPoolExecutor(len(dbsnp_fnames)) as p:
            for fname in dbsnp_fnames:
                jobs.append(p.submit(snptk.core.load_dbsnp_by_coordinate, fname, coordinates))

        for job in jobs:
            for k, v in job.result().items():
                db.setdefault(k, []).extend(v)
    else:
        db = snptk.core.load_dbsnp_by_coordinate(dbsnp_fname, coordinates)

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
