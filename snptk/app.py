from os.path import join, basename, splitext

import subprocess
import snptk.core
import snptk.util

from snptk.util import debug

#-----------------------------------------------------------------------------------
# map_using_rs_id
#-----------------------------------------------------------------------------------

def map_using_rs_id(args):
    bim_fname = args['bim']
    dbsnp_fname = args['dbsnp']
    rs_merge_fname = args['rs_merge']
    bim_offset = args['bim_offset']
    output_prefix = args['output_prefix']

    rs_merge = snptk.core.execute_load(snptk.core.load_rs_merge, rs_merge_fname, merge_method='update')

    #-----------------------------------------------------------------------------------
    # Build a list of tuples with the original snp_id and updated_snp_id
    #-----------------------------------------------------------------------------------
    snp_map = []

    for entry in snptk.core.load_bim(bim_fname, offset=bim_offset):
        snp_id = entry['snp_id']
        snp_id_new = snptk.core.update_snp_id(snp_id, rs_merge)
        snp_map.append((snp_id, entry['chromosome'] + ':' + entry['position'], snp_id_new))

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

    snps_to_delete, snps_to_update, coords_to_update, chromosomes_to_update = map_using_rs_id_logic(snp_map, dbsnp)

    with open(join(output_prefix, 'deleted_snps.txt'), 'w') as f:
        for snp_id in snps_to_delete:
            print(snp_id, file=f)

    with open(join(output_prefix, 'updated_snps.txt'), 'w') as f:
        for snp_id, snp_id_new in snps_to_update:
            print(snp_id + '\t' + snp_id_new, file=f)

    with open(join(output_prefix, 'coord_update.txt'), 'w') as f:
        for snp_id, coord_new in coords_to_update:
            print(snp_id + '\t' + coord_new, file=f)

    with open(join(output_prefix, 'chr_update.txt'), 'w') as f:
        for snp_id, chromosome in chromosomes_to_update:
            print(snp_id + '\t' + chromosome, file=f)

def map_using_rs_id_logic(snp_map, dbsnp):

    snps_to_delete = []
    snps_to_update = []
    coords_to_update = []
    chromosomes_to_update = []

    for snp_id, original_coord, snp_id_new in snp_map:

        # If the snp has been updated (merged)
        if snp_id_new != snp_id:

            # If the merged snp was already in the original
            if snp_id_new in [snp[0] for snp in snp_map]:
                snps_to_delete.append(snp_id)

            elif snp_id_new in dbsnp:
                snps_to_update.append((snp_id, snp_id_new))
                debug(f'original_coord={original_coord} updated_coord={dbsnp[snp_id_new]}', level=2)

                new_chromosome, new_position = dbsnp[snp_id_new].split(':')
                original_chromosome, original_position = original_coord.split(':')

                if new_position != original_position:
                    coords_to_update.append((snp_id_new, new_position))

                if new_chromosome != original_chromosome:
                    chromosomes_to_update.append((snp_id_new, new_chromosome))

            else:
                snps_to_delete.append(snp_id)

        # if snp_id wasn't merged and is the same as snp_id_new (no change)
        else:
            if snp_id in dbsnp:
                debug(f'original_coord={original_coord} updated_coord={dbsnp[snp_id]}', level=2)

                new_chromosome, new_position = dbsnp[snp_id].split(':')
                original_chromosome, original_position = original_coord.split(':')

                if new_position != original_position:
                    coords_to_update.append((snp_id, new_position))

                if new_chromosome != original_chromosome:
                    chromosomes_to_update.append((snp_id, new_chromosome))

            # if the snp isn't in dbsnp it has been deleted
            else:
                snps_to_delete.append(snp_id)

    return snps_to_delete, snps_to_update, coords_to_update, chromosomes_to_update

#-----------------------------------------------------------------------------------
# map_using_coord
#-----------------------------------------------------------------------------------

def map_using_coord(args):

    bim_fname = args['bim']
    bim_offset = args['bim_offset']
    dbsnp_fname = args['dbsnp']
    output_prefix = args['output_prefix']

    keep_multi = args['keep_multi_snp_mappings']
    keep_unmapped_rsids = args['keep_unmapped_rsids']
    skip_rs_ids = args['skip_rs_ids']

    coordinates = set()
    snps = set()

    bim_entries = snptk.core.load_bim(bim_fname, offset=bim_offset)

    for entry in bim_entries:
        snps.add(entry['snp_id'])
        coordinates.add(entry['chromosome'] + ':' + entry['position'])

    dbsnp = snptk.core.execute_load(snptk.core.load_dbsnp_by_coordinate, dbsnp_fname, coordinates, merge_method='extend')

    snps_to_delete, snps_to_update, multi_snps = map_using_coord_logic(bim_entries, snps, dbsnp, keep_multi, keep_unmapped_rsids, skip_rs_ids)

    with open(join(output_prefix, 'deleted_snps.txt'), 'w') as f:
        for snp_id in snps_to_delete:
            print(snp_id, file=f)

    with open(join(output_prefix, 'updated_snps.txt'), 'w') as f:
        for snp_id, snp_id_new in snps_to_update:
            print(snp_id + '\t' + snp_id_new, file=f)

    if len(multi_snps) > 0:
        with open(join(output_prefix, 'multi_snp_mappings.txt'), 'w') as f:
            for chr_pos, mappings in multi_snps:
                print(chr_pos + '\t'+ ','.join(mappings), file=f)

def map_using_coord_logic(bim_entries, snps, dbsnp, keep_multi=False, keep_unmapped_rsids=False, skip_rs_ids=False):

    snps_to_update = []
    snps_to_delete = []
    multi_snps = []

    for entry in bim_entries:
        k = entry['chromosome'] + ':' + entry['position']
        snp = entry['snp_id']

        if snp.startswith("rs") and skip_rs_ids:
            continue

        if k in dbsnp:
            if len(dbsnp[k]) > 1:
                debug(f'Has more than one snp_id dbsnp[{k}] = {str(dbsnp[k])}')
                if keep_multi:
                    multi_snps.append((k, dbsnp[k]))

                    # this prevents rs123 being updated to rs123 (No change)
                    # this also checks to see if snp already in bim so duplicate
                    # snps aren't included twice
                    if dbsnp[k][0] != snp and dbsnp[k][0] not in snps:
                        snps_to_update.append((snp, dbsnp[k][0]))
                    else:
                        continue
                else:
                    if keep_unmapped_rsids and snp.startswith('rs'):
                        continue
                    snps_to_delete.append(snp)
            else:
                if dbsnp[k][0] != snp:
                    debug(f'Rewrote snp_id {snp} to {dbsnp[k][0]} for position {k}')
                    snps_to_update.append((snp, dbsnp[k][0]))
                    snp = dbsnp[k][0]

        else:
            if keep_unmapped_rsids and snp.startswith('rs'):
                continue
            debug('NO_MATCH: ' + '\t'.join(entry.values()))
            snps_to_delete.append(snp)

    return snps_to_delete, snps_to_update, multi_snps

#-----------------------------------------------------------------------------------
# Remove Duplicates
#-----------------------------------------------------------------------------------

def remove_duplicates(args):

    plink_fname = args['plink_prefix']
    output_prefix = args['output_prefix']

    file_name=splitext(basename(plink_fname))[0]

    # convert to vcf
    command = f'plink --bfile {plink_fname} --recode vcf --out {output_prefix}/{file_name}'
    subprocess.call(command, shell=True)
    print("Finished converting to VCF")

    # remove dups using bcftools
    command = f'bcftools norm --rm-dup all -o {output_prefix}/{file_name}_no_dups.vcf -O vcf {output_prefix}/{file_name}.vcf'
    subprocess.call(command, shell=True)
    print("Finished removing duplicate snps using Bcftools")

    # convert to vcf to plink
    command = f'plink --vcf {output_prefix}/{file_name}_no_dups.vcf --const-fid --make-bed --out {output_prefix}/{file_name}_no_dups'
    subprocess.call(command, shell=True)
    print("Finished converting VCF back to Plink")

    # set fam IDs back to original
    command = f'cut -d" " -f1-2 {output_prefix}/{file_name}_no_dups.fam > {output_prefix}/new_fam_ids.txt'
    command2 = f'cut -d" " -f1-2 {plink_fname}.fam > {output_prefix}/ori_fam_ids.txt'
    command3 = f'paste -d" " {output_prefix}/new_fam_ids.txt {output_prefix}/ori_fam_ids.txt > {output_prefix}/update_fam_ids.txt'

    subprocess.call(command, shell=True)
    subprocess.call(command2, shell=True)
    subprocess.call(command3, shell=True)

    command = f'plink --bfile {output_prefix}/{file_name}_no_dups --update-ids {output_prefix}/update_fam_ids.txt --make-bed --out {output_prefix}/{file_name}_no_dups_final'
    subprocess.call(command, shell=True)
    print("Finished fixing Fam IDs")
    print("***** COMPLETE ******")

#-----------------------------------------------------------------------------------
# snpid_from_coord_update
#-----------------------------------------------------------------------------------

def snpid_from_coord_update(args):

    plink_fname = args['plink_prefix']
    update_fname = args['update_file']
    delete_fname = args['delete_file']
    out_name = args['out_name']
    output_prefix = args['output_prefix']

    file_name=splitext(basename(plink_fname))[0]

    # exclude deleted snps
    command = f'plink --bfile {plink_fname} --exclude {delete_fname} --make-bed --out {output_prefix}/{file_name}_deleted'
    subprocess.call(command, shell=True)
    print("Finished removing Deleted SNPs")

    # exclude deleted snps
    command = f'plink --bfile {output_prefix}/{file_name}_deleted --update-name {update_fname} --make-bed --out {output_prefix}/{out_name}'
    subprocess.call(command, shell=True)
    print("Finished Updating SNPs")
    print("***** COMPLETE ******")

#-----------------------------------------------------------------------------------
# snpid_and_position_update
#-----------------------------------------------------------------------------------

def snpid_and_position_update(args):

    plink_fname = args['plink_prefix']
    update_fname = args['update_file']
    delete_fname = args['delete_file']
    coord_fname = args['coord_file']
    chr_fname = args['chr_file']
    out_name = args['out_name']
    output_prefix = args['output_prefix']

    file_name=splitext(basename(plink_fname))[0]

    # exclude deleted snps
    command = f'plink --bfile {plink_fname} --exclude {delete_fname} --make-bed --out {output_prefix}/{file_name}_deleted'
    subprocess.call(command, shell=True)
    print("Finished removing Deleted SNPs")

    # update snps
    command = f'plink --bfile {output_prefix}/{file_name}_deleted --update-name {update_fname} --make-bed --out {output_prefix}/{file_name}_updated'
    subprocess.call(command, shell=True)
    print("Finished Updating SNPs")

    # update coordniates
    command = f'plink --bfile {output_prefix}/{file_name}_updated --update-map {coord_fname} --make-bed --out {output_prefix}/{file_name}_coord_update'
    subprocess.call(command, shell=True)
    print("Finished Updating Coordniates")

    # update chromosomes
    command = f'plink --bfile {output_prefix}/{file_name}_coord_update --update-chr {chr_fname} --make-bed --out {output_prefix}/{out_name}'
    subprocess.call(command, shell=True)
    print("Finished Updating Chromosomes")
    print("***** COMPLETE ******")
