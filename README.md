# snptk

Helps analyze,translate SNP entries from NCBI dbSNP and others.

## Usage

    snptk <sub_command> [options...]

### snpid-from-coord

Updates the SNP Id column in a Plink [BIM](https://www.cog-genomics.org/plink2/formats#bim) formatted file
and outputs to `STDOUT`.

     snptk snpid-from-coord [--bim-offset=<n>] --dbsnp=tmp/data/grch38p7/dbsnp.d/ tests/data/example.bim
     
Use `--keep-multi-snp-mappings` option to keep multi snp mappings and not delete them.

### update-snpid-and-position

     snptk update-snpid-and-position [--bim-offset=<n>]...

This will generate 4  plink edit files as:
- `<prefix>/deleted.txt`
- `<prefix>/updated_snps.txt`
- `<prefix>/coord_update.txt`
- `<prefix>/chr_update.txt`

These files are then used by plink against the original `bim`, e.g.:

    plink \
      [--keep-allele-order] \
      --bfile <bim> \
      --exclude <prefix>/deleted_snps.txt \
      --make-bed \
      --out <output_bim_1>

    plink \
      [--keep-allele-order] \
      --bfile <output_bim_1> \
      --update-name <prefix>/updated_snps.txt \
      --make-bed \
      --out <output_bim_2>

    plink \
      [--keep-allele-order] \
      --bfile <output_bim_2> \
      --update-map <prefix>/coord_update.txt \
      --make-bed \
      --out <output_bim_3>

    plink \
      [--keep-allele-order] \
      --bfile <output_bim_3> \
      --update-chr <prefix>/chr_update.txt \
      --make-bed \
      --out <output_bim_4>
      
### remove_duplicates

Tool to remove duplicate snps inside of plink binary files bim, bed, and fam. Unlike using plink --list-duplicate-vars and --exlude to get rid of all snps that are duplicated, this tool keeps one copy of duplicated snps and removes the rest. This allows retenation of data without unncessary throwing it away.  

If you have plink files: test.bim, test.fam, test.bed 

plink_prefix = {input_dir}/test 

      snptk remove-duplicates --plink_prefix {plink_prefix} -o {output_dir}

##### Output 

      {output_dir}/test_no_dups_final.{bim,fam,bed}

### snpid_from_coord_update 

Uses snptk snpid_from_coord output to update plink files 

      snptk snpid-from-coord-update \
            --plink_prefix {plink_prefix} \ 
            --update_file {path_to_update_file} \
            --delete_file {path_to_delete_file} \
            --out_name {name_of_final_file} \
            -o {output_dir}
 
 ##### Output 

      {output_dir}/{out_name}.{bim,fam,bed}

### snpid_and_position_update 

Uses snptk snpid_and_position output to update plink files 

      snptk snpid-and-position-update \
            --plink_prefix {plink_prefix} \
            --update_file {path_to_update_file} \
            --delete_file {path_to_delete_file} \
            --coord_file {path_to_file} \
            --chr_file {path_to_file} \
            --out_name {name_of_final_file} \
            -o {output_dir}
##### Output 

      {output_dir}/{out_name}.{bim,fam,bed}

## Preprocessing of NCBI SNP data

NCBI changed their dbsnp data format beginning with build 152. The new data format is in json formatting. Due to this, preprocessing is required to make dbsnp json files compatiable with snptk. NCBI dbsnp json files can be found here:
https://ftp.ncbi.nih.gov/snp/archive/

### Processing GRCh38 dbsnp JSON data

We have provided a script inside of bin called snptk-parse-json.py. GRCh38 json data can be found at https://ftp.ncbi.nih.gov/snp/archive/b153/JSON/

Usage of snptk-parse-json to process snp data: 

       python3 snptk-parse-json.py --method dbsnp --outfile refsnp-chr1 refsnp-chr1.json.bz2

Usage of snptk-parse-json to process rsmerge data:

       python3 snptk-parse-json.py --method rsmerge --outfile Rsmerge refsnp-merged.json.bz2

**Note:** Once all chromosomes have been processed, files need to be concatenated into one gzip file. This can be easily done with cat. 

       cat chr1.gz {chr2, chr3,... chrMT}.gz > dbsnp-GRCh38.gz

### Processing GRCh37 dbsnp VCF data

GRCh37 is a little different than GRCh38 as NCBI does not provide json formatted files. Instead a GRCh37 VCF file is provided and located at https://ftp.ncbi.nih.gov/snp/archive/b153/VCF/GCF_000001405.25.gz. To process this file, we have provided a script inside of bin called snptk-parse-dbsnp-vcf which requires bcftools http://samtools.github.io/bcftools/
to use. 

Usage of snptk-parse-dbsnp-vcf:

       snptk-parse-dbsnp-vcf <input_vcf> <output_file> 

Althought snptk-parse-dbsnp-vcf uses bcftools to extract snp information, the output does not contain correct chromosome assignmnets. In order to fix this issue, we need to map snp IDs to GRCh38 to assign correct chromosome value. To do this, we have a provided a script inside of bin called snptk-map-grch37-chromosomes.py to use. 

Usage of snptk-map-grch37-chromosomes.py:

       python3 snptk-map-grch37-chromosomes.py --grch37_dbsnp grch37.gz --grch38_dbsnp grch38.gz <outfile>

## Concurrency

Since the reference files `snptk` deals with are rather large in number of records we have included a split utility to read the original file and split it into chunks within a directory.

If the input file is a directory as opposed to a file, the utility will use `concurrent.futures.ProcessPoolExecutor()` to parse all of the files in the directory to increase speed. It will use as many processes as there are files in the directory - currently 32 is a good guideline (the most expected on any node).

The recommended directory structure for a split file is `<file_path>.d/01`, `<file_path>.d/02`, etc.

For example:

    snptk-split \
      /shares/hii/bioinfo/ref/ncbi/human_9606_b151_GRCh38p7/b151_SNPChrPosOnRef_108.bcp.gz \
      tmp/data/grch38p7/dbsnp.d/ \
      32


